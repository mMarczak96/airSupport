import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os

# This file contains all necessary physics function 

#Reynolds number
def Re(ro,U,d,visc):
    Re = (ro * U * d) / visc

    return int(Re)
















# FUN
def squat(n):
    ran = np.linspace(1, n, n)
    print(ran)
    ran = np.flip(ran)
    sum = 0
    start_val = 2 * n -1
    print(f'starting value {start_val}')

    for i in ran :
        val = 2 * i - 1
        print(val)
        sum = sum + val
    
    print(f'total: {sum}')

squat(20)
