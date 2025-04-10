from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
from datetime import datetime
import csv
import sys
import requests
import os

def main():

    update_bina_csv_file()

    check_sold(BINA_CSV_FILE)



#Function to check if there are any new listings on the website that are not present in the database. If so, then add that new listing
#to the CSV Database and also get its photos. Also, this function adds the columns "Days Passed" and "Days listed" in the CSV
def update_bina_csv_file():

    list_rows = load_bina_rows(BINA_CSV_FILE)

    entries = get_bina_entries()
    
    # If the listing already exists on the database and is still present on the website then just create a "Days listed" column
    # in the CSV database which just shows how many days the listing has been up. The moment the listing will no longer be available
    # on the website(which in turn means it will not be in "entries") the Days listed column will stop updating. Later we can compare
    # and see if "Days Passed" == "Days listed". If not that means at some point the listing was taken off the website.
    for row in list_rows:
        for entry in entries:
            if row["Unique ID"] == entry["Unique ID"]:
                row["Days listed"] = get_rows_days_passed(row)
                

    new_rows = []

    for entry in entries:

        for row in list_rows: 
            if row["Unique ID"] == entry["Unique ID"]:
                break
        else:
            #This is if the listing on the website was not found in the database by cross-checking for Unique ID in which case the
            # "Days listed" column is added and then the entire Dict row is added to the new_rows list.
            entry["Days listed"] = get_rows_days_passed(entry)
            new_rows.append(entry)
            get_bina_photos(entry['Unique ID'], entry['Link'])
            
            

    combined_rows = list_rows + new_rows

    #All the rows(the old listings already present in the database and the new listings to be added) will get "Days Passed" updated.
    for row in combined_rows:
        row["Days Passed"] =  get_rows_days_passed(row)

    #Save the new updated database to the file
    save_bina_rows(BINA_CSV_FILE, combined_rows)



#Load the rows from the existing file into memory. If file doesn't exist make new file with the following header fieldnames.
def load_bina_rows(infile):
    try:
        with open(infile, "r") as datafile:
            reader = csv.DictReader(datafile)
            rows = list(reader)
            return rows
    except FileNotFoundError:
        fieldnames = ["Price", "Area", "Price per m2", "Date", "Days listed", "Days Passed", "Street", "Unique ID", "Link"]
        with open(infile, "w", newline="") as datafile:
            writer = csv.DictWriter(datafile, fieldnames=fieldnames)
            writer.writeheader()
        return []


    

#Get all the listings from the website using Selenium and BeautifulSoup to parse 
def get_bina_entries():
    driver = webdriver.Chrome()

    driver.get(arg1)

    element = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "items-i")))

    entries = []

    while True:

        source = driver.page_source

        soup = BeautifulSoup(source, 'lxml')

        #Returns a list of all query elements containing a unique listing in the website
        identifiers = soup.find_all('div', class_='items-i', attrs={'data-item-id': True})
      

        for e in identifiers:

            price = e.find('span', class_ = 'price-val')
            area = e.find('ul', class_ = 'name')
            date = e.find('div', class_ = 'city_when')
            unique = e['data-item-id']
            #Within is to get the listings identifying URL
            within = e.find('a', class_='item_link')['href']
            link_url = 'https://bina.az' + within

            #The original price and area strings are invalid and need to be cleaned
            clean_price = float(price.text.replace(' ', ''))
            clean_area = float(area.li.text.replace('m\u00B2', ''))

            #bugün means today. Must convert into today time
            if "bugün" in date.text:
                clean_date = time.strftime('%d/%m/%Y')
            #Dünən means Yesterday. Must convert into time 
            elif "dünən" in date.text:
                now = time.time()
                yesterday = now - 86400
                yesterday_struct = time.localtime(yesterday)
                yesterday_str = time.strftime("%d/%m/%Y", yesterday_struct)
                clean_date = yesterday_str
            else:
                #Turn month names into their respective number dates
                months = {'yanvar':'01','fevral':'02','mart':'03','aprel':'04','may':'05','iyun':'06','iyul':'07', 'avgust':'08', 'sentyabr':'09', 'oktyabr':'10','noyabr':'11','dekabr':'12'}
                words = date.text.split()
                clean_date = words[1] + '/' + months[words[2]] + '/' + words[3]

            #Finally, append dict row into entries list
            entries.append({"Price" :price.text, "Area" : area.text, "Price per m2" : int(clean_price/clean_area), "Date" : clean_date, 
                            "Unique ID" : unique, "Street": parts[4], "Link": link_url })


        
        #Check if there is next page. If there is, proceed to next page to continue gathering listings.
        if soup.find('span', class_ = 'next') is not None:

            next_page = soup.find('span', class_ = 'next').a['href'] 

            driver.get('https://bina.az/' + next_page)

            element = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "items-i")))
        else:
            break



    return entries



