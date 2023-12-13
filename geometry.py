from cgitb import reset
import cmd
from turtle import color
from matplotlib.patches import Arc
from subprocess import PIPE, run
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os
import sys
import pyvista as pv
# from sklearn.tree import plot_tree
from sympy import li
from tenacity import retry 
import pathlib
from icecream import ic
from pathlib import Path
import settings

cwd = os.getcwd()
center = [0,0,0]

def run_cmd(command : str):
    """
    run a command and return its output
    """
    return run(
        command, 
        stdout=PIPE, 
        stderr=PIPE, 
        universal_newlines=True, 
        shell=True
    )
def nameSTLpart(name: str, file: str):
    nameStart = f'sed -i "/solid Visualization Toolkit generated SLA File/c solid {name} " {cwd}/geometry/{file}.stl'

    return nameStart

def nameSTLpart_new(name: str, path: str):
    nameStart = f'sed -i "/solid Visualization Toolkit generated SLA File/c solid {name} " {path}'

    return nameStart

def nameSTLpartEnd(name: str, file: str):
    nameEnd = f'sed -i "/endsolid/c endsolid {name} " {cwd}/geometry/{file}.stl'

    return nameEnd

def nameSTLpartEnd_new(name: str, path: str):
    nameEnd = f'sed -i "/endsolid/c endsolid {name} " {path}'

    return nameEnd

def STLtoTXT(file):
    cmd = f'cp {cwd}/geometry/{file}.stl {cwd}/geometry/{file}.txt'
    run_cmd(cmd)

def arcInletDomain(c, name):
    r = 15 * c
    w = 20 * c
    A = [center[0], r, center[2]]
    B = [w, r, center[2]]
    C = [w, -r, center[2]]
    D = [center[0], -r, center[2]]
    upperLine = pv.Line(A,B)
    outlet = pv.Line(B,C)
    lowerLine = pv.Line(C,D)
    inletArc = pv.CircularArc(D, A, center)
    domain = inletArc.merge([upperLine, lowerLine, outlet])
    domain3D = domain.extrude([0,0,1], capping=False)
    cwd = os.getcwd()
    domain3D.save('{}/geometry/{}.stl'.format(cwd,name), binary=False)

    return domain3D

def mergeFoilDomain(foilMesh, domainMesh, name):
    cwd = os.getcwd()
    domain = foilMesh.merge(domainMesh)
    domain.save('{}/geometry/{}.stl'.format(cwd,name), binary=False)
    
    return domain

def arcInlet(c, name: str):
    r = 15 * c
    A = [center[0], r, center[2]]
    D = [center[0], -r, center[2]]
    inletArc = pv.CircularArc(D, A, center)
    inletArc3D = inletArc.extrude([0,0,1], capping=False)
    inletArc3D.save('{}/geometry/{}.stl'.format(cwd,name), binary=False)
    run_cmd(nameSTLpart('Inlet', name))
    run_cmd(nameSTLpartEnd('Inlet', name))
    #STLtoTXT(name)

    return inletArc3D 

def sides(c, name: str):
    r = 15 * c
    w = 20 * c
    A = [center[0], r, center[2]]
    B = [w, r, center[2]]
    C = [w, -r, center[2]]
    D = [center[0], -r, center[2]]
    upperLine = pv.Line(A,B)
    upperLine3D = upperLine.extrude([0,0,1], capping=False)
    lowerLine = pv.Line(C,D)
    lowerLine3D = lowerLine.extrude([0,0,1], capping=False)
    sides3D = upperLine3D.merge(lowerLine3D)
    sides3D.save('{}/geometry/{}.stl'.format(cwd,name), binary=False)
    run_cmd(nameSTLpart('Sides', name))
    run_cmd(nameSTLpartEnd('Sides', name))
    #STLtoTXT(name)

    return sides3D

