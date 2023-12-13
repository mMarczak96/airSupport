#!/bin/bash

#source ~/openFOAM/OpenFOAM1912/OpenFOAM-v1912/etc/bashrc
source /usr/lib/openfoam/openfoam2212/etc/bashrc

echo "- - - - running blockMesh - - - -"
blockMesh &> logs/blockMesh.log
echo "- - - - running surfaceFeatureExtract - - - -"
surfaceFeatureExtract &> logs/surfaceFeatureExtract.log
echo "- - - - creating patches - - - -"





echo "- - - - running renumberMesh - - - -"
renumberMesh -overwrite &> logs/renumberMesh.log
