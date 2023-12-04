#!/bin/bash

source /usr/lib/openfoam/openfoam2212/etc/bashrc

echo "- - - - running blockMesh - - - -"
blockMesh  &> logs/blockMesh.log
echo "- - - - running renumberMesh - - - -"
renumberMesh -overwrite &> logs/renumberMesh.log
echo "- - - - running checkMesh - - - -"
checkMesh  &> logs/checkMesh.log

