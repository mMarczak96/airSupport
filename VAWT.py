from cgitb import reset
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

class VAWT:

# TODO: 
# 1. implement domain creation 
# 2. implement simulation template 
# 3. implement simulation automatisation 
# 4. implement simulation postprocessing 


    name = ""
    n = None #Number of blades
    D = None #Outer diamater of the VAWT [m]
    d = None #Schaft diameter [m]
    mode = None # Rotational model of the analysis [sliding, MRF]
    

    def __init__(self, name: str, D: float, d: float, mode: str):
        self.name = name 
        self.D = D
        self.d = d
        self.mode = mode
    

    
    
class Savonius(VAWT):

    # TODO: 
    # ---

    d_i = None #Inner dimateter of the VAWT [m]
    dist = None #Blades move distamce from the center [m]

    def __init__(self, name: str, D: float, d: float, mode: str, d_i: float, dist: float):
        super().__init__(name, D, d, mode)
        self.d_i = d_i
        self.dist = dist
    
    #TEST FUNCTION
    def test(self, text):
        print(text)

    # Geometry Creation
    def Savonius_geom(self, name: str, d: float, d_i: float, D: float, dist: float):

        center = [0,0,0]
        #shaft
        arc1 = pv.CircularArc([0,d/2,0], [0,-d/2,0], center)
        arc2 = arc1.rotate_vector((0,0,1), 180, inplace=False)
        shaft = arc1.merge(arc2)
        # blades
        innerArc = pv.CircularArc([0,d_i/2,0], [0,-d_i/2,0], center)
        outerArc = pv.CircularArc([0,D/2,0], [0,-D/2,0], center)
        # sharp ending
        line1 = pv.Line([0,d_i/2,0], [0,D/2,0])
        line2 = pv.Line([0,-d_i/2,0], [0,-D/2,0])
        # smooth ending
        endCenterUpper = [0, d_i/2 + (D/2 - d_i/2) / 2, 0]
        endCenterLower = [0, -d_i/2 - (D/2 - d_i/2) / 2, 0]
        roundedEndUpper = pv.CircularArc([0,d_i/2,0], [0,D/2,0], endCenterUpper)
        roundedEndUpper = roundedEndUpper.rotate_vector((0,0,1), 180, inplace=False)
        roundedEndLower = pv.CircularArc([0,-d_i/2,0], [0,-D/2,0], endCenterLower)
        roundedEndLower = roundedEndLower.rotate_vector((0,0,1), 180, inplace=False)
        # merging
        bladeUpper = innerArc.merge([outerArc, roundedEndUpper, roundedEndLower])
        bladeLower = bladeUpper.rotate_vector((0,0,1), 180, inplace=False)
        bladeUpper = bladeUpper.translate([0,d_i/2 - dist,0])
        bladeLower = bladeLower.translate([0,-d_i/2 + dist,0])
        VAWT = shaft.merge([bladeUpper, bladeLower])
        VAWT3D = VAWT.extrude([0,0,1], capping=False)
        cwd = os.getcwd()
        VAWT3D.save('{}/geometry/{}.stl'.format(cwd,name), binary=False)

        return VAWT3D


    

class  Darrieus(VAWT):

    # TODO: 
    # 1. add geometry creation function -> geometry.py

    airfoil = None #Probably airfoil coordinates, or maybe STL

    def __init__(self, name, D, d, mode, airfoil):
        super().__init__(name, D, d, mode)
        self.airfoil = airfoil
    
    #TEST FUNCTION
    def test(self, text):
        print(text)
    
    # Geometry Creation
    def Darrieus_geom(self, foil, d, D, n: int):

        center = [0,0,0]
        # shaft
        arc1 = pv.CircularArc([0,d/2,0], [0,-d/2,0], center)
        arc2 = arc1.rotate_vector((0,0,1), 180, inplace=False)
        shaft = arc1.merge(arc2)

        foil = foil.translate([0,D/2,0])
        step = 360 / n
        blades = foil
 
        foil_merged = foil #nie działa. Znika element bazowy
        for i in range(n):
            foil1 = foil.rotate_vector((0,0,1), i * step, inplace=False)
            foil_merged = foil_merged.merge(foil1)

        foil_merged=foil_merged.merge(foil)
        VAWT = shaft.merge(foil_merged)
        VAWT3D = VAWT.extrude([0,0,1], capping=False)
        cwd = os.getcwd()
        #VAWT3D.save('{}/geometry/{}.stl'.format(cwd,name, binary=False)  

        return VAWT3D 





    