def outlet(c, name: str):
    r = 15 * c
    w = 20 * c
    B = [w, r, center[2]]
    C = [w, -r, center[2]]
    outlet = pv.Line(B,C)
    outlet3D = outlet.extrude([0,0,1], capping=False)
    outlet3D.save('{}/geometry/{}.stl'.format(cwd,name), binary=False)
    run_cmd(nameSTLpart('Outlet', name))
    run_cmd(nameSTLpartEnd('Outlet', name))
    #STLtoTXT(name)

    return outlet3D

# VAWT domain functions

def VAWT_line_inlet(D: float, fac_X: float, fac_Y: float, name: str):
    point_X_coord = (-1) * fac_X * D
    point_Y_coord = fac_Y * D
    upper_point = [point_X_coord, point_Y_coord, center[2]]
    lower_point = [point_X_coord, -point_Y_coord, center[2]]
    inlet = pv.Line(lower_point, upper_point)
    inlet3D = inlet.extrude([0,0,1], capping=False)
    inlet3D.save('{}/geometry/{}.stl'.format(cwd,name), binary=False)
    run_cmd(nameSTLpart('Inlet', name))
    run_cmd(nameSTLpartEnd('Inlet', name))

    return inlet3D

def VAWT_line_outlet(D: float, fac_X: float, fac_Y: float, name: str):
    point_X_coord = fac_X * D
    point_Y_coord = fac_Y * D
    upper_point = [point_X_coord, fac_Y, center[2]]
    lower_point = [point_X_coord, -fac_Y, center[2]]
    outlet = pv.Line(lower_point, upper_point)
    outlet3D = outlet.extrude([0,0,1], capping=False)
    outlet3D.save('{}/geometry/{}.stl'.format(cwd,name), binary=False)
    run_cmd(nameSTLpart('Outlet', name))
    run_cmd(nameSTLpartEnd('Outlet', name))

    return outlet3D

# def VAWT_line_sides(D: float, fac_X_in: float, fac_X_out: float, fac_Y_in: float, fac_Y_out: float, name: str):


#     return sides3D


def VAWT_domain(d: float, x_in_fac: float, x_out_fac: float, y_fac: float, name: str):
    #Generation of 3D STL model of a computational domain for VAWT simulation.
    #Domain is rectangulatr shaped with length and width in function of turbine external diameter.

    #Geometry folder preparation:
    VAWT_geom_dir = f'{cwd}/geometry/{name}/domain'
    create_VAWT_geom_dir = f'mkdir -p {VAWT_geom_dir}'
    if os.path.isdir(VAWT_geom_dir):
        print(f'{VAWT_geom_dir} <--- directory alredy exists!\nDirctory to be overwrite')
        os.system(f'rm -r {VAWT_geom_dir}')
        run_cmd(create_VAWT_geom_dir)
    else:
        run_cmd(create_VAWT_geom_dir)
    #Vertex generation:
    A = [-d*x_in_fac, d*y_fac, center[2]]
    B = [-d*x_in_fac, -d*y_fac, center[2]]
    C = [d*x_out_fac, d*y_fac, center[2]]
    D = [d*x_out_fac, -d*y_fac, center[2]]
    #Inlet generation:
    inlet = pv.Line(A, B)
    inlet3D = inlet.extrude([0,0,1], capping=False)
    inlet3D.save(f'{VAWT_geom_dir}/inlet.stl', binary=False)
    run_cmd(nameSTLpart_new('Inlet', f'{VAWT_geom_dir}/inlet.stl'))
    run_cmd(nameSTLpartEnd_new('Inlet', f'{VAWT_geom_dir}/inlet.stl'))
    #Outlet generation:
    outlet = pv.Line(C, D)
    outlet3D = outlet.extrude([0,0,1], capping=False)
    outlet3D.save(f'{VAWT_geom_dir}/outlet.stl', binary=False)
    run_cmd(nameSTLpart_new('Outlet', f'{VAWT_geom_dir}/outlet.stl'))
    run_cmd(nameSTLpartEnd_new('Outlet', f'{VAWT_geom_dir}/outlet.stl'))
    #Sides generation:
    upperLine = pv.Line(B, D)
    upperLine3D = upperLine.extrude([0,0,1], capping=False)
    lowerLine = pv.Line(C, A)
    lowerLine3D = lowerLine.extrude([0,0,1], capping=False)
    sides3D = upperLine3D.merge(lowerLine3D)
    sides3D.save(f'{VAWT_geom_dir}/sides.stl', binary=False)
    run_cmd(nameSTLpart_new('Sides', f'{VAWT_geom_dir}/sides.stl'))
    run_cmd(nameSTLpartEnd_new('Sides', f'{VAWT_geom_dir}/sides.stl'))
    #Rotor zone generation:
    rotor = pv.Circle((d*1.5)/2) #rotor zone 150% of rotor diameter
    rotor3D = rotor.extrude([0,0,1], capping=False)
    rotor3D.save(f'{VAWT_geom_dir}/rotor_zone_stationary.stl', binary=False)
    run_cmd(nameSTLpart_new('Rotor_zone_stationary', f'{VAWT_geom_dir}/rotor_zone_stationary.stl'))
    run_cmd(nameSTLpartEnd_new('Rotor_zone_stationary', f'{VAWT_geom_dir}/rotor_zone_stationary.stl'))

    #develop a function to group STL files in a ordered manner
    #by now let's do it manually
    fInlet = open(f'{VAWT_geom_dir}/inlet.stl', 'r')
    dInlet = fInlet.read()
    fInlet.close()

    fOutlet = open(f'{VAWT_geom_dir}/outlet.stl', 'r')
    dOutlet = fOutlet.read()
    fOutlet.close()

    fSides = open(f'{VAWT_geom_dir}/sides.stl', 'r')
    dSides = fSides.read()
    fSides.close()

    os.system(f'cp {VAWT_geom_dir}/rotor_zone_stationary.stl {VAWT_geom_dir}/domain_farfield.stl')

    fDomain = open(f'{VAWT_geom_dir}/domain_farfield.stl', 'a')
    fDomain.write(dInlet)
    fDomain.write(dSides)
    fDomain.write(dOutlet)
    fDomain.close()