# For every listing get photos which will be stored in a folder which is named the unique ID of that listing which is then 
# stored in a folder which is the street/region to which that listing belongs. The function accepts as parameters the unique ID
# and the specific listings URL
def get_bina_photos(unique, link):
        
        driver = webdriver.Chrome()

        folder_path = f".\\{parts[4]}\\{unique}"
        
        driver.get(link)

        WebDriverWait(driver, 6).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "product-photos__slider-nav-i_picture")))

        source = driver.page_source

        soup = BeautifulSoup(source, 'lxml')

        photo_id = soup.find_all('div', class_='product-photos__slider-nav-i_picture')
        
        for index,photo in enumerate(photo_id):
            #Must clean URL from beautifulsoup
            clean_url = photo['style'].replace("background-image: url('", "").replace("jpg')", "jpg")

            filename = f"{index}.jpg"

            #Create folder path
            os.makedirs(folder_path, exist_ok=True)

            file_path = os.path.join(folder_path, filename)
            
            r = requests.get(clean_url)

            #Final file path where the photo will be saved
            with open(file_path, 'wb') as file:
                file.write(r.content)



#Just a function to save the Dict.
def save_bina_rows(filename, rows):
    fieldnames = ["Price", "Area", "Price per m2", "Date", "Days listed", "Days Passed", "Street", "Unique ID", "Link"]
    with open(filename, mode='w', newline="") as outfile:
        writer = csv.DictWriter(outfile, fieldnames = fieldnames )
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
        



#Get the difference between today and the date at which the listing was posted.
def get_rows_days_passed(row):
    days_passed = (datetime.now() - datetime.strptime(row["Date"], "%d/%m/%Y")).days

    return days_passed




#Read "sold.csv" and get all the unique_ID's (or if it doesn't exist create it). Then take the CSV file with the name of the street/region
#and check for all listings where "Days listed" != "Days Passed". If that listing isn't present within sold.csv then add the listing
#to sold.csv
def check_sold(csv_file):

    #Check sold.csv for unique ID's. If sold.csv doesn't exist, create it.
    try:
        with open("sold.csv", 'r') as rfile:
            reader_sold = csv.DictReader(rfile)
            unique_ids = [row["Unique ID"] for row in reader_sold]
    except FileNotFoundError:
        fieldnames = ["Price", "Area", "Price per m2", "Date", "Days listed", "Days Passed", "Street", "Unique ID", "Link"]
        with open("sold.csv", "w") as datafile:
            writer = csv.DictWriter(datafile, fieldnames=fieldnames)
            writer.writeheader()
            unique_ids = []


    #Open csv file with the name of the street/region and put contents into memory.
    with open(csv_file, 'r') as rfile:
        reader = csv.DictReader(rfile)
        rows = list(reader)
       

        fieldnames = ["Price", "Area", "Price per m2", "Date", "Days listed", "Days Passed", "Street", "Unique ID", "Link"]
        #Check if file already has contents in which case we don't need to rewrite header fieldnames
        with open("sold.csv", 'a+', newline='') as wfile:
            wfile.seek(0)
            empty_file = not wfile.read(1)
            wfile.seek(0,2)

            writer = csv.DictWriter(wfile, fieldnames=fieldnames)
            #If file empty write header fieldnames
            if empty_file:
                writer.writeheader()
            for row in rows:
                # If "Days Passed" != "Days listed" means the listing was delisted at some point. Days Passed will update everyday
                # no matter what but "Days listed" will only update as long as the listing is on the website. Check unique_id to avoid
                # DUPLICATES in sold.csv
                if (row['Days Passed'] != row['Days listed']) and (row["Unique ID"] not in unique_ids) :
                    writer.writerow(row)
    



if __name__ == "__main__":

    #Make sure only 2 command-line arguments are given. The second argument is the website URL to be parsed in order
    # to be used as the name of CSV files but also to be used to access the link where all the listings are located.
    if len(sys.argv) == 2:

        arg1 = sys.argv[1]

        parts = arg1.split('/')

        BINA_CSV_FILE = f"{parts[4]}.csv"
    else:
        sys.exit("Invalid number of arguments. Must be 2: final_vip.py + website link")

    main()


