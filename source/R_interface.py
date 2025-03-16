import os
from glob import glob
from rpy2.robjects.packages import importr
from csvInterface import buildCsvFromObject, addDataToCsv, addObjectToCSV, build_data_from_csv
import time
from utilities import is_windows
import re
from pathlib import Path
from rpy2 import robjects
import rpy2.robjects.packages as rpackages

def init():
    print(f'Installing necessary R packages.')
    utils = rpackages.importr('utils')
    utils.chooseCRANmirror(ind=1)
    utils.install_packages("Rvcg")
    utils.install_packages("molaR")
    utils.install_packages("V8")
    utils.install_packages("doolkit")

def smooth(targetDir = "output"):
    Rvcg = rpackages.importr("Rvcg")
    molaR = rpackages.importr("molaR")

    def mbSmooth(mesh):
        smoothed_mesh = Rvcg.vcgSmooth(mesh, **{'type': ["taubin"], 'iteration': 10, 'lambda': 0.9, 'mu': -0.95})
        
        return(smoothed_mesh)

    def mbClean(mesh):
        cleaned_mesh = molaR.molaR_Clean(mesh, cleanType = "Both", verbose = True)
        return(cleaned_mesh)

    def process(file, inputDir):
        try:
            newFileName = re.sub(".ply", "_smoothed.ply", os.path.basename(os.path.normpath(file)))
            normalizedFileName = os.path.normpath(file)
            normalizedSmoothedFileName = os.path.normpath(Path("/".join([inputDir, "smoothed", newFileName])))
            if(os.path.exists(normalizedSmoothedFileName)):
                print(f'{file} has already been smoothed by this algorithm. Skipping...')

            # Import mesh & set filename
            mesh = Rvcg.vcgPlyRead(normalizedFileName, updateNormals = True, clean = True)

            # Smoothing protocol of Morley & Berthaume (2023) using Rvcg
            mesh_smooth = mbSmooth(mesh)

            # Cleaning mesh vertices & faces
            mesh_clean = mbClean(mesh_smooth)

            # Export smoothed & cleaned mesh as a new PLY file
            normalizedSmoothedFileName = os.path.normpath(Path("/".join([inputDir, "smoothed", newFileName])))
            Rvcg.vcgPlyWrite(mesh_clean, normalizedSmoothedFileName, binary = True)
        except Exception as e:
            print(f"An error occured while processing '{file}'.")
            print(e)

    print(f"Applying Morley smoothing algorithm to '{targetDir}'.")
    dirs = glob(f"{targetDir}/*_morley*", recursive = False)
    print(f"Found {len(dirs)} folder{"" if len(dirs) == 1 else "s"} containing '_morley'.")
    for d in dirs:
        if(not os.path.isdir(d)):
            continue
        Path(f"{d}/smoothed").mkdir(parents=True, exist_ok=True)
        listply = glob(f"{d}/*.ply")
        total = len(listply)
        counter = 1
        print(f"Found {total} .ply file{"" if total == 1 else "s"} in '{d}'.")
        for file in listply:
            print(f"Processing file {counter} of {total}...")
            process(file, d)
            counter += 1

def analyze(file, doolkit):
    fileName = os.path.basename(os.path.normpath(file))
    Rvcg = importr("Rvcg")
    molaR = importr("molaR")
    
    mesh = Rvcg.vcgPlyRead(file, updateNormals = True, clean = True)
    dne = molaR.DNE(mesh, BoundaryDiscard = "Vertex")
    opcr = molaR.OPCr(mesh)
    rfiBoyer = doolkit.rfi(mesh, method = "Boyer", hull = "concave")
    rfiUngar = doolkit.rfi(mesh, method = "Ungar", hull = "concave")

    results = {}
    results["File"] = fileName
    results["DNE"] = dne[0][0]
    results["Convex_DNE"] = dne[1][0]
    results["Concave_DNE"] = dne[2][0]
    results["Convex_Area"] = dne[3][0]
    results["Concave_Area"] = dne[4][0]
    results["OPCR"] = opcr[0][0]
    results["0 deg."] = opcr[1][8]
    results["5.625 deg."] = opcr[1][9]
    results["11.25 deg."] = opcr[1][10]
    results["16.875 deg."] = opcr[1][11]
    results["22.5 deg."] = opcr[1][12]
    results["28.125 deg."] = opcr[1][13]
    results["33.75 deg."] = opcr[1][14]
    results["39.375 deg."] = opcr[1][15]
    results["RFI_Boyer"] = rfiBoyer[0]
    results["RFI_Ungar"] = rfiUngar[0]
    return results

def analyzeAll(outputDir = 'output'):
    print(f'Analyzing all 3D scans within the output folder.')

    rpackages.importr("V8")
    doolkit = rpackages.importr("doolkit")

    fullAnalysisOutputFile = f"{outputDir}/fullAnalysis.csv"
    dirs = glob(f"{outputDir}/*", recursive = False)

    alreadyComplete = build_data_from_csv(fullAnalysisOutputFile)

    for dir in dirs:
        # skip csv files, and temporary folders
        if(".csv" in dir or "analyzed" in dir or "temp" in dir or "failed" in dir):
            continue
        groupStartTime = time.time()
        groupName = os.path.basename(os.path.normpath(dir))
        groupAnalysisOutputFile = f"{outputDir}/{groupName}_analysis.csv"
        print(f'Analyzing all files within {groupName}.')

        files = glob(f'{dir}/smoothed/*.ply')

        for file in files:
            fileStartTime = time.time()
            fileName = os.path.basename(os.path.normpath(file))

            if(fileName in alreadyComplete):
                print(f'Analysis is already done on this {fileName}. Skipping...')
                continue

            print(f'Analyzing {fileName} from {groupName}.')
            analysis = analyze(file, doolkit)
            processTime = round(time.time() - fileStartTime, 2)
            analysis["Algorithm"] = groupName
            analysis["processTime"] = processTime
            
            if(not os.path.isfile(fullAnalysisOutputFile)):
                buildCsvFromObject(fullAnalysisOutputFile, analysis)
            
            if(not os.path.isfile(groupAnalysisOutputFile)):
                buildCsvFromObject(groupAnalysisOutputFile, analysis)

            addObjectToCSV(fullAnalysisOutputFile, analysis)
            addObjectToCSV(groupAnalysisOutputFile, analysis)

            print(f'Analysis complete for {fileName}.')
            print(f"--- Processing Time: {processTime} seconds ---")
        print(f'Finished processing {groupName}')
        print(f'--- Processing Time: {round(time.time() - groupStartTime, 2)} seconds')
    print(f'Analysis complete.')
    print(f'--- Processing Time: {round(time.time() - groupStartTime, 2)} seconds') 