def groupedSTLdomain(airfoil: str, inlet: str, sides: str, outlet: str):
    copyFoil = f'cp {cwd}/geometry/{airfoil}.stl {cwd}/geometry/domain_{airfoil}.stl'
    run_cmd(copyFoil)
    # Parts to save
    fInlet = open('{}/geometry/{}.stl'.format(cwd, inlet), 'r')
    dInlet = fInlet.read()
    fInlet.close()

    fSides = open('{}/geometry/{}.stl'.format(cwd, sides), 'r')
    dSides = fSides.read()
    fSides.close()

    fOutlet = open('{}/geometry/{}.stl'.format(cwd, outlet), 'r')
    dOutlet = fOutlet.read()
    fOutlet.close()

    fDomain = open('{}/geometry/domain_{}.stl'.format(cwd, airfoil), 'a')
    fDomain.write(dInlet)
    fDomain.write(dSides)
    fDomain.write(dOutlet)
    fDomain.close()

    return fDomain

def  savoniusVAWT(r: float, R1: float, R2: float, dist: float, name: str):
    cwd = os.getcwd()
    center = [0,0,0]
    VAWT_geom_dir = f'{cwd}/geometry/{name}/rotor'
    create_VAWT_geom_dir = f'mkdir -p {VAWT_geom_dir}'
    if os.path.isdir(VAWT_geom_dir):
        print(f'{VAWT_geom_dir} <--- directory alredy exists!\nDirctory to be overwrite')
        os.system(f'rm -r {VAWT_geom_dir}')
        run_cmd(create_VAWT_geom_dir)
    else:
        run_cmd(create_VAWT_geom_dir)
    #shaft
    arc1 = pv.CircularArc([0,r,0], [0,-r,0], center)
    arc2 = arc1.rotate_vector((0,0,1), 180, inplace=False)
    shaft = arc1.merge(arc2)
    # blades
    innerArc = pv.CircularArc([0,R1,0], [0,-R1,0], center)
    outerArc = pv.CircularArc([0,R2,0], [0,-R2,0], center)
    # sharp ending
    line1 = pv.Line([0,R1,0], [0,R2,0])
    line2 = pv.Line([0,-R1,0], [0,-R2,0])
    # smooth ending
    endCenterUpper = [0, R1 + (R2 - R1) / 2, 0]
    endCenterLower = [0, -R1 - (R2 - R1) / 2, 0]
    roundedEndUpper = pv.CircularArc([0,R1,0], [0,R2,0], endCenterUpper)
    roundedEndUpper = roundedEndUpper.rotate_vector((0,0,1), 180, inplace=False)
    roundedEndLower = pv.CircularArc([0,-R1,0], [0,-R2,0], endCenterLower)
    roundedEndLower = roundedEndLower.rotate_vector((0,0,1), 180, inplace=False)
    # merging
    bladeUpper = innerArc.merge([outerArc, roundedEndUpper, roundedEndLower])
    bladeLower = bladeUpper.rotate_vector((0,0,1), 180, inplace=False)
    bladeUpper = bladeUpper.translate([0,R1 - dist,0])
    bladeLower = bladeLower.translate([0,-R1 + dist,0])
    VAWT = shaft.merge([bladeUpper, bladeLower])
    VAWT3D = VAWT.extrude([0,0,1], capping=False)
    cwd = os.getcwd()
    VAWT3D.save(f'{VAWT_geom_dir}/rotor.stl', binary=False)
    run_cmd(nameSTLpart_new('Rotor', f'{VAWT_geom_dir}/rotor.stl'))
    run_cmd(nameSTLpartEnd_new('Rotor', f'{VAWT_geom_dir}/rotor.stl'))
    #Rotor zone generation:
    rotor = pv.Circle(2*R2*1.5) #rotor zone 150% of rotor diameter
    rotor3D = rotor.extrude([0,0,1], capping=False)
    rotor3D.save(f'{VAWT_geom_dir}/rotor_zone_moving.stl', binary=False)
    run_cmd(nameSTLpart_new('Rotor_zone_moving', f'{VAWT_geom_dir}/rotor_zone_moving.stl'))
    run_cmd(nameSTLpartEnd_new('Rotor_zone_moving', f'{VAWT_geom_dir}/rotor_zone_moving.stl'))
    #develop a function to group STL files in a ordered manner
    #by now let's do it manually
    fRotorZone = open(f'{VAWT_geom_dir}/rotor_zone_moving.stl', 'r')
    dRotorZone = fRotorZone.read()
    fRotorZone.close()

    os.system(f'cp {VAWT_geom_dir}/rotor.stl {VAWT_geom_dir}/domain_rotor.stl')

    fDomain = open(f'{VAWT_geom_dir}/domain_rotor.stl', 'a')
    fDomain.write(dRotorZone)
    fDomain.close()

