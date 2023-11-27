#!/bin/bash

#source ~/openFOAM/OpenFOAM1912/OpenFOAM-v1912/etc/bashrc
source /usr/lib/openfoam/openfoam2212/etc/bashrc

np=X

echo "- - - - running decomposePar- - - -"
decomposePar -force &> logs/decomposePar.log
# decomposePar -fields &> logs/decomposePar.log <--- change in the future. First decomposition has to be done without "-fields" flag
echo "- - - - running simpleFoam - - - -"
mpirun -np $np simpleFoam &> logs/simpleFoam.log
echo "- - - - running reconstructPar - - - -"
reconstructPar simpleFoam &> logs/reconstructPar.log


