from cgitb import reset
import cmd
from turtle import color
from matplotlib.patches import Arc
from subprocess import PIPE, run
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os
import sys
import pyvista as pv
from sklearn.tree import plot_tree
from sympy import li
from tenacity import retry 
import pathlib

cwd = os.getcwd()
center = [0,0,0]

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

# CF MESH

def create_cfMeshDict(airfoil):

    file = open('{}/run/NACA0018/system/meshDict'.format(cwd, airfoil), "w+")

    file.write("""FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      meshDict;
}

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

surfaceFile     "domain.fms";

maxCellSize     0.05;



objectRefinements
{

}

edgeMeshRefinement
{

}

localRefinement
{
	foil
	{
		additionalRefinementLevels 5;
		refinementThickness 0.1; //cm
	}
}

boundaryLayers
{
	patchBoundaryLayers
	{
		foil
		{
			nLayers 20;
			thicknessRatio 1.1;
			maxFirstLayerThickness 1;
			allowDiscontinuity 1;
		}
	}
}


// ************************************************************************* //""")