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

    inlet_scale = 10 * settings.c 
    outlet_scale = 15 * settings.c
    coords_up_back = coords_up_front[['X', 'Y']].copy()
    coords_up_back['Z'] = 1

    #Correct function for lower airfoil surface generation. For now its broken:
    coords_down_front['Y'] = coords_down_front['Y'] * (-1)   
    coords_down_back = coords_down_front[['X', 'Y']].copy()
    coords_down_back['Z'] = 1
    
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

    vertices_list_print = np.array([
        [coords_up_front['X'][coords_up_front.index[0]], coords_up_front['Y'][coords_up_front.index[0]], coords_up_front['Z'][coords_up_front.index[0]] ], #0
        [coords_up_front['X'][coords_up_front.index[-1]], coords_up_front['Y'][coords_up_front.index[-1]], coords_up_front['Z'][coords_up_front.index[-1]] ], #1
        [coords_up_front['X'][coords_up_front.index[-1]], inlet_scale, coords_up_front['Z'][coords_up_front.index[-1]] ], #2
        [-inlet_scale, coords_up_front['Y'][coords_up_front.index[0]], coords_up_front['Z'][coords_up_front.index[0]] ], #3
        [coords_up_back['X'][coords_up_back.index[0]], coords_up_back['Y'][coords_up_back.index[0]], coords_up_back['Z'][coords_up_back.index[0]] ], #4
        [coords_up_back['X'][coords_up_back.index[-1]], coords_up_back['Y'][coords_up_back.index[-1]], coords_up_back['Z'][coords_up_back.index[-1]] ], #5
        [coords_up_back['X'][coords_up_back.index[-1]], inlet_scale, coords_up_back['Z'][coords_up_back.index[0]] ], #6
        [-inlet_scale, coords_up_back['Y'][coords_up_back.index[0]], coords_up_back['Z'][coords_up_back.index[0]] ], #7
        [outlet_scale, coords_up_front['Y'][coords_up_front.index[-1]], coords_up_front['Z'][coords_up_front.index[-1]] ], #8
        [outlet_scale, inlet_scale, coords_up_front['Z'][coords_up_front.index[0]] ], #9
        [outlet_scale, coords_up_back['Y'][coords_up_back.index[-1]], coords_up_back['Z'][coords_up_back.index[-1]] ], #10
        [outlet_scale, inlet_scale, coords_up_back['Z'][coords_up_back.index[0]] ], #11
        [coords_up_front['X'][coords_up_front.index[-1]], -inlet_scale, coords_up_front['Z'][coords_up_front.index[-1]] ], #12
        [coords_up_back['X'][coords_up_back.index[-1]], -inlet_scale, coords_up_back['Z'][coords_up_back.index[-1]] ], #13
        [outlet_scale, -inlet_scale, coords_up_front['Z'][coords_up_front.index[-1]] ], #14
        [outlet_scale, -inlet_scale, coords_up_back['Z'][coords_up_back.index[-1]] ], #15
        [coords_down_front['X'][coords_down_front.index[-1]], coords_down_front['Y'][coords_down_front.index[-1]], coords_down_front['Z'][coords_down_front.index[-1]] ], #16
        [coords_down_back['X'][coords_down_back.index[-1]], coords_down_back['Y'][coords_down_back.index[-1]], coords_down_back['Z'][coords_down_back.index[-1]] ], #17
        [outlet_scale, coords_down_front['Y'][coords_down_front.index[-1]], coords_down_front['Z'][coords_up_back.index[-1]] ], #18
        [15, coords_down_front['Y'][coords_down_front.index[-1]], 1], #19
    ])

    vertices_list = [
       f"({coords_up_front['X'][coords_up_front.index[0]]} {coords_up_front['Y'][coords_up_front.index[0]]} {coords_up_front['Z'][coords_up_front.index[0]]} ) // 0",
       f"({coords_up_front['X'][coords_up_front.index[-1]]} {coords_up_front['Y'][coords_up_front.index[-1]]} {coords_up_front['Z'][coords_up_front.index[-1]]} ) // 1",
       f"({coords_up_front['X'][coords_up_front.index[-1]]} {inlet_scale} {coords_up_front['Z'][coords_up_front.index[-1]]} ) //2 ",
       f"({-inlet_scale} {coords_up_front['Y'][coords_up_front.index[0]]} {coords_up_front['Z'][coords_up_front.index[0]]} ) // 3",
       f"({coords_up_back['X'][coords_up_back.index[0]]} {coords_up_back['Y'][coords_up_back.index[0]]} {coords_up_back['Z'][coords_up_back.index[0]]} ) // 4",
       f"({coords_up_back['X'][coords_up_back.index[-1]]} {coords_up_back['Y'][coords_up_back.index[-1]]} {coords_up_back['Z'][coords_up_back.index[-1]]} ) // 5",
       f"({coords_up_back['X'][coords_up_back.index[-1]]} {inlet_scale} {coords_up_back['Z'][coords_up_back.index[0]]} ) // 6",
       f"({-inlet_scale} {coords_up_back['Y'][coords_up_back.index[0]]} {coords_up_back['Z'][coords_up_back.index[0]]} ) // 7",
       f"({outlet_scale} {coords_up_front['Y'][coords_up_front.index[-1]]} {coords_up_front['Z'][coords_up_front.index[-1]]} ) // 8",
       f"({outlet_scale} {inlet_scale} {coords_up_front['Z'][coords_up_front.index[0]]} ) // 9",
       f"({outlet_scale} {coords_up_back['Y'][coords_up_back.index[-1]]} {coords_up_back['Z'][coords_up_back.index[-1]]} ) // 10",
       f"({outlet_scale} {inlet_scale} {coords_up_back['Z'][coords_up_back.index[0]]} ) // 11",
       f"({coords_up_front['X'][coords_up_front.index[-1]]} {-inlet_scale} {coords_up_front['Z'][coords_up_front.index[-1]]} ) // 12",
       f"({coords_up_back['X'][coords_up_back.index[-1]]} {-inlet_scale} {coords_up_back['Z'][coords_up_back.index[-1]]} ) // 13",
       f"({outlet_scale} {-inlet_scale} {coords_up_front['Z'][coords_up_front.index[-1]]} ) // 14",
       f"({outlet_scale} {-inlet_scale} {coords_up_back['Z'][coords_up_back.index[-1]]} ) // 15",
       f"({coords_down_front['X'][coords_down_front.index[-1]]} {coords_down_front['Y'][coords_down_front.index[-1]]} {coords_down_front['Z'][coords_down_front.index[-1]]} ) // 16",
       f"({coords_down_back['X'][coords_down_back.index[-1]]} {coords_down_back['Y'][coords_down_back.index[-1]]} {coords_down_back['Z'][coords_down_back.index[-1]]}) // 17",
       f"({outlet_scale} {coords_down_front['Y'][coords_down_front.index[-1]]} {coords_down_front['Z'][coords_up_back.index[-1]]} ) // 18",
       f"({outlet_scale}, {coords_down_front['Y'][coords_down_front.index[-1]]} 1 ) // 19",
    ]

    vertices_df = pd.DataFrame(vertices_list, columns=['vertices'])

    print("lsttt")


    labels = np.arange(0,20,1)
    p = pv.Plotter()
    p.add_point_labels(
    vertices_list_print,
    labels,
    italic=True,
    font_size=10,
    point_color='red',
    point_size=10,
    render_points_as_spheres=True,
    always_visible=True,
    shadow=True,
)
    p.show_grid()
    # p.show()

    file = open(f'{case_path}', "w+")

    file.write("""
        /*--------------------------------*- C++ -*----------------------------------*/
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
        convertToMeters	1	;														
                                                                        
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
	hex	(0	1	2	3	4	5	6	7)	(	41	48	1	)	//block	1
	edgeGrading															
	(															
	//	x-direction	expansion	ratio												
	(															
(	0.4	0.51219512195122	3.5	)												
(	0.6	0.487804878048781	0.857142857142857	)												
	)															
	0.03	0.03														
	(															
(	0.4	0.51219512195122	3.5	)												
(	0.6	0.487804878048781	0.857142857142857	)												
	)															
	//	y-direction	expansion	ratio												
	(															
(	0.041666666666667	0.354166666666667	22.1861110674044	)												
(	0.958333333333333	0.645833333333333	9.0146488220659	)												
	)															
	(															
(	0.041666666666667	0.354166666666667	22.1861110674044	)												
(	0.958333333333333	0.645833333333333	9.0146488220659	)												
	)															
	(															
(	0.041666666666667	0.354166666666667	22.1861110674044	)												
(	0.958333333333333	0.645833333333333	9.0146488220659	)												
	)															
	(															
(	0.041666666666667	0.354166666666667	22.1861110674044	)												
(	0.958333333333333	0.645833333333333	9.0146488220659	)												
	)															
																
	//	z-direction	expansion	ratio												
	1	1	1	1												
	)															
																
	hex	(1	8	9	2	5	10	11	6)	(	74	48	1)	//block	2	
	edgeGrading															
	(															
	//	x-direction	expansion	ratio												
	33.3333333333333	33.3333333333333	33.3333333333333	33.3333333333333												
	//	y-direction	expansion	ratio												
	(															
(	0.041666666666667	0.354166666666667	22.1861110674044	)												
(	0.958333333333333	0.645833333333333	9.0146488220659	)												
	)															
	13.9581659180375	13.9581659180375														
	(															
(	0.041666666666667	0.354166666666667	22.1861110674044	)												
(	0.958333333333333	0.645833333333333	9.0146488220659	)												
	)															
																
	//	z-direction	expansion	ratio												
	1	1	1	1												
	)															

               											
	hex	(3	12	16	0	7	13	17	4)	(	41	48	1	)	//block	3
	edgeGrading															
	(															
	//	x-direction	expansion	ratio												
	0.03															
	(															
(	0.4	0.51219512195122	3.5	)												
(	0.6	0.487804878048781	0.857142857142857	)												
	)															
	(															
(	0.4	0.51219512195122	3.5	)												
(	0.6	0.487804878048781	0.857142857142857	)												
	)															
	0.03															
	//	y-direction	expansion	ratio												
	(															
(	0.958333333333333	0.645833333333333	0.110930555337022	)												
(	0.041666666666667	0.354166666666667	0.04507324411033	)												
	)															
	(															
(	0.958333333333333	0.645833333333333	0.110930555337022	)												
(	0.041666666666667	0.354166666666667	0.04507324411033	)												
	)															
	(															
(	0.958333333333333	0.645833333333333	0.110930555337022	)												
(	0.041666666666667	0.354166666666667	0.04507324411033	)												
	)															
	(															
(	0.958333333333333	0.645833333333333	0.110930555337022	)												
(	0.041666666666667	0.354166666666667	0.04507324411033	)												
	)															
																
	//	z-direction	expansion	ratio												
	1	1	1	1												
	)															
																
																												
	hex	(12	14	18	16	13	15	19	17)	(	74	48	1)	//block	4	
	edgeGrading															
	(															
	//	x-direction	expansion	ratio												
	33.3333333333333	33.3333333333333	33.3333333333333	33.3333333333333												
	//	y-direction	expansion	ratio												
	(															
(	0.958333333333333	0.645833333333333	0.110930555337022	)												
(	0.041666666666667	0.354166666666667	0.04507324411033	)												
	)															
	0.071642650321827	0.071642650321827														
	(															
(	0.958333333333333	0.645833333333333	0.110930555337022	)												
(	0.041666666666667	0.354166666666667	0.04507324411033	)												
	)															
																
	//	z-direction	expansion	ratio												
	1	1	1	1												
	)	
	hex	(16 18 8 1 13 15 19 17)	(	74	48	1)	//block	5
	edgeGrading															
	(															
	//	x-direction	expansion	ratio												
	33.3333333333333	33.3333333333333	33.3333333333333	33.3333333333333												
	//	y-direction	expansion	ratio												
	(															
(	0.958333333333333	0.645833333333333	0.110930555337022	)												
(	0.041666666666667	0.354166666666667	0.04507324411033	)												
	)															
	0.071642650321827	0.071642650321827														
	(															
(	0.958333333333333	0.645833333333333	0.110930555337022	)												
(	0.041666666666667	0.354166666666667	0.04507324411033	)												
	)															
																
	//	z-direction	expansion	ratio												
	1	1	1	1												
	)														
);		

edges																
(																
	arc	3 2	(	-7.48528137423857	8.48528137423857	0	)									
	arc	7 6 	(	-7.48528137423857	8.48528137423857	1	) 									
																
	spline	0 1													
	(					      

    """)
    file.write(df_front_up.to_string(header=False, index=False))
    file.write(""" 
    spline 4 5
    (
    """)
    file.write(df_back_up.to_string(header=False, index=False))
    file.write(""" 
	)															
																
																
	arc	3 12	(	-7.48528137423857	-8.48528137423857	0	)									
	arc	7 13	(	-7.48528137423857	-8.48528137423857	1	)									
																
	spline	0	16													
	(
    """)
    file.write(df_front_up.to_string(header=False, index=False))
    file.write(""" 
    spline 4 17
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
    inlet              // patch name																
            {																
                type patch;    // patch type for patch 0																
                faces																
                (																
                    (9 2 6 11)  // block face in this patch																
                    (2 3 7 6  )  // block face in this patch																
                    (3 12 13 7  )  // block face in this patch																
                    (12 15 14 13  )  // block face in this patch																
                );																
            } 																
                                                                    
    outlet              // patch name																
            {																
                type patch;    // patch type for patch 0																
                faces																
                (																
                    (8 9 10 11)  // block face in this patch																
                    (8 18 19 10)  // block face in this patch	
                    (14 15 19 18) // block face in this patch																
                );																
            }																
                                                                    
    walls              // patch name																
            {																
                type wall;    // patch type for patch 0																
                faces																
                (																
                    (0 1 5 4)  // block face in this patch																
                    (0 4 17 16)  // block face in this patch	
                    (1 16 17 5)  // block face in this patch															
                );																
            } 																
                                                                    		
    );																
                                                                    			               	
    """)
