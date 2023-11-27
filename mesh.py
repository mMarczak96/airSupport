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
import settings

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
    

def create_5Blocks_BlockMeshDict(coords_up_front, coords_down_front ,case_path: str):
    # Calculating computational domain size in a function of airfoil chord
    inlet_scale = 10 * settings.c 
    outlet_scale = 15 * settings.c
    # Creating data frames for back plane of the domain
    coords_up_back = coords_up_front[['X', 'Y']].copy()
    coords_up_back['Z'] = 1
    coords_down_back = coords_down_front[['X', 'Y']].copy()
    coords_down_back['Z'] = 1
    #Creating data frames of the airfoil coordinates in string form for the blockMeshDict
    coords_front_up_list = []
    coords_back_up_list = []
    for i in range(len(coords_up_front)):
        coords_front_element = f" ( {coords_up_front.loc[i, 'X']} {coords_up_front.loc[i, 'Y']} {coords_up_front.loc[i, 'Z']} ) "
        coords_back_element = f" ( {coords_up_front.loc[i, 'X']} {coords_up_front.loc[i, 'Y']} 1 ) "
        coords_front_up_list.append(coords_front_element)
        coords_back_up_list.append(coords_back_element)

    df_front_up = pd.DataFrame(coords_front_up_list, columns=['coords'])
    df_back_up = pd.DataFrame(coords_back_up_list, columns=['coords'])

    coords_front_down_list = []
    coords_back_down_list = []    

    for i in range(len(coords_down_front)):
        coords_front_element = f" ( {coords_down_front.loc[i, 'X']} {coords_down_front.loc[i, 'Y']} {coords_down_front.loc[i, 'Z']} ) "
        coords_back_element = f" ( {coords_down_front.loc[i, 'X']} {coords_down_front.loc[i, 'Y']} 1 ) "
        coords_front_down_list.append(coords_front_element)
        coords_back_down_list.append(coords_back_element)

    df_front_down = pd.DataFrame(coords_front_down_list, columns=['coords'])
    df_back_down = pd.DataFrame(coords_back_down_list, columns=['coords'])
    # Creating data frame of computational domain vertices in string form for the blockMeshDict
    vertices_list_print = np.array([
        [coords_up_front['X'][coords_up_front.index[0]], coords_up_front['Y'][coords_up_front.index[0]], coords_up_front['Z'][coords_up_front.index[0]]],  #0
        [coords_up_front['X'][coords_up_front.index[-1]], coords_up_front['Y'][coords_up_front.index[-1]], coords_up_front['Z'][coords_up_front.index[-1]]], #1
        [coords_up_front['X'][coords_up_front.index[-1]], inlet_scale, coords_up_front['Z'][coords_up_front.index[-1]]], #2
        [-inlet_scale, coords_up_front['Y'][coords_up_front.index[0]], coords_up_front['Z'][coords_up_front.index[0]]],  #3
        [outlet_scale, coords_up_front['Y'][coords_up_front.index[-1]], coords_up_front['Z'][coords_up_front.index[-1]]],  #4
        [outlet_scale, inlet_scale, coords_up_front['Z'][coords_up_front.index[-1]]],  #5
        [coords_down_front['X'][coords_up_front.index[-1]], coords_down_front['Y'][coords_up_front.index[-1]], coords_down_front['Z'][coords_up_front.index[-1]]], #6
        [outlet_scale, coords_down_front['Y'][coords_up_front.index[-1]], coords_down_front['Z'][coords_up_front.index[-1]]], #7
        [coords_down_front['X'][coords_up_front.index[-1]], -inlet_scale, coords_down_front['Z'][coords_up_front.index[-1]]], #8
        [outlet_scale, -inlet_scale, coords_down_front['Z'][coords_up_front.index[-1]]], #9
        [coords_up_back['X'][coords_up_back.index[0]], coords_up_back['Y'][coords_up_back.index[0]], coords_up_back['Z'][coords_up_back.index[0]]], #10
        [coords_up_back['X'][coords_up_back.index[-1]], coords_up_back['Y'][coords_up_back.index[-1]], coords_up_back['Z'][coords_up_back.index[-1]]], #11
        [coords_up_back['X'][coords_up_back.index[-1]], inlet_scale, coords_up_back['Z'][coords_up_back.index[-1]]] , #12
        [-inlet_scale, coords_up_back['Y'][coords_up_back.index[0]], coords_up_back['Z'][coords_up_back.index[0]]] , #13
        [outlet_scale, coords_up_back['Y'][coords_up_back.index[-1]], coords_up_back['Z'][coords_up_back.index[-1]]],  #14
        [outlet_scale, inlet_scale, coords_up_back['Z'][coords_up_back.index[-1]]] , #15
        [coords_down_back['X'][coords_up_back.index[-1]], coords_down_back['Y'][coords_up_back.index[-1]], coords_down_back['Z'][coords_up_back.index[-1]]] , #16
        [outlet_scale, coords_down_back['Y'][coords_up_back.index[-1]], coords_down_back['Z'][coords_up_back.index[-1]]] , #17
        [coords_down_back['X'][coords_up_back.index[-1]], -inlet_scale, coords_down_back['Z'][coords_up_back.index[-1]]] , #18
        [outlet_scale, -inlet_scale, coords_down_back['Z'][coords_up_back.index[-1]]] #19
    ])

    point_counter = 0
    vertices_list = []
    for point in vertices_list_print:
        element = f"( {point[0]} {point[1]} {point[2]}) // {point_counter}"
        vertices_list.append(element)
        point_counter += 1
  
    vertices_df = pd.DataFrame(vertices_list, columns=['vertices'])
    ## Optional plotting of the vertices
    # labels = np.arange(0,len(vertices_list),1)
    # p = pv.Plotter()
    # p.add_point_labels(
    #     vertices_list_print,
    #     labels,
    #     italic=True,
    #     font_size=10,
    #     point_color='red',
    #     point_size=10,
    #     render_points_as_spheres=True,
    #     always_visible=True,
    #     shadow=True,
    # )
    # p.show_grid()
    # p.show()

    #Creating blockMeshdict out of previously prepared data
    # TODO: prepare better mesh grading procedure. Preferably in function of the domain size
    file = open(f'{case_path}', "w+")

    file.write("""/*--------------------------------*- C++ -*----------------------------------*\
  =========                 |
  \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox
   \\    /   O peration     | Website:  https://openfoam.org
    \\  /    A nd           | Version:  7
     \\/     M anipulation  |
\*---------------------------------------------------------------------------*/																
FoamFile																
{																
    version     2.0;																
    format      ascii;																
    class       dictionary;																
    object      blockMeshDict;																
}																
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

															
scale 1;														
                                                                
geometry																
{																
}	

vertices
(
               															
	""")
    file.close 

    file =  open(f'{case_path}', "a+")
    file.write(vertices_df.to_string(header=False, index=False))
    file.write(""" 
        );
        
blocks																
(																
	hex	(0 1 2 3 10 11 12 13)	( 500 150 1) simpleGrading (1 1000 1)   //block	0
																													
	hex	(1 4 5 2 11 14 15 12)	( 700 150 1) simpleGrading (15 1000 1)  //block	1														
               											
	hex	(6 7 4 1 16 17 14 11)	( 700 15 1) simpleGrading (15 1 1)      //block	2
																																								
	hex	(8 9 7 6 18 19 17 16)	( 700 150 1) simpleGrading (15 0.001 1) //block	3	
	
	hex	(3 8 6 0 13 18 16 10)	( 500 150 1) simpleGrading (1 0.001 1)  //block	4								
);		

edges																
(																
	arc	2 3	(-7 7 0)									
	arc	12 13	(-7 7 1)
	arc	8 3	(-7 -7 0)									
	arc	18 13	(-7 -7 1)									
																
	spline	0 1													
	(					      

    """)
    file.write(df_front_up.to_string(header=False, index=False))
    file.write(""" 
    )
    spline 10 11
    (
    """)
    file.write(df_back_up.to_string(header=False, index=False))
    file.write(""" 
	)																																																													
	spline	0	6													
	(
    """)
    file.write(df_front_down.to_string(header=False, index=False))
    file.write(""" 
    )
    spline 10 16
    (
    """)
    file.write(df_back_down.to_string(header=False, index=False))   
    file.write(""" 
							
    )															
                                                                    
                                                                    
    );																
                                                                    
    faces																
    (																
                                                                    
    );																
                                                                    
    faces																
    (																
                                                                    
    );																
                                                                    
                                                                    
    defaultPatch																
    {																
        name frontAndBack;																
        type empty;																
    }		
                                                                                                                                
    boundary																
    (																
        inlet              																
            {																
            type patch;    																
            faces																
            (																
                (3 13 12 2)
                (8 18 13 3)
                (5 2 12 15)
                (8 9 19 18)															
            );																
            } 
        outlet              																
            {																
            type patch;    																
            faces																
            (																
                (4 5 15 14)
                (7 4 14 17)
                (7 17 19 9)  															
            );																
            }	

        foil              																
            {																
            type wall;    																
            faces																
            (																
                (0 1 11 10)
                (0 6 16 10)
                (6 1 11 16)															
            );																
            }	
                                                                
                                                                        
    );	
    // ************************************************************************* //																
                                                                    			               	
    """)
