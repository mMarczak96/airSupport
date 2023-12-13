from cgitb import reset
from turtle import color
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os
import sys
import pyvista as pv 
from subprocess import PIPE, run
# import salome
# salome.salome_init()
# import salome_notebook
#triSurf().writeFms(‘domain.fms’) 
class Airfoil:
    A = None
    T = None 
    n = None
    name = ""

    def __init__(self, name, A, T, n):
        self.name = name
        self.A = A 
        self.T = T
        self.n = n

    
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

    def nameSTLpart(self, name: str, file: str):
        cwd=os.getcwd()
        nameStart = f'sed -i "/solid Visualization Toolkit generated SLA File/c solid {name} " {cwd}/geometry/{file}.stl'

        return nameStart

    def nameSTLpartEnd(self, name: str, file: str):
        cwd=os.getcwd()
        nameEnd = f'sed -i "/endsolid/c endsolid {name} " {cwd}/geometry/{file}.stl'

        return nameEnd
    
    # 4 Digit symmetric airfoil

    def foil_cords_plus(self, A, T, n):
        a0 = 0.2969
        a1 = -0.126
        a2 = -0.3516
        a3 = 0.2843
        a4 = -0.1015
        delta_deg = 180 / n
        lst_deg = np.arange(start = 0, stop = 180.000001, step = delta_deg)
        foil_Pts = pd.DataFrame(lst_deg, columns = ['deg'])
        foil_Pts['rad'] = foil_Pts['deg'] * 0.0174532925
        foil_Pts['X'] = (1 - np.cos(foil_Pts['rad'])) / 2
        foil_Pts['Y'] = T / 0.2 *( a0 * pow(foil_Pts['X'],0.5) + a1 * foil_Pts['X'] + a2 * pow(foil_Pts['X'],2) + a3 * pow(foil_Pts['X'],3) + a4 * pow(foil_Pts['X'],4) )
        foil_Pts['Z'] = 0

        return foil_Pts

    def foil_cords_min(self, A, T, n):
        a0 = 0.2969
        a1 = -0.126
        a2 = -0.3516
        a3 = 0.2843
        a4 = -0.1015
        delta_deg = 180 / n
        lst_deg = np.arange(start = 0, stop = 180.000001, step = delta_deg)
        foil_Pts = pd.DataFrame(lst_deg, columns = ['deg'])
        foil_Pts['rad'] = foil_Pts['deg'] * 0.0174532925
        foil_Pts['X'] = (1 - np.cos(foil_Pts['rad'])) / 2
        foil_Pts['Y'] = -T / 0.2 *( a0 * pow(foil_Pts['X'],0.5) + a1 * foil_Pts['X'] + a2 * pow(foil_Pts['X'],2) + a3 * pow(foil_Pts['X'],3) + a4 * pow(foil_Pts['X'],4) )
        foil_Pts['Z'] = 0
        # foil_Pts = foil_Pts[::-1]

        return foil_Pts

    def roundedTE(self, nT, sT, eT, foilDF):
        degTE = eT - sT
        delta_degTE = degTE / nT 
        lst_degTE = np.arange(sT, eT + 0.0001, delta_degTE)
        TE_Pts = pd.DataFrame(lst_degTE, columns = ['deg'])
        TE_Pts['rad'] = np.deg2rad(TE_Pts['deg']) 
        TE_Pts['X'] = np.sin(TE_Pts['rad']) * ((foilDF['Y'].iloc[-2] + foilDF['Y'].iloc[-1])/2) + ((foilDF['X'].iloc[-2] + foilDF['X'].iloc[-1])/2)
        TE_Pts['Y'] = np.cos(TE_Pts['rad']) * (foilDF['Y'].iloc[-2] + foilDF['Y'].iloc[-1])/2
        TE_Pts.iat[-1,3] = 0.0
        TE_Pts['Z'] = 0
        
        return TE_Pts
    
    # 5 Digit asymmetric airfoil



    def mergeFoilPts(self, plusPts, minPts):

        PTS = pd.concat([plusPts, minPts])    
        PTS_pv = np.column_stack((PTS['X'], PTS['Y'], PTS['Z']))

        return PTS_pv, PTS

    def create_STL_foil(self, coords):
        poly = pv.PolyData()
        poly.points = coords
        cells = np.full((len(coords) - 1, 3), 2, dtype=np.int_)
        cells[:, 1] = np.arange(0, len(coords) - 1, dtype=np.int_)
        cells[:, 2] = np.arange(1, len(coords), dtype=np.int_)
        poly.lines = cells
        foil_curve = pv.Spline(coords, 5000)      
        foil_STL = foil_curve.extrude([0, 0, 1], capping=False)
        foil_STL = foil_STL.translate([-0.5,0,0])
        cwd = os.getcwd()
        foil_STL.save('{}/geometry/{}.stl'.format(cwd, self.name), binary=False)
        name = self.name
        self.run_cmd(self.nameSTLpart('Foil', name))
        self.run_cmd(self.nameSTLpartEnd('Foil', name))

        return foil_STL

    def airfoil_coord(self, A, T, n):
        a0 = 0.2969
        a1 = -0.126
        a2 = -0.3516
        a3 = 0.2843
        a4 = -0.1015
        delta_deg = 180 / n
        lst_deg = np.arange(start = 0, stop = 180.000001, step = delta_deg)
        foil_Pts = pd.DataFrame(lst_deg, columns = ['deg'])
        foil_Pts['rad'] = foil_Pts['deg'] * 0.0174532925
        foil_Pts['X'] = (1 - np.cos(foil_Pts['rad'])) / 2
        foil_Pts['Y'] = T / 0.2 *( a0 * pow(foil_Pts['X'],0.5) + a1 * foil_Pts['X'] + a2 * pow(foil_Pts['X'],2) + a3 * pow(foil_Pts['X'],3) + a4 * pow(foil_Pts['X'],4) )
        foil_Pts['Z'] = 0
        foil_Pts['sal_form'] = 'geompy.MakeVertex( ' + foil_Pts['X'].astype(str) + ', ' + foil_Pts['Y'].astype(str) + ', ' + foil_Pts['Z'].astype(str) + " )"
        #print(SAL_foil)

        return foil_Pts

    def airfoil_salome(self, foil_pts_df):
        salFormFoil = foil_pts_df['sal_form']
        SAL_foil_whole = np.array(salFormFoil)
        SAL_foil = SAL_foil_whole[:-1]

        return SAL_foil

    def TE_salome(self, TE_df):
        salFormTE = TE_df['sal_form']
        SAL_TE = np.array(salFormTE) 

        return SAL_TE       
    
    def mergeSalomeFoil(self, LE_salome, TE_salome):
        fullSalomeFoil = np.append(LE_salome, TE_salome)

        return fullSalomeFoil
    
    def mergeFoil(self, LE_df, TE_df):
        upFoil = LE_df.append(TE_df)
        downFoil = upFoil
        downFoil['Y'] = downFoil['Y'] * (-1)
        fullFoil = upFoil.append(downFoil)

        return fullFoil

    def drawFoil(self, merged_df):
        foilFig = plt.figure(figsize=(20,5))
        plt.title('{} - {} points'.format(self.name, 2 * len(merged_df['X'])))
        plt.scatter(merged_df['X'], merged_df['Y'], color='k')
        plt.scatter(merged_df['X'], -merged_df['Y'], color='k')
        plt.grid()
        plt.show()

    def writeFoilToSalomeFile(self, fullSalomeFoil):
    
        with open(os.path.join(os.getcwd() + '/foilScripts/', "{}_gen.py".format(self.name)), 'w') as gen:
            gen.write(
                str(fullSalomeFoil)
            )

    @staticmethod
    def prepend_line(file_name, line):
        """ Insert given string as a new line at the beginning of a file """
        # define name of temporary dummy file
        dummy_file = file_name + '.py'
        # open original file in read mode and dummy file in write mode
        with open(file_name, 'r') as read_obj, open(dummy_file, 'w') as write_obj:
            # Write given line to the dummy file
            write_obj.write(line + '\n')
            # Read lines from original file one by one and append them to the dummy file
            for line in read_obj:
                write_obj.write(line)
        # remove original file
        os.remove(file_name)
        # Rename dummy file as the original file
        os.rename(dummy_file, file_name)

    def printSalomeFoil(self, path, coords):
        np.savetxt(path + "foilGen" + ".py", coords, fmt='%s')

    @staticmethod
    def lines_from_points(points):
        poly = pv.PolyData()
        poly.points = points
        cells = np.full((len(points) - 1, 3), 2, dtype=np.int_)
        cells[:, 1] = np.arange(0, len(points) - 1, dtype=np.int_)
        cells[:, 2] = np.arange(1, len(points), dtype=np.int_)
        poly.lines = cells

        return poly


