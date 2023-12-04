from cgitb import reset
import math
from turtle import color
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os
import sys
import pyvista as pv 
from subprocess import PIPE, run
from physics import run_cmd
import geometry as geom
import VAWT
import postProc
from airfoil import Airfoil
import settings

#blade data
blade_df = pd.DataFrame()
blade_df['pos'] = np.arange(0,10,1)
blade_df['c'] = np.array([1,1,1,0.9,0.8,0.7,0.6,0.5,0.4,0.3])
# blade_df['twist'] = np.array([0,0,5,10,15,20,25,30,35,40])
blade_df['twist'] = np.array([30,25,23,20,15,13,12,10,8,5])
blade_df['airfoil'] = np.array(['NACA0020','NACA0020','NACA0020','NACA0020','NACA0020','NACA0010','NACA0010','NACA0010','NACA0010','NACA0010',])
#Airfoil data
airfoil_dict ={}
for T in [0.20, 0.10]:
    A = 0.0
    Naca = Airfoil('NACA0015', A, T, settings.N)
    plus = Naca.foil_cords_plus(A, T, settings.N)
    min = Naca.foil_cords_min(A, T, settings.N)
    te = Naca.roundedTE(settings.NT, settings.ST, settings.ET, plus)
    airoifl_df = pd.concat([plus,min,te])
    airfoil_dict[f'NACA00{int(T*100)}'] = airoifl_df


def generate_blade_mesh(blade_df,airfoil_dict):
    # Generates blade mesh in .stl format
    # Requires: 
    # blade_df -> data frame with general blade information: position of an airfoil, chord, twist, airfoil name
    # airfoil_dict -> dictionary containing data frames with coordinates for every airfoil used in a blade
    blade_mesh = pv.PolyData()
    for index, column in blade_df.iterrows():
        foil = blade_df.loc[index].at['airfoil']

        for foil in airfoil_dict.keys():
            airfoil_df = airfoil_dict[f'{foil}']
            airfoil_mesh = pv.PolyData(np.column_stack((airfoil_df['X'],airfoil_df['Y'],airfoil_df['Z'])))
            airfoil_mesh_element_scaled = airfoil_mesh.scale([blade_df.loc[index].at['c'],blade_df.loc[index].at['c'],1])
            airfoil_mesh_element_rotated = airfoil_mesh_element_scaled.rotate_z(blade_df.loc[index].at['twist'] ,point = [0.5,0,0])
            airfoil_mesh_element_translated = airfoil_mesh_element_rotated.translate([0,0,[blade_df.loc[index].at['pos']][0]])
            blade_mesh = blade_mesh.merge(airfoil_mesh_element_translated)
   
    blade_volume = blade_mesh.delaunay_3d(alpha=3, tol=0.5, offset=2.5, progress_bar=True)
    blade_shell = blade_volume.extract_surface(pass_pointid=False, pass_cellid=False)

    return blade_shell

def generate_rotor_geometry(blade_shell, n: int,r: float, L: float):
    # Generates rotor mesh in .stl format
    # Requires:
    # blade_shell -> surface ot a blade obtained from generate_blade_mesh() function
    # n -> number of blades, r -> radius of a hub, L -> lenght of a hub
    
    rotor_dict = {}
    blade_shell = blade_shell.rotate_z(180, point=[0.5,0,0])
    for blade in np.arange(0,360,360/n):
        rotor_dict[f'blade{blade}'] = blade_shell.rotate_x(blade, point=[0.5,0,0])

    cylinder = pv.Cylinder(center=[0,0,0], direction=[1,0,0], radius=r, height=L)
    sphere = pv.Sphere(center=[L/2,0,0], direction=[-1,0,0], radius=r, end_phi=90, theta_resolution=100)
    tower = pv.Cylinder(center=[0,0,0], direction=[0,0,1], radius=r/2, height=10)
    tower = tower.translate([0,0,-5])
    
    for part in [cylinder, sphere, tower]:
        rotor_dict[f'{part}'] = part

    part_list = ['cylinder', 'sphere', 'tower']
    i = 0
    for part in rotor_dict.keys():
        rotor_dict[f'{part}'].save(f'rotor_geo/{part}.stl')
        i += 1

    return rotor_dict, cylinder, sphere, tower







blade_shell = generate_blade_mesh(blade_df, airfoil_dict)
rotor_dict, cylinder, sphere, tower = generate_rotor_geometry(blade_shell,3, 0.5, 2)
plotter = pv.Plotter()
plotter.add_mesh(cylinder)
plotter.add_mesh(sphere)
plotter.add_mesh(tower)
# plotter.add_mesh(blade_shell)
for blade in rotor_dict.values():
    plotter.add_mesh(blade)
plotter.show()