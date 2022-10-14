from asyncio import subprocess
from cgitb import reset
from telnetlib import NAOVTD
from subprocess import PIPE, run
from traceback import print_tb
from turtle import filling
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
def parse_args():
    parser = argparse.ArgumentParser()
    cwd = os.getcwd()

    parser.add_argument('-f', '--foil', help='airfoil code', required=True)                                  
    parser.add_argument('-a', '--actions', nargs='+',help='Actions type [foil]', required=True,)
    args = parser.parse_args()

    return args

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

cwd = os.getcwd()

if __name__ == '__main__':
    
    args = parse_args()
    foil = args.foil
    actions = args.actions

    for action in actions:

        if action == 'foil':
            Naca = Airfoil('NACA{}'.format(foil), settings.A, settings.T, settings.N)

            plus = Naca.foil_cords_plus(settings.A, settings.T, settings.N)
            min = Naca.foil_cords_min(settings.A, settings.T, settings.N)
            te = Naca.roundedTE(settings.NT, settings.ST, settings.ET, plus)
            cords = Naca.mergeFoilPts(plus, min, te)
            Naca.create_STL_foil(cords)
            c=1
            geom.sides(c, 'Sides')
            geom.arcInlet(c, 'Inlet')
            geom.outlet(c, 'Outlet')
            geom.groupedSTLdomain('NACA0018','Inlet','Sides','Outlet')
            copyOFtemp = f'cp -r {cwd}/template {cwd}/run'
            changeOFdir = f'mv {cwd}/run/template {cwd}/run/NACA{foil}'
            run_cmd(copyOFtemp)
            run_cmd(changeOFdir)
            mesh.create_cfMeshDict('NACA0018')
            os.system('cp {}/geometry/domain_NACA{}.stl {}/run/NACA{}'.format(cwd, foil, cwd, foil))
            os.system('mv {}/run/NACA{}/domain_NACA{}.stl {}/run/NACA{}/domain.stl'.format(cwd,foil,foil,cwd,foil))
            os.system('sed -i "/internalField   uniform (0 0 0);/c internalField   uniform ({} 0 0); " {}/run/NACA{}/0/U'
                .format(settings.Uinlet, cwd, foil))
            os.system('./run/NACA{}/run.sh'.format(foil))
            
