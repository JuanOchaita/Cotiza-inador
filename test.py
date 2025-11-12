import csv

language = "en"

with open("card_information.csv", newline="") as file:
    reader = csv.DictReader(file)
    for counter, row in enumerate(reader):
        if counter % 5 == 0:
            print(f"{counter}: {row['card_name']} - {language} - {row['set_name']} - {row['number_in_set']} - {row['image']} - {row['printing_option']}")
