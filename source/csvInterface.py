import os
import csv

def buildCsv(fileName = ""):
    if not os.path.isfile(fileName):
        with open(fileName, 'w', newline='') as file:
            writer = csv.writer(file, quotechar='\"')
            field = ["File","DNE","Convex_DNE","Concave_DNE","Convex_Area","Concave_Area","RFI","3D_Area","2D_Area","Alpha","OPCR","0 deg.","5.625 deg.","11.25 deg.","16.875 deg.","22.5 deg.","28.125 deg.","33.75 deg.","39.375 deg.","Slope"]
            writer.writerow(field)

def buildCsvFromObject(fileName = "", dictionary = {}):
    fields = list(dictionary.keys())
    print(fields)
    if not os.path.isfile(fileName):
        with open(fileName, 'w', newline='') as file:
            writer = csv.writer(file, quotechar='\"')
            writer.writerow(fields)

def writeRow(csvWriter, rowObject, keys, formatting):
    data = []
    for key in keys:
        data.append(rowObject[key])
    csvWriter.writerow(data)

def extractData(filePath):
    with open(filePath, 'r') as file:
        csv_reader = csv.DictReader(file)
        data = [row for row in csv_reader]
    return data

# Generate a CSV file from a list of dictionaries
# It will use the first item's keys in the list to generate
# the headers. Non-dictionaries in the list will be ignored. 
# Values without those keys in subsequent objects
# will be ignored. Optionally pass in a dictionary of formatting.
# Pair the key with the formatting function to format all of the data
# Data with mismatching data types or formatting failure with be treated
# as a string.
def buildCsvFromData(fileName = "", data = [], formatting = {}):
    gen = (
        item for item in data
        if isinstance(item, dict)
    )

    firstItem = next(gen)
    keys = list(firstItem.keys())
    buildCsvFromObject(fileName, firstItem)
    with open(fileName, 'a', newline='') as file:
        csvWriter = csv.writer(file, quotechar='\"')
        writeRow(csvWriter, firstItem, keys, formatting)

        for item in gen:
            writeRow(csvWriter, item, keys, formatting)

def addDataToCsv(fileName = "", data = [], formatting = {}):
    gen = (
        item for item in data
        if isinstance(item, dict)
    )

    firstItem = next(gen)
    keys = list(firstItem.keys())
    with open(fileName, 'a', newline='') as file:
        csvWriter = csv.writer(file, quotechar='\"')
        for item in gen:
            writeRow(csvWriter, item, keys, formatting)

def addObjectToCSV(fileName = "", item = {}, formatting = {}):
    keys = list(item.keys())
    with open(fileName, 'a', newline='') as file:
        csvWriter = csv.writer(file, quotechar='\"')
        writeRow(csvWriter, item, keys, formatting)

def build_data_from_csv(file_path):
    data = {}
    if os.path.exists(file_path):
        with open(file_path, mode='r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)  # Reads CSV into a list of dictionaries
            for row in reader:
                file_key = row.pop("File")  # Extract the "File" column as the key
                data[file_key] = row  # Remaining columns are the value (as a dictionary)
    return data
           
