#!/bin/bash

#source ~/openFOAM/OpenFOAM1912/OpenFOAM-v1912/etc/bashrc
source /usr/lib/openfoam/openfoam2212/etc/bashrc

echo "- - - - running mapFields - - - -"
mapFields -consistent -sourceTime latestTime  fields/mapFieldsTemplate/ &> logs/mapFields.log
