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

# TEST = VAWT.Savonius("test",1,1,1,1,1)
# TEST.test("HURAAA")
# TEST.Savonius_geom('test_s',0.1, 1.8, 2, 0.2)
    
# geom.VAWT_line_inlet(1, 10, 20, "VAWT_inlet")

# geom.VAWT_line_outlet(1,10,20, 'VAWT_outlet')

# geom.VAWT_domain(1,20,30,15,'testcase')

# geom.group_STL_domain(['inlet', 'outlet', 'sides', 'rotor'],'/home/maciek/repository/airSupport/geometry/testcase' )

# geom.savoniusVAWT("testcase", 0.05, 0.9, 1, 0.2)


