#!/bin/bash

#source ~/openFOAM/OpenFOAM1912/OpenFOAM-v1912/etc/bashrc
source /usr/lib/openfoam/openfoam2212/etc/bashrc

echo "- - - - converting STL to FMS file - - - -"
surfaceToFMS domain.stl  &> logs/surfaceToFMS.log
echo "- - - - running cfMesh- - - -"
cartesian2DMesh &> logs/cartesian2DMesh.log
echo "- - - - creating patches - - - -"
createPatch -overwrite &> logs/createPatch.log
echo "- - - - running renumberMesh - - - -"
renumberMesh -overwrite &> logs/renumberMesh.log