def darrieusVAWT(name: str, foil, r, R, n):
    center = [0,0,0]
    # shaft
    arc1 = pv.CircularArc([0,r,0], [0,-r,0], center)
    arc2 = arc1.rotate_vector((0,0,1), 180, inplace=False)
    shaft = arc1.merge(arc2)

    foil = foil.translate([0,R,0])
    step = 360 / n
    blades = foil
    # for i in range(n):
    #     rot = foil.rotate_z(step * i, point=center, inplace=False)
    #     blades = blades.merge(rot)
    
    foil_merged = foil #nie działa. Znika element bazowy
    for i in range(n):
        foil1 = foil.rotate_vector((0,0,1), i * step, inplace=False)
        foil_merged = foil_merged.merge(foil1)

    foil_merged=foil_merged.merge(foil)
    # merging 
    # VAWT = shaft.merge(blades)
    # VAWT3D = VAWT.extrude([0,0,1], capping=False)
    VAWT = shaft.merge(foil_merged)
    VAWT3D = VAWT.extrude([0,0,1], capping=False)
    cwd = os.getcwd()
    #VAWT3D.save('{}/geometry/{}.stl'.format(cwd,name, binary=False)  

    return VAWT3D 

def generate_circular_airfoil(r: float, resolution: int):
    circular_foil_df = pd.DataFrame()
    circular_foil_df['deg'] = np.linspace(0,360,resolution)
    circular_foil_df['rad'] = np.deg2rad(circular_foil_df['deg'])
    circular_foil_df['X'] = np.cos(circular_foil_df['rad']) * r + settings.c / 2
    circular_foil_df['Y'] = np.sin(circular_foil_df['rad']) * r
    circular_foil_df['Z'] = 0

    return circular_foil_df

