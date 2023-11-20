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
# from sklearn.tree import plot_tree
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

def create_cfMeshDict(range, airfoil, range_path = str):

    if range == False:
        file = open(f'{cwd}/run/{airfoil}/system/meshDict', "w+")
    else:
        file = open(f'{range_path}/system/meshDict', "w+")


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
    	wake
        {
            cellSize 0.05;
            type box;
            centre (0 0 0);
            lengthX 3;
            lengthY 2;
            lengthZ 1;
        }
}

edgeMeshRefinement
{

}

localRefinement
{
	Foil
	{
		additionalRefinementLevels 5;
		refinementThickness 0.1; //cm
	}
}

boundaryLayers
{
	patchBoundaryLayers
	{
		Foil
		{
			nLayers 10;
			thicknessRatio 1.1;
			maxFirstLayerThickness 1;
			allowDiscontinuity 1;
		}
	}
}


// ************************************************************************* //""")
    

def create_Savonius_cfMeshDict(case_path: str):

    #TODO: Develop a function to combine maxCellSize with VAWT diameter

    file = open(f'{case_path}/system/meshDict', "w+")

    file.write("""FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      meshDict;
}

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

surfaceFile     "domain.fms";

maxCellSize     0.025;



objectRefinements
{

}

edgeMeshRefinement
{

}

localRefinement
{
	Rotor
	{
		additionalRefinementLevels 2;
		refinementThickness 0.1; //cm
	}
}

boundaryLayers
{
	patchBoundaryLayers
	{
		Rotor
		{
			nLayers 5;
			thicknessRatio 1.1;
			maxFirstLayerThickness 1;
			allowDiscontinuity 1;
		}
	}
}


// ************************************************************************* //""")