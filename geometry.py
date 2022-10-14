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
from sklearn.tree import plot_tree
from sympy import li
from tenacity import retry 
import pathlib

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

def nameSTLpartEnd(name: str, file: str):
    nameEnd = f'sed -i "/endsolid/c endsolid {name} " {cwd}/geometry/{file}.stl'

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

def  savoniusVAWT(name, r, R1, R2, dist):
    center = [0,0,0]
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
    VAWT3D.save('{}/geometry/{}.stl'.format(cwd,name), binary=False)

    return VAWT3D

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



