from cgitb import reset
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os
from airfoil import Airfoil
import argparse
import settings

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument()
    parser.add_argument('-a' ,'--airfoil', help="Create airfoil .stl file", required=False )

    args = parser.parse_args()
    return args

# if __name__ == '__main__':

#     args = parse_args()
#     airfoil = args.airfoil 


Naca = Airfoil("naca0018", settings.A, settings.T, settings.N)
LE = Naca.airfoil_coord(Naca.A, Naca.T, Naca.n)
# TE = Naca.roundedTE(settings.NT, settings.ST, settings.ET, LE)
# foil = Naca.mergeFoil(LE, TE)
# pwd =os.getcwd() + '/' + Naca.name + "_"
# Naca.printSalomeFoil(pwd, foil)

