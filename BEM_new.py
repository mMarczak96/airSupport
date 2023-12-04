import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
import sys
import time

cwd = os.getcwd()
start_time = time.time()
# Estimations
def radius_estimation(P, Cp, ni, ro, U):
    # Estimates a radius of a wind turbine for given:
    # P -> power, Cp -> power coeff, ni -> mechanical and elec. efficiency, ro -> density, U -> freestream velocity
    radius = math.sqrt(P/(Cp*ni*0.5*ro*math.pi*pow(U,3)))
    return radius

def TSR_estimation(r, omega, U):
    # Estimates local tip speed ratio for given:
    # r -> local radius, omega -> local rotational speed [rad/s], U -> freestream velocity
    TSR = (omega * r) / U
    return TSR

def rotational_speed_estimation(U, TSR, r):
    # Estimates local rotational speed for givenL
    # U -> freestream velocity, TSR -> tip speed ratio, r -> blade radius
    omega = (U * TSR) / r
    return omega

def twist_estimation(TSR_local):
    # Estimates a local blade twist angle (beta) for given local tip speed ratio
    # twist_angle = 90 - 2 / 3 * np.rad2deg(pow(np.tan(1 / TSR_local), -1))
    # twist_angle = 90 - 2 / 3 * pow(np.tan(1 / TSR_local), -1)     
    twist_angle = 2 / 3 * pow(np.tan(1 / TSR_local), -1)     
    return twist_angle

def chord_estimation(r, twist_angle, n_blades, TSR_local):
    # Estimates chord length for a given:
    # r -> local radius, twist angle, n_blades -> number of blades, TSR_local -> local tip speed ratio
    chord = (8 * math.pi * r * np.cos(np.rad2deg(twist_angle))) / (3 * n_blades * TSR_local)
    return chord

def solidity_estimation(n_blades, chord, r):
    solidity = (n_blades * chord) / (2 * math.pi * r)
    return solidity

def axial_factor_estimation(twist_angle, solidity, Cl):
    # Estimates a local axial induction factor for given:
    # twist angle, local solidity, Cl -> local lift force coeff.
    axial_factor = pow(1 + ((2 * pow(np.cos(np.deg2rad(twist_angle)), 2)) / (solidity * Cl * np.sin(np.deg2rad(twist_angle)))), -1)
    return axial_factor

def tangential_factor_estimation(axial_factor):
    # Estimates a local tangential induction factor for a given axial induction factor
    tangential_factor = (1 - 3 * axial_factor) / (4 * axial_factor - 1)
    return tangential_factor

def read_blade_table(path: str):
    blade_df = pd.read_csv(path)
    return blade_df

#Constants 
P, Cp, ni, ro, U = 100000, 0.35, 0.9, 1.3, 11.5
TSR = 5
R = round(radius_estimation(P,Cp,ni,ro,U),0)
omega = (U * TSR) / R
n_blades = 3 
n_elements = 10
tol = 1e-06

# blade_df = pd.DataFrame()
# blade_df['element'] = np.arange(1, n_elements + 1, 1)
# blade_df['radius'] = (R / n_elements) * blade_df['element']
# blade_df['TSR_local'] = TSR_estimation(blade_df['radius'], omega, U)
# blade_df['twist_angle'] = twist_estimation(blade_df['TSR_local'])
# blade_df['chord'] = chord_estimation(blade_df['radius'],blade_df['twist_angle'],n_blades,blade_df['TSR_local'])
# blade_df['solidity'] = solidity_estimation(n_blades, blade_df['chord'], blade_df['radius'])
# blade_df['axial_fac'] = axial_factor_estimation(blade_df['twist_angle'],blade_df['solidity'], 1)
# blade_df['tangential_fac'] = tangential_factor_estimation(blade_df['axial_fac'])

#Reading the reference data from Qblade
path = f'{cwd}/resources/reference_project/'
blade_df = read_blade_table(f'{path}/reference_turbine.csv')
columns_foil = ['AoA', 'Cl', 'Cd', 'Cm']
foils_list = ['Cylinder1', 'Cylinder2', 'DU21_A17', 'DU25_A17', 'DU30_A17', 'DU35_A17', 'DU40_A17', 'NACA64_A17' ]
foils_data_dict = {}
for foil in foils_list:
    foils_data_dict[f'{foil}'] = pd.read_csv(f'{path}/{foil}.dat' ,names=columns_foil, skiprows=14,delim_whitespace=True)

#Starting BEM
blade_df['solidity'] = (blade_df['chord'] * n_blades) / (2 * math.pi * blade_df['pos'].iloc[-1])
blade_df['axial_fac'] = 0.1
blade_df['tangential_fac'] = 0.01
if (blade_df['solidity'] >= 1).any():
    print(' - - - Solidity cannot be greater than 1!- - - \n - - - Breaking the loop! - - -')
    sys.exit()

for element in blade_df.index:

    
    print(f'Computing forces for element no.{element + 1}:')


    



print(blade_df)














print("--- %s seconds ---" % (time.time() - start_time))