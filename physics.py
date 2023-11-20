import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
from subprocess import PIPE, run


# This file contains all necessary physics function 

#Reynolds number
def Re(ro,U,d,visc):
    Re = (ro * U * d) / visc

    return int(Re)


def run_cmd(self, command : str):
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














