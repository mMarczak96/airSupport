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
blade_df['pos'] = np.arange(0,3.01,1)
blade_df['c'] = np.array([1,1,1,1])
blade_df['twist'] = np.array([0,0,0,0])
blade_df['airfoil'] = np.array(['NACA0010', 'NACA0010', 'NACA0015','NACA0050'])
# blade_df.to_csv('initial_data/blade_df.csv')
#Airfoil data
airfoil_dict ={}
te_dict = {}
for T in [0.20, 0.10]:
    A = 0.0
    Naca = Airfoil('NACA0015', A, T, settings.N)
    plus = Naca.foil_cords_plus(A, T, settings.N)
    min = Naca.foil_cords_min(A, T, settings.N)
    # te = Naca.roundedTE(settings.NT, settings.ST, settings.ET, plus)
    airoifl_df = pd.concat([plus,min])
    airfoil_dict[f'NACA00{int(T*100)}'] = airoifl_df
    

airfoil_dict['circular'] = geom.generate_circular_airfoil(0.25,220)

#Only TE generation



# def generate_blade_mesh(blade_df,airfoil_dict):
#     # Generates blade mesh in .stl format
#     # Requires: 
#     # blade_df -> data frame with general blade information: position of an airfoil, chord, twist, airfoil name
#     # airfoil_dict -> dictionary containing data frames with coordinates for every airfoil used in a blade
#     blade_mesh = pv.PolyData()
#     for index, column in blade_df.iterrows():
#         foil = blade_df.loc[index].at['airfoil']
#         print(foil)
#         for key, value in airfoil_dict.items():
#             print(key)
#             print(foil)
#             airfoil_df = airfoil_dict[f'{key}']
#             airfoil_mesh = pv.PolyData(np.column_stack((airfoil_df['X'],airfoil_df['Y'],airfoil_df['Z'])))
#             airfoil_mesh_element_scaled = airfoil_mesh.scale([blade_df.loc[index].at['c'],blade_df.loc[index].at['c'],1])
#             airfoil_mesh_element_rotated = airfoil_mesh_element_scaled.rotate_z(blade_df.loc[index].at['twist'] ,point = [0.5,0,0])
#             airfoil_mesh_element_translated = airfoil_mesh_element_rotated.translate([0,0,[blade_df.loc[index].at['pos']][0]])
#             blade_mesh = blade_mesh.merge(airfoil_mesh_element_translated)
   
#     blade_volume = blade_mesh.delaunay_3d(alpha=3, tol=0.5, offset=2.5, progress_bar=True)
#     blade_shell = blade_volume.extract_surface(pass_pointid=False, pass_cellid=False)

#     return blade_shell4

def generate_blade_mesh(blade_df,airfoil_dict, path):
    # Generates blade mesh in .stl format
    # Requires: 
    # blade_df -> data frame with general blade information: position of an airfoil, chord, twist, airfoil name
    # airfoil_dict -> dictionary containing data frames with coordinates for every airfoil used in a blade
    blade_mesh = pv.PolyData()
    plotter = pv.Plotter()
    for index, column in blade_df.iterrows():
        foil = blade_df.loc[index].at['airfoil']
       
        airfoil_df = airfoil_dict[f'{foil}']
        airfoil_mesh = pv.PolyData(np.column_stack((airfoil_df['X'],airfoil_df['Y'],airfoil_df['Z'])))
        if foil != 'circular':
            airfoil_mesh_element_scaled = airfoil_mesh.scale([blade_df.loc[index].at['c'],blade_df.loc[index].at['c'],1])
        else:
            airfoil_mesh_element_scaled = airfoil_mesh.scale([1,blade_df.loc[index].at['c'],1], inplace=True)
        if foil != 'circular':
            airfoil_mesh_element_rotated = airfoil_mesh_element_scaled.rotate_z(blade_df.loc[index].at['twist'] ,point = [0.5,0,0])
        else:
            airfoil_mesh_element_rotated = airfoil_mesh_element_scaled

        plotter.add_mesh(airfoil_mesh_element_rotated)
        
        airfoil_mesh_element_translated = airfoil_mesh_element_rotated.translate([0,0,[blade_df.loc[index].at['pos']][0]])
        blade_mesh = blade_mesh.merge(airfoil_mesh_element_translated)
    # plotter.show()
    blade_volume = blade_mesh.delaunay_3d(alpha=3, tol=0.5, offset=2.5, progress_bar=True)
    blade_shell = blade_volume.extract_surface(pass_pointid=False, pass_cellid=False)
    blade_shell.save(path)

    return blade_shell

