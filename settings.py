import numpy as np

#Lists of possible settings
sim_type_list = ['steady', 'transient']
turbModel_list = ['kEpsilon', 'kOmega', 'kOmegaSST']
meshing_type_list = ['blockMesh', 'cfMesh']
VAWT_geom_type_list = ['savonius', 'darrieus']

# SIMULATION SETTINGS
Uinlet = 10 # m/s
c = 1 # m - chord length
sim_type = 'steady' # simulation type. Types available -> see sim_type_list
turbModel = 'kOmegaSST' # Turbulance model. Types available -> see turbModel_list
AoA_single = 0
AoA_range = np.arange(0,4,1)
mapFields = True # Implements mapping from previous AoA results [True, False]
parallel = True # Implements parallel computation: [True, False]
NP = 2 # Number of processors for parallelisation
meshing_type = 'blockMesh' # Type of an airfoil meshing strategy. Types available -> see meshing_type_list

# PHYSICS SETTINGS
ro = 1.293 # kg/m3 - Air denisty
visc = 1e-05 #m2/s - viscosity

# AIRFOIL SETTINGS:
# A = 0 #NACA0018
# T = 0.18 #NACA0018
N = 100 # number of points without trailing edge

# AIRFOIL TRAILING EDGE SETTINGS:
NT = 10 #number of points on trailing edge
ST = 20 #starting degree value
ET = 90 #ending degree value

# VAWT SETTINGS:
VAWT_geom_type = 'savonius' #Geometry type. Types available -> see VAWT_geom_type_list
#SAVONIUS SETTINGS:
sav_d_shaft = 0.1
sav_d_in = 1.8
sav_d_out = 2
sav_dist = 0.2