# def generate_blade_mesh(blade_df,airfoil_dict):
#     # Generates blade mesh in .stl format
#     # Requires: 
#     # blade_df -> data frame with general blade information: position of an airfoil, chord, twist, airfoil name
#     # airfoil_dict -> dictionary containing data frames with coordinates for every airfoil used in a blade
#     blade_mesh = pv.PolyData()
#     for index, column in blade_df.iterrows():
#         foil = blade_df.loc[index].at['airfoil']

#         for foil in airfoil_dict.keys():
#             airfoil_df = airfoil_dict[f'{foil}']
#             airfoil_mesh = pv.PolyData(np.column_stack((airfoil_df['X'],airfoil_df['Y'],airfoil_df['Z'])))
#             airfoil_mesh_element_scaled = airfoil_mesh.scale([blade_df.loc[index].at['c'],blade_df.loc[index].at['c'],1])
#             airfoil_mesh_element_rotated = airfoil_mesh_element_scaled.rotate_z(blade_df.loc[index].at['twist'] ,point = [0.5,0,0])
#             airfoil_mesh_element_translated = airfoil_mesh_element_rotated.translate([0,0,[blade_df.loc[index].at['pos']][0]])
#             blade_mesh = blade_mesh.merge(airfoil_mesh_element_translated)
   
#     blade_volume = blade_mesh.delaunay_3d(alpha=3, tol=0.5, offset=2.5, progress_bar=True)
#     blade_shell = blade_volume.extract_surface(pass_pointid=False, pass_cellid=False)

#     return blade_shell

def generate_blade_mesh(blade_df,airfoil_dict, path):
    # Generates blade mesh in .stl format
    # Requires: 
    # blade_df -> data frame with general blade information: position of an airfoil, chord, twist, airfoil name
    # airfoil_dict -> dictionary containing data frames with coordinates for every airfoil used in a blade

    blade_mesh = pv.PolyData()
    scale_factor = 5
    # plot = pv.Plotter() ## -> activate for plotting

    # Scalling foil data frames
    for foil_df in airfoil_dict.values():
        foil_df['X'] = foil_df['X'] * scale_factor
        foil_df['Y'] = foil_df['Y'] * scale_factor
    # Starting blade element generation 
    for index, column in blade_df.iterrows():

        foil = blade_df.loc[index].at['airfoil'] 
        airfoil_df = airfoil_dict[f'{foil}']
        airfoil_mesh = pv.PolyData(np.column_stack((airfoil_df['X'],airfoil_df['Y'],airfoil_df['Z'])))
        te_mesh = pv.PolyData(pv.CircularArc(
            [airfoil_df['X'].iloc[-1],airfoil_df['Y'].iloc[-1],0],
            [airfoil_df['X'].iloc[-1],airfoil_df['Y'].iloc[-1] * (-1),0],
            [airfoil_df['X'].iloc[-1],0,0], resolution=20, negative=True))
        # airfoil_mesh = airfoil_mesh.merge(te_mesh)
        
        if foil != 'circular':
            airfoil_mesh_element_scaled = airfoil_mesh.scale([blade_df.loc[index].at['c'],blade_df.loc[index].at['c'],1])
            airfoil_mesh_element_rotated = airfoil_mesh_element_scaled.rotate_z(blade_df.loc[index].at['twist'] ,point = [(airfoil_df['X'].iloc[1] + airfoil_df['X'].iloc[-1]) / 2,0,0])
        else:
            airfoil_mesh_element_scaled = airfoil_mesh.scale([1,blade_df.loc[index].at['c'],1], inplace=True)
            airfoil_mesh_element_rotated = airfoil_mesh_element_scaled

        airfoil_mesh_element_translated = airfoil_mesh_element_rotated.translate([0,0,[blade_df.loc[index].at['pos']][0] * scale_factor]) 
        blade_mesh = blade_mesh.merge(airfoil_mesh_element_translated)
        # plot.add_mesh(airfoil_mesh_element_translated, color=blade_df['color'].iloc[index], label=f'{index}: {foil}') ## plotting final elements fo the blade for debbuing

    # Final operations: blade generation and saving
    blade_volume = blade_mesh.delaunay_3d(alpha=3, tol=1e-12, offset=2.5, progress_bar=True)
    blade_shell = blade_volume.extract_surface(pass_pointid=False, pass_cellid=False)
    blade_shell = blade_shell.scale(1/scale_factor,1/scale_factor,1)
    blade_shell.save(f'{path}/blade.stl')
    # plot.add_legend() ## -> activate for plotting
    # plot.show() ## -> activate for plotting

    return blade_shell

