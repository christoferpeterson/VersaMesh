import pymeshlab
from pathlib import Path
import glob
import os

def simplifyAll(
    simplifyFunc, 
    inputDir = 
    'data', 
    outputDir = 'output/simplified', 
    remesh = False, 
    preserveBoundary = False
):
    files = glob.glob(f'{inputDir}/*.ply')

    total = len(files)
    print(f'Found {total} files in {inputDir} to process.')
    i = 1
    for file in files:
        print(f'Simplifying file {i} of {total} "{file}"')
        simplifyFunc(file, outputDir, remesh = remesh, preserveBoundary = preserveBoundary)
        i = i + 1

def morleyCleanAndSimplify(
        path, 
        outputDir = 'output/simplified',
        remesh = False, 
        preserveBoundary = False
    ):
    try:
        print(f'Applying Morley cleaning and simplifying to "{path}".')

        # prepare the output
        Path(outputDir).mkdir(parents=True, exist_ok=True)
        fileName = os.path.basename(path).replace('.ply', '')
        outputFileName = f'{outputDir}/{fileName}_simplified.ply'

        # verify simplification hasn't already been done
        if os.path.exists(outputFileName):
            print(f'{fileName} has already been smoothed by this algorithm. Skipping...')
            return

        meshSet = pymeshlab.MeshSet()
        meshSet.load_new_mesh(path)

        # morley specific MeshLab parameters
        minComponentSize = 5000
        faceCount = 10000
        qualityThreshold = 1.000000

        meshSet.meshing_remove_connected_component_by_face_number(mincomponentsize = minComponentSize)
        meshSet.meshing_decimation_quadric_edge_collapse(targetfacenum = faceCount, qualitythr = qualityThreshold, preservenormal = True, preserveboundary = preserveBoundary)

        if remesh:
            # attempts to make the triangles a uniform area
            meshSet.meshing_isotropic_explicit_remeshing()

        # export
        meshSet.save_current_mesh(outputFileName)
    except Exception as e:
        print(f'Failed to simplify "{path}" with this algorithm. Details: {e}')

def deVriesCleanAndSimplify(        
        path, 
        outputDir = 'output/simplified',
        remesh = False, 
        preserveBoundary = False
    ):
    try:
        faceCount = 10000
        meshSet = pymeshlab.MeshSet()

        fileName = os.path.basename(path).replace('.ply', '')
        Path(outputDir).mkdir(parents=True, exist_ok=True)
        Path(f'{outputDir}/smoothed').mkdir(parents=True, exist_ok=True)
        simplifiedOutputFileName = f'{outputDir}/{fileName}_simplified.ply'
        smoothedOutputFileName = f'{outputDir}/smoothed/{fileName}_smoothed.ply'

        if not os.path.exists(simplifiedOutputFileName):
            meshSet.load_new_mesh(path)
            
            # Extracted from cleanscript.xml supplied in de Vries online supplemental documentation
            meshSet.meshing_remove_connected_component_by_diameter()
            meshSet.meshing_remove_connected_component_by_face_number()
            meshSet.meshing_remove_duplicate_faces()
            meshSet.meshing_remove_duplicate_vertices()
            meshSet.meshing_remove_unreferenced_vertices()
            meshSet.meshing_remove_null_faces()
            meshSet.compute_selection_by_non_manifold_edges_per_face()
            meshSet.compute_selection_by_non_manifold_per_vertex()
            meshSet.meshing_remove_selected_vertices_and_faces()
            meshSet.meshing_re_orient_faces_coherently()

            # Extracted from simplifyscript.xml supplied in de Vries online supplemental documentation
            meshSet.meshing_decimation_quadric_edge_collapse(targetfacenum = faceCount, preservenormal = True, preserveboundary = preserveBoundary)

            if remesh:
                # attempts to make the triangles a uniform area
                meshSet.meshing_isotropic_explicit_remeshing()

            # export the simplified file
            meshSet.save_current_mesh(simplifiedOutputFileName)
        else:
            print(f'{fileName} has already been simplified by this algorithm. Skipping and loading the result...')
            meshSet.load_new_mesh(simplifiedOutputFileName)

        if not os.path.exists(smoothedOutputFileName):
            meshSet.apply_coord_hc_laplacian_smoothing()

            # export the smoothed file
            meshSet.save_current_mesh(smoothedOutputFileName)
        else:
            print(f'{fileName} has already been smoothed by this algorithm. Skipping...')
    except Exception as e:
        print(f'Failed to simplify and smooth {path} using the de Vries algorithm. Details: {e}')