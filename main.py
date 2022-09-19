from cgitb import reset
from turtle import filling
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


Naca = Airfoil("NACA0018", settings.A, settings.T, settings.N)
LE = Naca.airfoil_coord(Naca.A, Naca.T, Naca.n)
TE = Naca.roundedTE(settings.NT, settings.ST, settings.ET, LE)

LE_salome = Naca.airfoil_salome(LE)
TE_salome = Naca.TE_salome(TE)
fullFoilSal = Naca.mergeSalomeFoil(LE_salome, TE_salome)
#print(fullFoilSal)
mergedFoil = Naca.mergeFoil(LE,TE)
Naca.drawFoil(mergedFoil)
Naca.writeFoilToSalomeFile(fullFoilSal)



