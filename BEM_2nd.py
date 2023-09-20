import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os


#Constants 
TSR = 5
R = 1 # m
U = 1 # m/s
omega = (U * TSR) / R
a = 3 #FInd the way to calculate
N = 3 # number of blades 
tol = 1e-03


#Aerodynamics table
# alpha = np.arange(start = -20, stop = 20.000001, step = 1)
# charTable = pd.DataFrame(alpha, columns = ['alpha'])
# charTable['Cl'] = np.full([41, 1], 1, dtype = int)
# charTable['Cd'] = np.full([41, 1], 1, dtype = int)

alpha = np.arange(start = -2, stop = 2.000001, step = 1)
charTable = pd.DataFrame(alpha, columns = ['alpha'])
charTable['Cl'] = [-2, -1, 0, 1, 2]
charTable['Cd'] = [-2, -1, 0, 1, 2]

#print(charTable)

ClFit = np.polyfit(charTable['Cl'], charTable['alpha'], 1)
CdFit = np.polyfit(charTable['Cd'], charTable['alpha'], 1)
# plt.plot(charTable['alpha'], ClFit[0] * charTable['alpha'] + ClFit[1])
# plt.scatter(charTable['alpha'], charTable['Cl'])
# plt.show()

#Blade table
# r_range = np.arange(start = 0, stop = 1.000001, step = 0.25)
r_range = [0, 0.25, 0.50, 0.75, 0.99]
blade1 = pd.DataFrame(r_range, columns=['r'])
blade1['r_diff'] = blade1['r'].diff()
blade1['theta'] = np.full([5, 1], 0, dtype = int)
blade1['chord'] = np.full([5, 1], 1, dtype = int)



#Calculation 
a_axial = 0
a_tang = 0
a_axial_ini = 1 # initial tolerance
a_tang_ini = 1
# for i in range(5):

while a_axial_ini > tol and a_tang_ini > tol:
    blade1['fi'] = np.arctan(((1 - a_axial) * U) / ((1 - a_tang) * blade1['r'] * omega))
    blade1['AoA'] = blade1['fi'] - blade1['theta']
    blade1['Cl'] = ClFit[0] * blade1['AoA'] + ClFit[1]
    blade1['Cd'] = CdFit[0] * blade1['AoA'] + CdFit[1]
    blade1['Cn'] = blade1['Cl'] * np.cos(blade1['fi'] + blade1['Cd'] * np.sin(blade1['fi']))
    blade1['CT'] = blade1['Cl'] * np.sin(blade1['fi'] - blade1['Cd'] * np.cos(blade1['fi']))
    #blade1['F'] =  2 / np.pi *np.arccos(np.exp((N * (R - blade1['r'])) / (2 * blade1['r'] * np.sin(blade1['fi']))))
    blade1['f'] = (N *(R - blade1['r'])) / (2 * blade1['r'] * np.sin(blade1['fi']))
    blade1['F'] =  2 / math.pi * np.arccos(np.exp(-1 * blade1['f']))
    blade1['solidity'] = (blade1['chord'] * N) / (2 * math.pi * R) 
    # if blade1['solidity'].any() >= 1:
    if (blade1['solidity'] >= 1).any():
        print(' - - - Solidity cannot be greater than 1!- - - \n - - - Breaking the loop! - - -')
        break
    else:
        blade1['a_axial'] = 1 / (4 * blade1['F'] * pow(np.sin(blade1['fi']), 2) / (blade1['solidity'] * blade1['Cn'] + 1))
        blade1['a_tang'] = 1 / (4 * blade1['F'] * np.sin(blade1['fi']) * ( np.cos(blade1['fi'])) / (blade1['solidity'] * blade1['Cn'] - 1))
        blade1['tol_a_axial'] = abs(a_axial - blade1['a_axial'])
        blade1['tol_a_tang'] = abs(a_tang - blade1['a_tang'])
        a_axial_tol_max = blade1['tol_a_axial'].max()
        a_tang_tol_max = blade1['tol_a_tang'].max()
        print(f'{a_axial_tol_max} and {a_tang_tol_max}')
        a_axial = blade1['a_axial']
        a_tang = blade1['a_tang']
        a_axial_ini = blade1['tol_a_axial'].max()
        a_tang_ini = blade1['tol_a_tang'].max()
        print('\n')
        print(blade1)

    
# blade1['dT'] = 4 * np.pi * blade1['r'] * pow(U,2) * (1 - blade1['a_axial']) * blade1['a_axial'] * blade1['F'] * blade1['r_diff']
# blade1['dQ'] = 4 * np.pi * pow(blade1['r'],3) * U * omega * (1 - blade1['a_axial']) * blade1['a_tang'] * blade1['F'] * blade1['r_diff']
# print(blade1)