def generate_blade_mesh_new(blade_df,airfoil_dict, path):
    # Generates blade mesh in .stl format
    # Requires: 
    # blade_df -> data frame with general blade information: position of an airfoil, chord, twist, airfoil name
    # airfoil_dict -> dictionary containing data frames with coordinates for every airfoil used in a blade
    blade_mesh = pv.PolyData()
    scale_factor = 100
    for index, column in blade_df.iterrows():
        plot = pv.Plotter()
        foil = blade_df.loc[index].at['airfoil'] 
        airfoil_dict[foil]['X'] = airfoil_dict[foil]['X'] * scale_factor
        airfoil_dict[foil]['Y'] = airfoil_dict[foil]['Y'] * scale_factor
        # airfoil_dict[foil]['X'] = airfoil_dict[foil]['X']
        # airfoil_dict[foil]['Y'] = airfoil_dict[foil]['Y']
        airfoil_df = airfoil_dict[f'{foil}'] 
        # airfoil_df['X'] = airfoil_df['X'] * scale_factor 
        # airfoil_df['Y'] = airfoil_df['Y'] * scale_factor 
        airfoil_mesh = pv.PolyData(np.column_stack((airfoil_df['X'],airfoil_df['Y'],airfoil_df['Z'])))
        te_mesh = pv.PolyData(pv.CircularArc(
            [airfoil_df['X'].iloc[-1],airfoil_df['Y'].iloc[-1],0],
            [airfoil_df['X'].iloc[-1],airfoil_df['Y'].iloc[-1] * (-1),0],
            [airfoil_df['X'].iloc[-1],0,0], resolution=20, negative=True))
        airfoil_mesh = airfoil_mesh.merge(te_mesh)
        plot.add_mesh(airfoil_mesh, color='red')
        # plot.show()
        
        if foil != 'circular':
            airfoil_mesh_element_scaled = airfoil_mesh.scale([blade_df.loc[index].at['c'],blade_df.loc[index].at['c'],1])
            airfoil_mesh_element_rotated = airfoil_mesh_element_scaled.rotate_z(blade_df.loc[index].at['twist'] ,point = [(airfoil_df['X'].iloc[1] + airfoil_df['X'].iloc[-1]) / 2,0,0])
        else:
            airfoil_mesh_element_scaled = airfoil_mesh.scale([1,blade_df.loc[index].at['c'],1], inplace=True)
            airfoil_mesh_element_rotated = airfoil_mesh_element_scaled

        airfoil_mesh_element_translated = airfoil_mesh_element_rotated.translate([0,0,[blade_df.loc[index].at['pos']][0] * scale_factor])
        blade_mesh = blade_mesh.merge(airfoil_mesh_element_translated)
        # plot.add_mesh(airfoil_mesh_element_translated, color='black')
        # plot.add_mesh(blade_mesh)
    blade_volume = blade_mesh.delaunay_3d(alpha=3, tol=1e-12, offset=2.5, progress_bar=True)
    blade_shell = blade_volume.extract_surface(pass_pointid=False, pass_cellid=False)
    blade_shell = blade_shell.scale(1/scale_factor,1/scale_factor,1)
    # plot.add_mesh(blade_shell)
    blade_shell.save(f'{path}/blade.stl')
    # plot.show()

    return blade_shell

