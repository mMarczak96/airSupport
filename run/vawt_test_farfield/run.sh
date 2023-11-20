#!/bin/bash

#source ~/openFOAM/OpenFOAM1912/OpenFOAM-v1912/etc/bashrc
source /usr/lib/openfoam/openfoam2212/etc/bashrc

echo "- - - - converting STL to FMS file - - - -"
surfaceToFMS domain.stl 
echo "- - - - running cfMesh- - - -"
cartesian2DMesh 
echo "- - - - creating patches - - - -"
createPatch -overwrite
echo "- - - - running simpleFoam - - - -"
simpleFoam 
