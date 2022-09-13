from math import tan
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os


#Constants 
TSR = 5
R = 10 # m
U = 5 # m/s
omega = (U * TSR) / R
a = 3 #FInd the way to calculate
N = 3 # number of blades (maybe)
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
r_range = np.arange(start = 0, stop = 1.000001, step = 0.25)
blade1 = pd.DataFrame(r_range, columns=['r'])
blade1['theta'] = np.full([5, 1], 0, dtype = int)
blade1['chord'] = np.full([5, 1], 1, dtype = int)


#Calculation 
a_prim = a

blade1['fi'] = np.arctan(((1 - a) * U) / ((1 - a_prim) * blade1['r'] * omega))
blade1['AoA'] = blade1['fi'] - blade1['theta']
blade1['Cl'] = ClFit[0] * blade1['AoA'] + ClFit[1]
blade1['Cd'] = CdFit[0] * blade1['AoA'] + CdFit[1]
blade1['Cn'] = blade1['Cl'] * np.cos(blade1['fi'] + blade1['Cd'] * np.sin(blade1['fi']))
blade1['CT'] = blade1['Cl'] * np.sin(blade1['fi'] - blade1['Cd'] * np.cos(blade1['fi']))
#blade1['F'] =  2 / np.pi *np.arccos(np.exp((N * (R - blade1['r'])) / (2 * blade1['r'] * np.sin(blade1['fi']))))
blade1['F'] = 1
blade1['sigma'] = 1
blade1['a'] = 1 / (4 * blade1['F'] * pow(np.sin(blade1['fi']), 2) / (blade1['sigma']) * blade1['Cn'] + 1)
blade1['a_prim'] = 1 / (4 * blade1['F'] * np.sin(blade1['fi']) * ( np.cos(blade1['fi'])) / (blade1['sigma']) * blade1['Cn'] - 1)
print(blade1)