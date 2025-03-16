from glob import glob
import os
import re
import csvInterface
from utilities import isfloat

def combineData(folder = "./data", controlGroup = "sample_control"):
    # create new combined output csv
    # get all csv files
    files = glob(f"{folder}/*.csv", recursive = False)
    data = []
    errors = {}

    # extract data and add category
    for file in files:
        fileName = os.path.basename(os.path.normpath(file))
        algorithm = re.sub(r"_(failed|analysis|errorCount).csv", "", fileName)
        rfiSuccess = bool(re.search(r"analysis", fileName))
        extractedData = csvInterface.extractData(file)
        extractedData = [dict(item, **{'Algorithm':algorithm, 'RFISuccess': rfiSuccess}) for item in extractedData]
        for row in extractedData:
            if(not isfloat(row['RFI'])):
                if row['RFI'] not in dict.keys(errors):
                    errors[row['RFI']] = 0
                errors[row['RFI']] = errors[row['RFI']] + 1
                row['RFI'] = 'error'
        data.extend(extractedData)

    errorList = list(errors.keys())
    errorCounts = []
    for error in errorList:
        errorCounts.append({'name': error, 'count': errors[error]})
    

    # save control data into dictonary for easy lookup
    csvInterface.buildCsvFromData("output/fullAnalysis.csv", data)
    csvInterface.buildCsvFromData("output/errorCount.csv", errorCounts)

    # for each non-control dataset, create calculation output file
    # run calculations on each row of non-control data
    # append data to rows in calculation output file
    return