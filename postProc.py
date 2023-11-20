import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os
from airfoil import Airfoil
import argparse
import settings
import pyvista as pv
import geometry as geom
import mesh 
import pathlib
import subprocess
import physics
import h5py as h5

#This file stores post-processing functions of any type

cwd = os.getcwd()

def plot_OF_aero_postProc(NACA, type: str):

    #Reads aerodynamic coefficents obtained during simulation and draws plot out of them. The final plot conatins od 3 charts: Cl(t), Cd(t), Cl/Cd(t).
    #The final plot is stored in run/NACA{number}/postProcessing directory 

    columns = ['Time', 'Cd', 'Cd(f)', 'Cd(r)', 'Cl', 'Cl(f)', 'Cl(r)', 'CmPitch', 'CmRoll', 'CmYaw', 'Cs', 'Cs(f)', 'Cs(r)']
    postProc_df  = pd.read_csv(f"{cwd}/run/NACA{NACA}/postProcessing/forceCoeffs1/0/coefficient.dat", names=columns, skiprows=13, delimiter='\t')
    postProc_df['Cl/Cd'] = postProc_df['Cl'] / postProc_df['Cd']

    plt.figure(figsize=(16,10))  
    if type == 'transient':
        x_label = 'time'
    else:
        x_label = 'iteration'

    # Cl
    plt.subplot(131)  
    plt.plot(postProc_df['Time'], postProc_df['Cl'])
    plt.xlabel(x_label)
    plt.ylabel('Cl')
    plt.xlim(postProc_df['Time'].min(), postProc_df['Time'].max())
    plt.ylim( postProc_df['Cl'].min(),  postProc_df['Cl'].max())
    plt.title('Cl')

    # Cd
    plt.subplot(132)  
    plt.plot(postProc_df['Time'], postProc_df['Cd'])
    plt.xlabel(x_label)
    plt.ylabel('Cd')
    plt.xlim(postProc_df['Time'].min(), postProc_df['Time'].max())
    plt.ylim( postProc_df['Cd'].min(),  postProc_df['Cd'].max())
    plt.title('Cd')

    # Cl/Cd
    plt.subplot(133)  
    plt.plot(postProc_df['Time'], postProc_df['Cl/Cd'])
    plt.xlabel(x_label)
    plt.ylabel('Cl/Cd')    
    plt.xlim(postProc_df['Time'].min(), postProc_df['Time'].max())
    plt.ylim( postProc_df['Cl/Cd'].min(),  postProc_df['Cl/Cd'].max())
    plt.title('Cl/Cd')

    #Final operations
    plt.tight_layout()
    plt.savefig(f"{cwd}/run/NACA{NACA}/postProcessing/aeroPlots.png")

def plot_AoA_series_aero(NACA, type = str):

    #Colects data from series of AoA simulations and creates plots of: Cl, Cd, Cl/Cd in function of AoA

    return 0

def plot_OF_residuals_postProc(NACA, type: str):

    #Reads residuals obtained during simulation and draws plot out of them.
    #The final plot is stored in run/NACA{number}/postProcessing directory 

    postProc_df  = pd.read_csv(f"{cwd}/run/NACA{NACA}/postProcessing/forceCoeffs1/0/coefficient.dat", names=columns, skiprows=13, delimiter='\t')

def aeroData_to_HDF(NACA, AoA, Re, simType = str, turb = str):

    #Saves final simulation outcomes to HDF file. 
    #HDF file is stored in simData direstory located in the main airSupport folder

    columns = ['Time', 'Cd', 'Cd(f)', 'Cd(r)', 'Cl', 'Cl(f)', 'Cl(r)', 'CmPitch', 'CmRoll', 'CmYaw', 'Cs', 'Cs(f)', 'Cs(r)']
    postProc_df  = pd.read_csv(f"{cwd}/run/NACA{NACA}/postProcessing/forceCoeffs1/0/coefficient.dat", names=columns, skiprows=13, delimiter='\t')
    postProc_df['Cl/Cd'] = postProc_df['Cl'] / postProc_df['Cd']

    hdf_dict = {
        'Cl': round(postProc_df['Cl'].iloc[-1], 4),
        'Cd': round(postProc_df['Cd'].iloc[-1], 4),
        'Cl/Cd': round(postProc_df['Cl/Cd'].iloc[-1], 4),

    }

    hdf_dict_df = pd.DataFrame(hdf_dict, index=[0])
    data = hdf_dict_df.to_numpy()

    with h5.File(f'{cwd}/simData/simData.hdf5', 'a') as f:
        dset = f.create_dataset(f'NACA{NACA}/{simType}/{turb}/{Re}/{AoA}/aeroData', data=data)
