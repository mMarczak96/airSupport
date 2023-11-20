#!/bin/bash

#source ~/openFOAM/OpenFOAM1912/OpenFOAM-v1912/etc/bashrc
source /usr/lib/openfoam/openfoam2212/etc/bashrc

np=X

echo "- - - - running decomposePar- - - -"
decomposePar -fields &> logs/decomposePar.log

echo "- - - - running simpleFoam - - - -"
mpirun -np $np simpleFoam &> logs/simpleFoam.log

echo "- - - - running reconstructPar - - - -"
reconstructPar simpleFoam &> logs/reconstructPar.log


