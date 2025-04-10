import csv
import datetime
import os
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from selenium.common.exceptions import TimeoutException

def main():

    rows = get_entries()

    overwrite(update_final_date(rows))

    get_rid_expired()

    check_dir(rows)




def get_entries():
    with open('sold.csv' , 'r', newline="") as file:

        reader= csv.DictReader(file)
        rows = list(reader)
        return rows



#In sold.csv a lot of the listings aren't actually sold. But rather expired or in some cases renewed. This function updates the rows
#to indicate whether it was sold,expired or renewed by adding a new column "Result" and it puts the updated rows into "sold_updated".csv 
def get_rid_expired():

    try:
        with open("sold_update.csv", "r") as datafile:
            reader = csv.DictReader(datafile)
            rows_sold_update = list(reader)
    except FileNotFoundError:
        rows_sold_update = []

    rows = get_entries()

    updated_rows = []
    
    #To avoid duplicates
    for row in rows:
        for sold_row in rows_sold_update:
            
            if row["Unique ID"] == sold_row["Unique ID"]:
                break
        else:
            driver= webdriver.Chrome()

            driver.get(row["Link"])

            source = driver.page_source

            soup = BeautifulSoup(source, "lxml")

            is_sold = "Satışdan çıxarılıb" in source

            is_expired = "Bu elanın müddəti başa çatıb" in source

            is_missing = "Elan tapılmadı" in source

            is_renewed = "Yeniləndi" in source

            if is_sold is True:
                row["Result"] = "Sold"
                updated_rows.append(row)
            elif is_expired is True:
                row["Result"] = "Expired"
                updated_rows.append(row)
            elif is_missing is True:
                row["Result"] = "Sold"
                updated_rows.append(row)
            elif is_renewed is True:
                row["Result"] = "Renewed"
                updated_rows.append(row)

    
    fieldnames = ["Price", "Area", "Price per m2", "Date", "Days listed", "Days Passed", "Street", "Unique ID", "Link", "Final date", "Result"]

    with open("sold_update.csv" , "a+", newline="") as file:
        file.seek(0)
        empty_file = not file.read(1)
        file.seek(0,2)

        writer = csv.DictWriter(file, fieldnames=fieldnames)
        if empty_file:
            writer.writeheader()
        for row in updated_rows:
            writer.writerow(row)




#This is the same function from "final_vip.py" to download photos and will be used in the function below "check_dirs" to double check if 
# the photos were downloaded as sometimes when there are internet connection problems the process can get disrupted which would later 
# lead to errors in trying to get the html file to load.
def get_bina_photos(unique,street, link):
        
        driver = webdriver.Chrome()

        folder_path = f".\\{street}\\{unique}"
        
        driver.get(link)

        try:
            WebDriverWait(driver, 6).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "product-photos__slider-nav-i_picture")))
        except TimeoutException:
            pass

        source = driver.page_source

        soup = BeautifulSoup(source, 'lxml')

        photo_id = soup.find_all('div', class_='product-photos__slider-nav-i_picture')

        #If listing's photos no longer exists just insert "unavailable-image" photo in folder
        if photo_id == []:
            url = "https://eagle-sensors.com/wp-content/uploads/unavailable-image.jpg"

            os.makedirs(folder_path, exist_ok=True)

            filename = "unavailable.jpg"

            file_path = os.path.join(folder_path,filename)

            r=requests.get(url)

            with open(file_path, 'wb') as file:
                file.write(r.content)
        else:        
            for index,photo in enumerate(photo_id):
                clean_url = photo['style'].replace("background-image: url('", "").replace("jpg')", "jpg")

                filename = f"{index}.jpg"

                os.makedirs(folder_path, exist_ok=True)

                file_path = os.path.join(folder_path, filename)
                
                r = requests.get(clean_url)

                with open(file_path, 'wb') as file:
                    file.write(r.content)
                


#This is to get the date at which the listing was delisted. By adding "Days listed" to the date at which the listing was first posted.
def update_final_date(rows):
    for row in rows:
        time_of_listing = datetime.datetime.strptime(row['Date'], "%d/%m/%Y")

        time_delta = datetime.timedelta(days= int(row["Days listed"]))

        final_date = time_of_listing + time_delta

        row["Final date"] = final_date.strftime("%d/%m/%Y")

    return rows



def overwrite(final_list):

    with open('sold.csv', 'w', newline="") as outfile:
        fieldnames = ["Price", "Area", "Price per m2", "Date", "Days listed", "Days Passed", "Street", "Unique ID", "Link", "Final date"]
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(final_list)



#To check if the listings directory and photos are present so that the HTML can load without errors. Photos might be absent if internet
#connection was disrupted during the first photo downloading phase.
def check_dir(rows):
    
    for row in rows:
        street_name = row["Street"]
        unique = row["Unique ID"]

        path_folder = f".\\{street_name}\\{unique}"
        
        # Folder path doesn't exist at all so create it.
        if not os.path.exists(path_folder):
            get_bina_photos(row["Unique ID"], row["Street"], row["Link"])

        
        # Folder exists but has no photos, so download photos.
        if os.listdir(path_folder) == []:
            get_bina_photos(row["Unique ID"], row["Street"], row["Link"])
            print("Done")

            
        


if __name__ == "__main__":
    main()