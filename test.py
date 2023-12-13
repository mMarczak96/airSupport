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
import mesh     

# mesh.create_HAWT_tunel_blockMeshDict('templates/template_HAWT/system/blockMeshDict', 10, 15, 10, 20, 10)

plot = pv.Plotter()
cylinder1 = pv.Cylinder(height=3).triangulate()
cylinder2 = pv.Cylinder(direction=(0,1,0), height=3).triangulate()
union = cylinder1.boolean_union(cylinder2)

# plot.add_mesh(cylinder1, color='red', opacity=0.5)
# plot.add_mesh(cylinder2, color='green', opacity=0.5)
plot.add_mesh(union,style='wireframe')
plot.show()

'''
z = 0
p1 = [0,0,z]
p2 = [0.5, -0.5, z]
p3 = [1, 0, z]
p4 = [0.5, 0.5, z]
z = 1
p5 = [0,0,z]
p6 = [0.5, -0.5, z]
p7 = [1, 0, z]
p8 = [0.5, 0.5, z]

point_list = [p1,p2,p3,p4,p5,p6,p7,p8]
# cube_cloud = pv.PolyData(point_list)
# volume = cube_cloud.delaunay_3d(alpha=3, tol=0.5, offset=2.5, progress_bar=True)
# shell = volume.extract_surface(pass_pointid=False, pass_cellid=False)
line_dict = {}
for i in [0,1,2,3]:
    line_dict[f'line{i}'] = pv.Line(point_list[i], point_list[i+4])

mesh = line_dict['line1']
# mesh = pv.Line((0,0,0), (0,0,1))
# mesh.plot(color='k', line_width=10)

rec1 = pv.Rectangle([p1,p2,p3, p4])
rec2 = pv.Rectangle([p5,p6,p7,p8])

# plotter = pv.Plotter()
# plotter.add_mesh(rec1)
# # plotter.add_mesh(rec2)
rec2_rot = rec2.rotate_z(3, point=[0.5,0,0])
# plotter.add_mesh(rec2_rot)
# for line in line_dict.values():
#     plotter.add_mesh(line)
# # plotter.show()

rec1_points = pv.PolyData(rec1)
boundary1 = rec1_points.extract_feature_edges(boundary_edges=True, 
                                      non_manifold_edges=False, 
                                      manifold_edges=False)
print(boundary1.points)

rec2_points = pv.PolyData(rec2_rot)
boundary2 = rec2_points.extract_feature_edges(boundary_edges=True, 
                                      non_manifold_edges=False, 
                                      manifold_edges=False)
print(boundary2.points)


# line_dict = {}
# for i in [0,1,2,3]:
#     line_dict[f'line{i}'] = pv.Line(boundary1.points[i],boundary2.points[i])

rec_dict = {}
for i in [0,1,2,3]:
    if i <= 2:
        line_dict[f'line{i}'] = pv.Rectangle([boundary1.points[i],boundary1.points[i+1],boundary2.points[i+1],boundary2.points[1]])
    else:
        line_dict[f'line{i}'] = pv.Rectangle([boundary1.points[i],boundary1.points[i-i],boundary2.points[i],boundary2.points[i-i]])

point_list = [p1,p2,p3,p4,boundary2.points[0],boundary2.points[1],boundary2.points[2],boundary2.points[3]]
cube_cloud = pv.PolyData(point_list)
volume = cube_cloud.delaunay_3d(alpha=3, tol=0.5, offset=2.5, progress_bar=True)
shell = volume.extract_surface(pass_pointid=False, pass_cellid=False)

# plotter = pv.Plotter()
# plotter.add_mesh(shell)
# plotter.add_mesh(rec1)
# plotter.add_mesh(rec2_rot)
# for line in line_dict.values():
#     plotter.add_mesh(line)
# plotter.add_mesh(line_dict['line1'])
# plotter.show()

## Airfoil coordinates:
A = 0.0
T = 0.15
Naca = Airfoil('NACA0015', A, T, settings.N)
plus = Naca.foil_cords_plus(A, T, settings.N)
min = Naca.foil_cords_min(A, T, settings.N)
te = Naca.roundedTE(settings.NT, settings.ST, settings.ET, plus)

airoifl_df = pd.concat([plus,min,te])
x_airfoil = airoifl_df['X']
y_airfoil = airoifl_df['Y']
z_airfoil = airoifl_df['Z']
airfoil_mesh = pv.PolyData(np.column_stack((x_airfoil,y_airfoil,z_airfoil)))
## Blade data:
n_blades = 3
radius = 1
blade_df = pd.DataFrame()
blade_df['pos'] = np.arange(0,10,1)
blade_df['c'] = np.array([1,1,1,0.9,0.8,0.7,0.6,0.5,0.4,0.3])
# blade_df['twist'] = np.ones(10)
blade_df['twist'] = np.array([0,0,5,10,15,20,25,30,35,40])

print(blade_df)

blade_mesh = pv.PolyData()
for index, row in blade_df.iterrows():

    airfoil_mesh_element_scaled = airfoil_mesh.scale([blade_df.loc[index].at['c'],blade_df.loc[index].at['c'],1])
    airfoil_mesh_element_rotated = airfoil_mesh_element_scaled.rotate_z(blade_df.loc[index].at['twist'] ,point = [0.5,0,0])
    airfoil_mesh_element_translated = airfoil_mesh_element_rotated.translate([0,0,[blade_df.loc[index].at['pos']][0]])
    blade_mesh = blade_mesh.merge(airfoil_mesh_element_translated)

blade_volume = blade_mesh.delaunay_3d(alpha=3, tol=0.5, offset=2.5, progress_bar=True)
blade_shell = blade_volume.extract_surface(pass_pointid=False, pass_cellid=False)
blade_dict = {}
for blade in [0, 120, 240]:
    blade_dict[f'blade{blade}'] = blade_shell.rotate_x(blade, point=[0.5,0,0])

# airfoil_mesh = pv.PolyData(np.column_stack((x_airfoil,y_airfoil,z_airfoil)))
# airfoil_mesh_extruded = airfoil_mesh.translate([0,0,radius])
# blade_mesh = airfoil_mesh.merge(airfoil_mesh_extruded)


plotter = pv.Plotter()
# plotter.add_mesh(airfoil_mesh, color='red')
# plotter.add_mesh(airfoil_mesh_extruded, color='green')
plotter.add_mesh(blade_mesh, color='black')
plotter.add_mesh(blade_shell)
for blade in blade_dict.values():
    plotter.add_mesh(blade)
# plotter.show()

i = 1
for blade in blade_dict.keys():
    blade_dict[f'{blade}'].save(f'blade_{i}.stl')
    i += 1

def generate_blade_mesh(blade_df,airfoil_dict):
    # Generates blade mesh in .stl format
    # Requires: 
    # blade_df -> data frame with general blade information: position of an airfoil, chord, twist, airfoil name
    # airfoil_dict -> dictionary containing data frames with coordinates for every airfoil used in a blade

    for index, column in blade_df.iterrow():
        print(f'index {index}, column {column}')


    return 

'''