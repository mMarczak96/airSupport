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





# def group_STL_domain(STL_list: list, path: str):
#     print(f'Components of the computational domain: {STL_list}')
#     #Reading STL components
#     STL_dict = {}
#     STL_part_list = []
#     for part in STL_list:
#         print(f'processing part {part}')
#         STL_dict[f'f{part}'] = open(f'{path}/{part}.stl', 'r')
#         STL_list_element = list(STL_dict.keys())[-1]
#         ic(STL_list_element)
#         STL_part_list.append(STL_list_element)
#         # element = Path(f'{path}/{STL_part_list[-1]}.stl')
#         # ic(element)
#         STL_dict[f'd{part}'] = element.read()
#         STL_dict.keys()[-2].close()
     
#     print(STL_dict)
#     print(STL_list)

abc = ['inlet', 'outlet', 'sides', 'rotor']


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

# def regionSTLgen (STL_lst: list):
#     for i in STL_lst:



