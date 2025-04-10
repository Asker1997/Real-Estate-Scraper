from flask import Flask
from flask import render_template
import csv
import os



#Changed static folder to be the original directory itself rather than "static". 
app = Flask(__name__, static_folder="/")


#This function will filter for only the "Sold" listings in sold_update.csv and exclude "Expired" or "Renewed"
def get_sold_csv(show_all):

    update_rows = []

    with open("sold_update.csv") as file:
        reader = csv.DictReader(file)
        rows = list(reader)

    for row in rows:
        if row["Result"] == "Sold" or show_all == True:
            update_rows.append(row)

    return update_rows






# This is an optional function which I use sometimes to get the latest listings(be it sold,expired or renewed) by getting the latest 
# date from the "Final Date" column 

# def get_latest_date():
#     rows = get_sold_csv()

#     reference = datetime.datetime.strptime("01/01/2000", "%d/%m/%Y")

#     for row in rows:
#         current = datetime.datetime.strptime(row["Final date"], "%d/%m/%Y")

#         if current > reference:
#             reference = current

#     reference = reference.strftime("%d/%m/%Y")
#     return reference




#This is related to the optional function above get_latest_date and this function uses that function to actually get the 
# listings from the sold.csv file that have the "Final Date" that is == to get_latest_date

# def get_entries_latest():
#     collection = []

#     rows = get_sold_csv()

#     latest_date = get_latest_date()

#     for row in rows:
#         if row["Final date"] == latest_date:
#             collection.append(row)

#     return collection





# Adds a row["photos"] that is a list of paths to photos
def take_rows_and_add_field_called_photos(rows):

    for row in rows:
        street_name = row["Street"]
        unique = row["Unique ID"]

        path = f".\\{street_name}\\{unique}"

        collection = os.listdir(path)

        row["Photos"] = []

        for image in collection:
            row["Photos"].append(f"{street_name}/{unique}/{image}")

        #To clean the area square symbol
        row["Area"] = row["Area"].replace("ï¿½","2")



#This shows only the SOLD listings
@app.route("/")
def show_sold():

    rows = get_sold_csv(False)
    take_rows_and_add_field_called_photos(rows)

    return render_template("carousel_layout_row.html", name=rows)


#This shows all the listings. Expired,renewed, and sold
@app.route("/all")
def show_all():

    rows = get_sold_csv(True)
    take_rows_and_add_field_called_photos(rows)

    return render_template("carousel_layout_row.html", name=rows)


