import meshlab_interface as meshlab
import time
import R_interface as R
import glob

from data import combineData

DEFAULT_SETTINGS = {
    "inputFolder": "data",
    "outputFolder": "output",
    "algorithms": "morley, morley_preserveBoundary, morley_remesh, morley_remesh_preserveBoundary,deVries, deVries_preserveBoundary, deVries_preserveBoundary, deVries_remesh, deVries_remesh_preserveBoundary"
}

SUPPORTED_ALGORITHMS = [
    "morley", 
    "morley_preserveBoundary", 
    "morley_remesh",
    "morley_remesh_preserveBoundary",
    "deVries",
    "deVries_preserveBoundary", 
    "deVries_preserveBoundary",
    "deVries_remesh",
    "deVries_remesh_preserveBoundary"
]

class ProcessEngine():
    def __init__(self, settings = DEFAULT_SETTINGS):
        self.settings = settings
        R.init()

    def update_setting(self, key, value):
        if key in self.settings:
            self.setValue(key, value)
        else:
            raise ValueError(f"Error: '{key}' is not a valid setting.")
        
    def setValue(self, key, value):
        current_value = self.settings[key]
        if isinstance(current_value, int):
            value = int(value)
        elif isinstance(current_value, float):
            value = float(value)

        if(key == "algorithms"):
            algorithms = [a.strip() for a in value.split(',')]
            validAlgorithms = []
            for a in algorithms:
                if a not in SUPPORTED_ALGORITHMS:
                    print(f"{a} is not a supported algorithm and will be skipped. Algorithm names are case sensitive.")
                else:
                    validAlgorithms.append(a)
            if len(validAlgorithms) != 0:
                value = ", ".join(validAlgorithms)
            else:
                print(f"No supported algorithms were provided. No changes made.")
        
        if(key == "inputFolder"):
            inputDir = self.settings['inputFolder']
            files = glob.glob(f'{inputDir}/*.ply')
            if(len(files) == 0):
                print(f'0 .ply files were found in the provided inputFolder, please verify the folder is correct.')
                
        self.settings[key] = value
        
    def process(self):
        start_time = time.time()

        inputDir = self.settings['inputFolder']
        outputDir = self.settings['outputFolder']
        algorithms = [x.strip() for x in self.settings['algorithms'].split(',')]
        morleyProcessed=False

        if(len(algorithms) < 1):
            raise Exception("No algorithms provided.")

        if('morley' in algorithms):
            meshlab.simplifyAll(meshlab.morleyCleanAndSimplify, inputDir, f'{outputDir}/simplified_morley')
            morleyProcessed = True
        if('morley_preserveBoundary' in algorithms):
            meshlab.simplifyAll(meshlab.morleyCleanAndSimplify, inputDir, f'{outputDir}/simplified_morley_preserveBoundary', preserveBoundary = True)
            morleyProcessed = True
        if('morley_remesh' in algorithms):
            meshlab.simplifyAll(meshlab.morleyCleanAndSimplify, inputDir, f'{outputDir}/simplified_morley_remesh', remesh = True)
            morleyProcessed = True
        if('morley_remesh_preserveBoundary' in algorithms):
            meshlab.simplifyAll(meshlab.morleyCleanAndSimplify, inputDir, f'{outputDir}/simplified_morley_remesh_preserveBoundary', remesh = True, preserveBoundary = True)
            morleyProcessed = True
        
        # Smooth and clean in R according to the morley paper
        if morleyProcessed:
            R.smooth()

        # Simplifies a ply file using the algorithm settings defined in de Vries et al. 2024
        # include runs with preserveBoundary, isotropic remeshing, and both
        if('deVries' in algorithms):
            meshlab.simplifyAll(meshlab.deVriesCleanAndSimplify, inputDir, f'{outputDir}/simplified_deVries')
        if('deVries_preserveBoundary' in algorithms):
            meshlab.simplifyAll(meshlab.deVriesCleanAndSimplify, inputDir, f'{outputDir}/simplified_deVries_preserveBoundary', preserveBoundary = True)
        if('deVries_preserveBoundary' in algorithms):
            meshlab.simplifyAll(meshlab.deVriesCleanAndSimplify, inputDir, f'{outputDir}/simplified_deVries_preserveBoundary', preserveBoundary = True)
        if('deVries_remesh' in algorithms):
            meshlab.simplifyAll(meshlab.deVriesCleanAndSimplify, inputDir, f'{outputDir}/simplified_deVries_remesh', remesh = True)
        if('deVries_remesh_preserveBoundary' in algorithms):
            meshlab.simplifyAll(meshlab.deVriesCleanAndSimplify, inputDir, f'{outputDir}/simplified_deVries_remesh_preserveBoundary', remesh = True, preserveBoundary= True)
        
        print("--- %s seconds ---" % (round(time.time() - start_time, 2)))

    def analyze(self):
        outputDir = self.settings['outputFolder']
        # Run analysis on all files
        R.analyzeAll(outputDir)