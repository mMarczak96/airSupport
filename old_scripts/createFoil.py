from asyncore import write
import math
from textwrap import wrap
from traceback import print_tb
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os

projectPath = os.getcwd()
foil = 'NACA0018'

#Airfoil constants
a0 = 0.2969
a1 = -0.126
a2 = -0.3516
a3 = 0.2843
a4 = -0.1015
T = 0.18			# NACA0018
R = 2
face = 247

#number of points 
n = 100
delta_deg = 180 / n

lst_deg = np.arange(start = 0, stop = 180.000001, step = delta_deg)

foil_Pts = pd.DataFrame(lst_deg, columns = ['deg'])
foil_Pts['rad'] = foil_Pts['deg'] * 0.0174532925
foil_Pts['X'] = (1 - np.cos(foil_Pts['rad'])) / 2
foil_Pts['Y'] = T / 0.2 *( a0 * pow(foil_Pts['X'],0.5) + a1 * foil_Pts['X'] + a2 * pow(foil_Pts['X'],2) + a3 * pow(foil_Pts['X'],3) + a4 * pow(foil_Pts['X'],4) )
foil_Pts['Z'] = 0
foil_Pts['sal_form'] = 'geompy.MakeVertex( ' + foil_Pts['X'].astype(str) + ', ' + foil_Pts['Y'].astype(str) + ', ' + foil_Pts['Z'].astype(str) + " )"
salFormFoil = foil_Pts['sal_form']
SAL_foil_whole = np.array(salFormFoil)
SAL_foil = SAL_foil_whole[:-1]


nPoints_trail = 10
start_trail = 20
end_trail = 90
deg_trail = end_trail - start_trail
delta_deg_trail = deg_trail / nPoints_trail

lst_deg_trail = np.arange(start = start_trail, stop = end_trail + 0.0001, step = delta_deg_trail)
trail_Pts = pd.DataFrame(lst_deg_trail, columns = ['deg'])
trail_Pts['rad'] = trail_Pts['deg'] * 0.0174532925
trail_Pts['X'] = np.sin(trail_Pts['rad']) * ((foil_Pts['Y'].iloc[-2] + foil_Pts['Y'].iloc[-1])/2) + ((foil_Pts['X'].iloc[-2] + foil_Pts['X'].iloc[-1])/2)
trail_Pts['Y'] = np.cos(trail_Pts['rad']) * 0.00189
trail_Pts.iat[-1,3] = 0.0
trail_Pts['Z'] = 0
trail_Pts['sal_form'] = 'geompy.MakeVertex( ' + trail_Pts['X'].astype(str) + ', ' + trail_Pts['Y'].astype(str) + ', ' + trail_Pts['Z'].astype(str) + " )"
salFormTrail = trail_Pts['sal_form']
SAL_trail = np.array(salFormTrail)


fullSalFoil = np.append(SAL_foil,SAL_trail)
fullFoil = np.append(SAL_foil,SAL_trail)
x = np.append(foil_Pts['X'],trail_Pts['X'])
y = np.append(foil_Pts['Y'],trail_Pts['Y'])
plt.plot(x,y)
#plt.show()


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

np.savetxt(foil + ".py", fullFoil, fmt='%s')
prepend_line(foil + ".py", "import salome\nfrom salome.geom import geomBuilder\ngeompy = geomBuilder.New()\n")

nr_pts = np.arange(len(fullFoil))
salome_Pts = pd.DataFrame(nr_pts, columns = ['nr_pts'])
salome_Pts['vertex'] = 'vertex_' + salome_Pts['nr_pts'].astype(str)
salome_Pts['coord'] = '= ' + fullFoil
salome_Pts['vertex_curve'] = salome_Pts['vertex'].astype(str) + ','
curve = np.array(salome_Pts['vertex_curve'])
curve = np.append(curve, '], False)')
salome_Pts['add'] = 'geompy.addToStudy( ' + salome_Pts['vertex'].astype(str) + ', ' + "'" + salome_Pts['vertex'].astype(str) + "' )"

salomeFile = 'foilGen.py'
sFile = open(salomeFile, 'w')
sFile.write("import sys\n")
sFile.write("import salome\n")
sFile.write("salome.salome_init()\n")
sFile.write("import salome_notebook\n")
sFile.write("notebook = salome_notebook.NoteBook()\n")
#sFile.write("sys.path.insert(0, r'/home/maciejmarczak/myFiles/prog/foilProject')\n")
sFile.write("\n### GEOM component\n\n")
sFile.write("import GEOM\n")
sFile.write("from salome.geom import geomBuilder\n")
sFile.write("import math\n")
sFile.write("import SALOMEDS\n\n")
sFile.write("geompy = geomBuilder.New()\n\n")
sFile.write("O = geompy.MakeVertex(0, 0, 0)\nOX = geompy.MakeVectorDXDYDZ(1, 0, 0)\nOY = geompy.MakeVectorDXDYDZ(0, 1, 0)\nOZ = geompy.MakeVectorDXDYDZ(0, 0, 1)\n\n")
sFile.close()

salome_Pts[['vertex', 'coord']].to_csv(salomeFile, header=None, index=None, sep='\t', mode='a')

sFile = open(salomeFile, 'a')
sFile.write('Curve_1 = geompy.MakePolyline([ ')
sFile.close()
#salome_Pts['vertex_curve'].to_frame().T.to_csv(salomeFile, header=None, index=None, sep='\t', mode='a')
pd.DataFrame(curve).T.to_csv(salomeFile, header=None, index=None, sep='\t', mode='a')
sFile = open(salomeFile, 'a')
sFile.write('Mirror_1 = geompy.MakeMirrorByAxis(Curve_1, OX)\n')
sFile.write('Fuse_1 = geompy.MakeFuseList([Curve_1, Mirror_1], True, True)\n')
sFile.write('Translation_1 = geompy.MakeTranslation(Fuse_1, -0.5, 0, 0)\n')
sFile.write('Disk_1 = geompy.MakeDiskR(' + str(R) + ',1)\n')
sFile.write('Partition_1 = geompy.MakePartition([Translation_1, Disk_1], [], [], [], geompy.ShapeType["FACE"], 0, [], 0)\n')
sFile.write("SuppressFaces_1 = geompy.SuppressFaces(Partition_1, [" + str(face) + "])\n")
sFile.close()

#adding to the salome project
salome_Pts['add'].to_csv(salomeFile, header=None, index=None, sep='\t', mode='a')
sFile = open(salomeFile, 'a')
sFile.write('geompy.addToStudy( Curve_1, ''Curve_1'' )\n')
sFile.write("geompy.addToStudy( Mirror_1, 'Mirror_1' )\n")
sFile.write("geompy.addToStudy( Fuse_1, 'Fuse_1' )\n")
sFile.write("geompy.addToStudy( Translation_1, 'Translation_1' )\n")
sFile.write("geompy.addToStudy( Disk_1, 'Disk_1' )\n")
sFile.write("geompy.addToStudy( Partition_1, 'Partition_1' )\n")
sFile.write("geompy.ExportSTL(Partition_1, 'partition',  True, 0.0001, True)\n")
sFile.write("geompy.addToStudy( SuppressFaces_1, 'SuppressFaces_1' )\n")

sFile.close()

print(SAL_foil)