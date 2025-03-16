# VersaMesh
Automates the workflow for preparing 3D dental scans for scientific research.

## Getting Started

Ensure you have access to the following requirements:

- Python v3.12.3
- pymeshlab build#2023.12.post1
- rpy2 v3.5.16
- R v4.4
- molaR v5.3
- Rvcg v0.22.2

### Installation Steps

In the terminal, navigate to the main folder containing the project. Next, run the steps involved with both Python and R.

#### Python

1. Download and install python https://www.python.org/downloads/
2. install dependencies 
```
pip install pymeshlab
pip install rpy2
```

3. If Windows, set the `R_HOME` environment variable to the root directory of the R installation. Here is a powershell script to run:
```powershell
$Env:R_HOME = "C:\Program Files\R\R-{{version}}"
```

#### R
This project uses the recommended [renv package](https://ecorepsci.github.io/reproducible-science/renv.html) for managing outside dependencies. To download and install all required packages, follow these steps:

The x86_64 architecture is required for this to run correctly.

1. Ensure you have the renv package installed in your local environment. Run the following code in the console:

```
install.packages('renv')
```

2. Install the required packages by running this code in the console:
```
renv::restore()
```


### Running the program

`py ./source/run.py`

1. Change any settings necessary with the `set` command.
2. Simplify and smooth the ply files in the input directory using the `process` command. The simplified and smoothed files will be saved in the `outputFolder` in the settings.
3. Run the `analyze` command to calculate topographical data points. Results will be output to a series of CSV files in the `ouputFolder` settings. There will be one CSV for each algorithm and a comprehensive CSV called `fullAnalysis.csv`.

## For Developers

### Compiling the program

`pyinstaller --onefile --collect-all=pymeshlab .\source\run.py`

### Versioning

## Documentation

### Supported algorithms

There are currently 8 supported algorithms:

- morley
- morley_preserveBoundary
- morley_remesh
- morley_remesh_preserveBoundary
- deVries
- deVries_preserveBoundary
- deVries_preserveBoundary
- deVries_remesh
- deVries_remesh_preserveBoundary

### Supported topographic analytical data 

- DNE
- Convex_DNE
- Concave_DNE
- Convex_Area
- Concave_Area
- OPCR
- 0 deg
- 5.625
- 11.25 deg.
- 16.875 deg.
- 22.5 deg.
- 28.125 deg.
- 33.75 deg.
- 39.375 deg.
- RFI_Boyer
- RFI_Ungar

## Information

Samples: Unworn primate teeth

1. Morley & Berthaume (Rvcg smoothing)
2. Devries (needs meshlab smoothing)
3. Morley w/ Preserve Boundary
4. Devries w/ Preserve Boundary
5. Morley w/ Isotropic Explicit Remeshing
6. Devries w/ Isotropic Explicit Remeshing
7. Morley w/ Isotropic Explicit Remeshing & Preserve Boundary
8. Devries w/ Isotropic Explicit Remeshing & Preserve Boundary
9. Proprietary (Avizo) (analysis only)

Morley cleans by removing components with fewer than 5000 connected faces.
Morley suggests using Quadric Edge Collapse Decimation to simplify. Setting Target Face Count to 10,000, quality threshold to 1, and preserve normal to true.
Morley suggests smoothing using Rvcg.

de Vries suggests a number of MeshLab filters to clean the scan prior to simplification and smoothing.
meshing_remove_connected_component_by_diameter
    - likely using default value and copied a specific absolute value
de Vries suggests using default values for Quadric Edge Collapse Decimation except for Target Face Count set to 10,000
de Vries suggests choosing the most ideal smoothing algorithm
    - chose "lightest" smoothing because we are using structured blue light scans and do not need to smooth voxels according to Spradley et al 2017. Increasing smoothing iterations can introduce artifacts

Values to collect
Relief Index (RFI)
Dirichlet Normal Energy (DNE)
Orientation Patch Count (OPC)

Compare analysis differences (RFI, OPC, DNE) by looking at absolute difference and % difference with all data sets
Look at diet classification predictive efficacy of each pipeline using linear discriminant analysis (LDA)

## Statistical analysis

- Shapiro-Wilk test - distribution normality for determining parametric testing suitability
- compare absolute difference between each scans
- compare % differences between each scans
- anova (analysis of variance)
- wilcoxian signed rank test
- linear discriminant analysis
- quadradic discriminant analysis

## References

Morley, M. J., & Berthaume, M. A. (2023). Technical note: A freeware, equitable approach to dental topographic analysis. American Journal of Biological Anthropology, 182(1), 143-153. https://doi.org/10.1002/ajpa.24807

de Vries, D., Janiak, M.C., Batista, R. et al. Comparison of dental topography of marmosets and tamarins (Callitrichidae) to other platyrrhine primates using a novel freeware pipeline. J Mammal Evol 31, 12 (2024). https://doi.org/10.1007/s10914-024-09704-9

Spradley JP, Pampush JD, Morse PE, Kay RF. Smooth operator: The effects of different 3D mesh retriangulation protocols on the computation of Dirichlet normal energy. Am J Phys Anthropol. 2017; 163: 94–109. https://doi.org/10.1002/ajpa.23188