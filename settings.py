import numpy as np

# SIMULATION SETTINGS
Uinlet = 10 # m/s
c = 1 # m - chord length
Type = 'steady' # simulation type ['steady', 'transient']
turbModel = 'k-omega' # Turbulance model - all avialable in OpenFoam
AoA_single = 0
AoA_range = np.arange(0,4,1)
mapFields = True # Implements mapping from lower AoA results [True, False]
parallel = True # Implements parallel computation: [True, False]
NP = 4

# PHYSICS SETTINGS
ro = 1.293 # kg/m3 - Air denisty
visc = 1e-05 #m2/s - viscosity

# AIRFOIL SETTINGS:
A = 0 #NACA0018
T = 0.18 #NACA0018
N = 100 # number of points without trailing edge

# AIRFOIL TRAILING EDGE SETTINGS:
NT = 10 #number of points on trailing edge
ST = 20 #starting degree value
ET = 90 #ending degree value

