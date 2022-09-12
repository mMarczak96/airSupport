from cgitb import reset
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os
from airfoil import Airfoil
import argparse

# AIRFOIL SETTINGS:
A = 0 #NACA0018
T = 0.18 #NACA0018
N = 100 # number of points without trailing edge

# AIRFOIL TRAILING EDGE SETTINGS:
NT = 10 #number of points on trailing edge
ST = 20 #starting degree value
ET = 90 #ending degree value

