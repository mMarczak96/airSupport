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
import VAWT

# TEST = VAWT.Savonius("test]1,1,1,1,1)
# TEST.test("HURAAA")
# TEST.Savonius_geom('test_s',0.1, 1.8, 2, 0.2)
    
# geom.VAWT_line_inlet(1, 10, 20, "VAWT_inlet")

# geom.VAWT_line_outlet(1,10,20, 'VAWT_outlet')

# geom.VAWT_domain(1,20,30,15,'testcase')

# geom.group_STL_domain(['inlet', 'outlet', 'sides', 'rotor'],'/home/maciek/repository/airSupport/geometry/testcase' )

# geom.savoniusVAWT("testcase] 0.05, 0.9, 1, 0.2)



def quadratic_interpolation(x0, y0, x1, y1, x):
    """
    Quadratic interpolation between two points (x0, y0) and (x1, y1) at a given x.

    Parameters:
    - x0, y0: Coordinates of the first point
    - x1, y1: Coordinates of the second point
    - x: The x-coordinate for interpolation

    Returns:
    - The interpolated y-coordinate at the given x
    """
    # Coefficients of the quadratic function ax^2 + bx + c
    a = (y1 - y0) / ((x1 - x0) * (x1 - x0))
    b = (y0 - a * x0 * x0 - y1 + a * x1 * x1) / (x0 - x1)
    c = y0 - a * x0 * x0 - b * x0

    # Quadratic interpolation formula
    y = a * x * x + b * x + c
    return y

# Example usage:
x0, y0 = -10 ,1
x1, y1 = 0, -10
interpolation_point = -9

result = quadratic_interpolation(x0, y0, x1, y1, interpolation_point)
print(f"Interpolated value at x={interpolation_point}: {result}")

inter_pt_lst = np.array([-10,-9,-8,-7,-6,-5,-4,-3,-2,-1,0,1])
Y_lst =[]

for i in inter_pt_lst:
    element = quadratic_interpolation(x0, y0, x1, y1, i)
    Y_lst.append(element)

Y_lst=np.array(Y_lst)

def func(x):
    return 0.11*x*x-11

new_lst = []
for i in inter_pt_lst:
    element = func(i)
    new_lst.append(element)

new_lst = np.array(new_lst)


print(new_lst)


plt.plot(inter_pt_lst,new_lst)
plt.plot(inter_pt_lst,new_lst*(-1))
plt.plot(-10,0, marker='o')
plt.plot(1,10,marker='*')
plt.plot(1,-10,marker='s')
plt.show()