def generete_blade_trailing_edge(blade_df,airfoil_dict, path):
    te_mesh = pv.PolyData()
    plotter = pv.Plotter()
    airfoil_dict['NACA0010']['X'] = airfoil_dict['NACA0010']['X'] * 100
    airfoil_dict['NACA0010']['Y'] = airfoil_dict['NACA0010']['Y'] * 100

    for index, column in blade_df.iterrows():
        foil = blade_df.loc[index].at['airfoil']
        airfoil_df = airfoil_dict[f'{foil}']
        print(airfoil_df)
        te_mesh = pv.PolyData(pv.CircularArc(
           [airfoil_df['X'].iloc[-1],airfoil_df['Y'].iloc[-1],0],
           [airfoil_df['X'].iloc[-1],airfoil_df['Y'].iloc[-1] * (-1),0],
           [airfoil_df['X'].iloc[-1],0,0], resolution=100))

        te_mesh_element_scaled = te_mesh.scale([blade_df.loc[index].at['c'],blade_df.loc[index].at['c'],1])
        te_mesh_element_rotated = te_mesh_element_scaled.rotate_z(blade_df.loc[index].at['twist'] ,point = [0.5,0,0])
        te_mesh_element_translated = te_mesh_element_rotated.translate([0,0,[blade_df.loc[index].at['pos']][0]])
        te_mesh = te_mesh.merge(te_mesh_element_translated)
        # plotter.add_mesh(te_mesh)
    
    te_volume = te_mesh.delaunay_3d(alpha=3, tol=0.5, offset=2.5, progress_bar=True)
    te_shell = te_volume.extract_surface(pass_pointid=False, pass_cellid=False)
    plotter.add_mesh(te_volume)
    plotter.show()
    te_shell.save(path)

    point_A = [airfoil_df['X'].iloc[-1],airfoil_df['Y'].iloc[-1],0]
    # point_B = [airfoil_df['X'].iloc[-1] + airfoil_df['Y'].iloc[-1],0,0]
    point_B = [airfoil_df['X'].iloc[-1],airfoil_df['Y'].iloc[-1] * (-1),0]
    center = [airfoil_df['X'].iloc[-1],0,0]
    arc = pv.CircularArc(point_A, point_B, center)
    arc_mesh = pv.PolyData(arc)
    pl = pv.Plotter()
    _ = pl.add_mesh(arc_mesh)
    _ = pl.show_bounds(location='all', font_size=5, use_2d=True)
    _ = pl.view_xy()
    # _ = pl.add_mesh(arc, color='k', line_width=10)
    pl.show()


def generate_turbine_geometry(path: str,blade_shell, n: int,r_hub: float, L_hub: float, r_tower: float, H_tower: float):
    # Generates rotor mesh in .stl format
    # Requires:
    # blade_shell -> surface ot a blade obtained from generate_blade_mesh() function
    # n -> number of blades, r_hub -> radius of a hub, L_hub -> lenght of a hub, r_tower -> radius of a tower, H_tower -> height of a tower
    # os.system(f'mkdir -p {pwd}/geometry/{name}')
    # Rotor generation 
    rotor_dict = {}
    blade_shell = blade_shell.rotate_z(180, point=[0.5,0,0])
    blade_shell = blade_shell.translate([1,0, r_hub/2])
    for blade in np.arange(0,360,360/n):
        rotor_dict[f'blade{int(blade)}'] = blade_shell.rotate_x(blade, point=[0.5,0,0])
    rotor = rotor_dict['blade0']
    for i, key in enumerate(rotor_dict.keys()):
        if i > 0:
            rotor = rotor.merge(rotor_dict[f'{key}'])
    rotor = rotor.triangulate()
    rotor_bounds = rotor.bounds
    # Tower generation
    tower_base1 = pv.Circle(radius=r_tower)
    tower_base2 = tower_base1.translate([0,0,-H_tower])
    tower_tube = pv.Tube(pointa=(0,0,0), pointb=(0,0,-H_tower),resolution=H_tower*10,radius=r_tower,n_sides=100)
    tower = tower_base1.merge([tower_base2, tower_tube]).triangulate()
    # Hub generation
    hub_base = pv.Circle(radius=r_hub, resolution=100)
    hub_tube = pv.Tube(pointa=(0,0,0), pointb=(0,0,L_hub),resolution=L_hub*10,radius=r_hub,n_sides=100)
    hub_dome = pv.Sphere(center=[0,0,L_hub], direction=[0,0,-1], radius=r_hub, end_phi=90, theta_resolution=100)
    hub = hub_base.merge([hub_dome, hub_tube]).triangulate()
    hub = hub.rotate_y(90, point=[0,0,0])
    hub = hub.translate([-L_hub/2,0,0])
    print(type(rotor))
    #Saving operations
    # turbine = rotor.boolean_union([tower, hub])
    turbine = tower.boolean_union(hub)
    turbine = turbine.boolean_union(rotor)
    turbine_dict = {
        'rotor': rotor,
        'tower': tower,
        'hub': hub,
        'turbine': turbine
    }
    for key, value in turbine_dict.items():
        value.save(f'{path}/{key}.stl')

    return turbine, rotor_bounds

# blade_shell = generate_blade_mesh(blade_df, airfoil_dict)
# generate_turbine_geometry('test_turbine',blade_shell,3, 0.5, 2, 0.5, 10)