def generate_turbine_geometry(path: str,blade_shell, n: int,r_hub: float, L_hub: float, r_tower: float, H_tower: float):
    # Generates rotor mesh in .stl format
    # Requires:
    # blade_shell -> surface ot a blade obtained from generate_blade_mesh() function
    # n -> number of blades, r_hub -> radius of a hub, L_hub -> lenght of a hub, r_tower -> radius of a tower, H_tower -> height of a tower
    # os.system(f'mkdir -p {pwd}/geometry/{name}')
    # Rotor generation 
    rotor_dict = {}
    blade_shell = blade_shell.rotate_z(180, point=[0.5,0,0])
    for blade in np.arange(0,360,360/n):
        rotor_dict[f'blade{int(blade)}'] = blade_shell.rotate_x(blade, point=[0.5,0,0])
    rotor = rotor_dict['blade0']
    for i, key in enumerate(rotor_dict.keys()):
        if i > 0:
            rotor = rotor.merge(rotor_dict[f'{key}'])
    rotor_bounds = rotor.bounds
    # Tower generation
    tower_base1 = pv.Circle(radius=r_tower)
    tower_base2 = tower_base1.translate([0,0,-H_tower])
    tower_tube = pv.Tube(pointa=(0,0,0), pointb=(0,0,-H_tower),resolution=H_tower*10,radius=r_tower,n_sides=100)
    tower = tower_base1.merge([tower_base2, tower_tube])
    # Hub generation
    hub_base = pv.Circle(radius=r_hub, resolution=100)
    hub_tube = pv.Tube(pointa=(0,0,0), pointb=(0,0,L_hub),resolution=L_hub*10,radius=r_hub,n_sides=100)
    hub_dome = pv.Sphere(center=[0,0,L_hub], direction=[0,0,-1], radius=r_hub, end_phi=90, theta_resolution=100)
    hub = hub_base.merge([hub_dome, hub_tube])
    hub = hub.rotate_y(90, point=[0,0,0])
    hub = hub.translate([-L_hub/2,0,0])

    #Saving operations
    turbine = rotor.merge([tower, hub])
    turbine_dict = {
        'rotor': rotor,
        'tower': tower,
        'hub': hub,
        'turbine': turbine
    }
    for key, value in turbine_dict.items():
        value.save(f'{path}/{key}.stl')

    return turbine, rotor_bounds

def generete_AMI_HAWT_cylinder(path: str, R: int, rotor_bounds: list):
    # Generetes a cylinder in .stl format that is later used for splitting mesh into stationary and moving zones
    # Requires: R -> wind turbine rotor radius, rotor_bounds -> list of a max and min X,Y,Z coordinates of a rotor
    rotor_domain = pv.Cylinder(center=[0,0,0], direction=[1,0,0], radius=R*1.5, height=2) #(rotor_bounds[1]-rotor_bounds[0])*3)
    rotor_domain = rotor_domain.translate([1,0,0])
    rotor_domain.save(f'{path}/rotor_domain.stl')

    return rotor_domain

