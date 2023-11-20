from asyncio import subprocess
from cgitb import reset
from telnetlib import NAOVTD
from subprocess import PIPE, run
from traceback import print_tb
from turtle import filling
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os
from airfoil import Airfoil
import argparse
import settings
import pyvista as pv
import geometry as geom
import mesh 
import pathlib
import subprocess
import physics
import postProc 
import VAWT
from icecream import ic

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--foil', help='airfoil code', required=True)                                  
    parser.add_argument('-a', '--actions', nargs='+',help='Actions type [foil, AoA_single, AoA_range, VAWT]', required=True,)
    args = parser.parse_args()

    return args

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

cwd = os.getcwd()

if __name__ == '__main__':
    
    args = parse_args()
    foil = args.foil
    actions = args.actions
    Re = physics.Re(settings.ro, settings.Uinlet, settings.c, settings.visc)

    for action in actions:

        if action == 'foil':

            print('----------------------------------------------------------------------------------------')
            print(f'Creating NACA{foil} geometry')
            print('----------------------------------------------------------------------------------------')

            # Re = physics.Re(settings.ro, settings.Uinlet, settings.c, settings.visc)
            A = float(f'0.{foil[0]}{foil[1]}')
            T = float(f'0.{foil[2]}{foil[3]}')
            Naca = Airfoil('NACA{}'.format(foil), settings.A, settings.T, settings.N)
            plus = Naca.foil_cords_plus(settings.A, settings.T, settings.N)
            # min = Naca.foil_cords_min(settings.A, settings.T, settings.N)
            te = Naca.roundedTE(settings.NT, settings.ST, settings.ET, plus)

            up = pd.concat([plus, te])    
            down = pd.concat([plus, te])    

            down['Y'] = down['Y'] * (-1)
            down = down.iloc[::-1]
                        
            cords, PTS = Naca.mergeFoilPts(up, down)
            plt.scatter(PTS['X'],PTS['Y'])
            Naca.create_STL_foil(cords)

            c=1
            geom.sides(c, 'Sides')
            geom.arcInlet(c, 'Inlet')
            geom.outlet(c, 'Outlet')
            geom.groupedSTLdomain(f'NACA{foil}','Inlet','Sides','Outlet')
            
            file_path = f"/home/maciek/repository/airSupport/geometry/domain_NACA{foil}.stl"

            # Step 1: Open the text file in read mode
            with open(file_path, 'r') as file:
                # Step 2: Read the contents of the file
                content = file.read()

            # Step 3: Replace all commas with dots
            modified_content = content.replace(',', '.')

            # Step 4: Open the same file in write mode
            with open(file_path, 'w') as file:
                # Step 5: Write the modified contents back into the file
                file.write(modified_content)    
            


        if action == 'AoA_single':

            print('----------------------------------------------------------------------------------------')
            print(f'Starting single angle of attack simulation. AoA range: {settings.AoA_single}, Re: {Re}, Turbulence model: {settings.turbModel}')
            print('----------------------------------------------------------------------------------------')

            copyOFtemp = f'cp -r {cwd}/template {cwd}/run'
            changeOFdir = f'mv {cwd}/run/template {cwd}/run/NACA{foil}_AoA{settings.AoA_single}_{settings.turbModel}'
            run_cmd(copyOFtemp)
            run_cmd(changeOFdir)
            mesh.create_cfMeshDict(False, f'NACA{foil}')
            os.system('cp {}/geometry/domain_NACA{}.stl {}/run/NACA{}'.format(cwd, foil, cwd, foil))
            os.system('mv {}/run/NACA{}/domain_NACA{}.stl {}/run/NACA{}/domain.stl'.format(cwd,foil,foil,cwd,foil))
            os.system('sed -i "/internalField   uniform (0 0 0);/c internalField   uniform ({} 0 0); " {}/run/NACA{}/0/U'
                .format(settings.Uinlet, cwd, foil))
            os.system('cd run/NACA{} && ./run_mesh.sh'.format(foil))
            os.system('cd run/NACA{} && ./run_simulation.sh'.format(foil))

            #Postprocessing stage
            postProc.plot_OF_aero_postProc(foil,'steady')
            postProc.aeroData_to_HDF(foil, int(Re), settings.Type, settings.turbModel)


        if action == 'AoA_range':

            print('----------------------------------------------------------------------------------------')
            print(f'Starting multiple angle of attack simulation. AoA range: {settings.AoA_range}, Re: {Re}, Turbulence model: {settings.turbModel}')
            print('----------------------------------------------------------------------------------------')

            AoA_dir = f'{cwd}/run/NACA{foil}_AoA[{settings.AoA_range.min()}-{settings.AoA_range.max()}]_{settings.turbModel}'
            # os.system(f'mkdir {AoA_dir}')
            # copyOFtemp = f'cp -r {cwd}/template {AoA_dir}'
            copyOFtemp = f'cp -r {cwd}/template {cwd}/run'
            run_cmd(copyOFtemp)
            changeOFdir = f'mv run/template {AoA_dir}'
            run_cmd(changeOFdir)

            # Calculate AoA velocity BC df
            AoA_df = pd.DataFrame(settings.AoA_range, columns=['AoA'])
            AoA_df['Ux'] = settings.Uinlet * np.cos(np.deg2rad(AoA_df['AoA']))
            AoA_df['Uy'] = settings.Uinlet * np.sin(np.deg2rad(AoA_df['AoA'])) * (-1)

            # Meshing and preprocessing
            mesh.create_cfMeshDict(True, f'NACA{foil}', AoA_dir)
            os.system(f'cp {cwd}/geometry/domain_NACA{foil}.stl {AoA_dir}/')
            os.system(f'mv {AoA_dir}/domain_NACA{foil}.stl {AoA_dir}/domain.stl')
            os.system(f'cd {AoA_dir} && ./run_mesh.sh')

            os.system(f'mkdir -p {AoA_dir}/fields/mapFieldsTemplate')
            os.system(f'cp -r {AoA_dir}/constant {AoA_dir}/fields/mapFieldsTemplate/ && cp -r {AoA_dir}/system {AoA_dir}/fields/mapFieldsTemplate/')

            counter = 0
            map_time_dir = 0
            for i in AoA_df['AoA']:
                print(f'---------- Begining calculation for AoA: {i} deg')

                os.system('sed -i "/internalField   uniform (0 0 0);/c internalField   uniform ({} {} 0); " {}/0/U'.format(AoA_df['Ux'][counter],AoA_df['Uy'][counter],AoA_dir))
                # Mapping from lower AoA fields
                if settings.mapFields == True and counter > 0:
                    print('Starting mapping from the previous AoA field')
                    os.system(f'cd {AoA_dir} && ./run_mapFields.sh')
                    os.system(f' rm -r {AoA_dir}/fields/mapFieldsTemplate/{map_time_dir}')
                    # for BC_dict in os.walk(f'{AoA_dir}/0'):
                    #     os.system(f'gunzip {AoA_dir}/0/{BC_dict}.gz ')
                    # os.system(f'mv {AoA_dir}/logs/mapFields.log {AoA_dir}/logs/mapFields_[{i}].log')

                if settings.parallel == True:
                    os.system('sed -i "/numberOfSubdomains X;/c numberOfSubdomains {}; " {}/system/decomposeParDict'.format(settings.NP,AoA_dir))
                    os.system('sed -i "/np=X/c np={} " {}/run_Parallelsimulation.sh'.format(settings.NP,AoA_dir))
                    os.system(f'cd {AoA_dir} && ./run_Parallelsimulation.sh')
                    # os.system(f'rm -r {AoA_dir}/processor*')
                else:
                    os.system(f'cd {AoA_dir} && ./run_simulation.sh')
                    # os.system(f'mv {AoA_dir}/logs/simpleFoam.log {AoA_dir}/logs/simpleFoam_[{i}].log')
                
                logFiles = ['decomposePar.log', 'mapFields.log', 'simpleFoam.log', 'reconstructPar.log']
                for log in logFiles:
                    os.system(f'mv {AoA_dir}/logs/{log} {AoA_dir}/logs/[{i}]_{log}')
                
                os.system(f'mv {AoA_dir}/postProcessing/forceCoeffs1/0/coefficient.dat {AoA_dir}/postProcessing/forceCoeffs1/0/coefficient_[{i}].dat')

                def is_all_digits(s):
                    return s.isdigit()
                
                field_list = []

                for dirpath, dirnames, filenames in os.walk(AoA_dir):
                    # if 'fields' in dirnames:
                    #     dirnames.remove('fields')
                    for dir in ['template', 'fields', 'test']:
                        if dir in dirnames:
                            dirnames.remove(dir)

                    for dirname in dirnames:
                        
                        if is_all_digits(dirname):
                            # print(f"Found directory with only numbers: {os.path.join(dirpath, dirname)}")
                            field = int(dirname)
                            field_list.append(field)

                print(field_list)
                max_time_dir = max(field_list)
                print(max_time_dir)
                if max_time_dir == 0:
                    print("Cannot move 0 directory")
                else:
                    os.system(f'mkdir {AoA_dir}/fields/AoA_[{i}] && mv {AoA_dir}/{str(max_time_dir)} {AoA_dir}/fields/AoA_[{i}]/')
                    os.system(f'cp -r {AoA_dir}/fields/AoA_[{i}]/{str(max_time_dir)} {AoA_dir}/fields/mapFieldsTemplate/')
                    map_time_dir = max_time_dir
                counter += 1

            os.system(f'rm -r {AoA_dir}/fields/mapFieldsTemplate')
            os.system(f'rm -r {AoA_dir}/processor*')

        if action == 'VAWT':

            #Geometry and mesh generation
            
            if settings.VAWT_geom_type not in settings.VAWT_geom_type_list:
                print(f'Invalid VAWT type: {settings.VAWT_geom_type} !!! Please check the program settings ')
            else:
                if settings.VAWT_geom_type == 'savonius':

                    print('----------------------------------------------------------------------------------------')
                    print(f'Creating geometry for Savonius VAWT:\nShaft d: {settings.sav_d_shaft}m, inner d: {settings.sav_d_in}m, outer d: {settings.sav_d_out}m, distance: {settings.sav_dist}m')
                    print('----------------------------------------------------------------------------------------')
                    VAWT_name = f'{settings.VAWT_geom_type}_out{settings.sav_d_out}_in{settings.sav_d_in}_s{settings.sav_d_shaft}_d{settings.sav_dist}'
                    #Geometry part:
                    geom.VAWT_domain(settings.sav_d_out, 20, 30, 15, VAWT_name)
                    geom.savoniusVAWT(settings.sav_d_shaft/2, settings.sav_d_in/2, settings.sav_d_out/2, settings.sav_dist, VAWT_name)
                    #Mesh part:
                    VAWT_run_dir = f'{cwd}/run/{VAWT_name}'
                    command_list = [
                        f'mkdir -p {VAWT_run_dir}',
                        f'cp -r {cwd}/template_VAWT {cwd}/run/{VAWT_name} && mv {VAWT_run_dir}/template_VAWT {VAWT_run_dir}/domain',
                        f'cp {VAWT_run_dir}/domain/domain_farfield.stl {VAWT_run_dir}/domain',
                        f'cp -r {cwd}/template_VAWT {VAWT_run_dir} && mv {VAWT_run_dir}/template_VAWT {VAWT_run_dir}/rotor ',
                        f'cp {cwd}/geometry/{VAWT_name}/rotor/domain_rotor.stl {VAWT_run_dir}/rotor',
                        f'mv {VAWT_run_dir}/domain/system/createPatchDict_domain {VAWT_run_dir}/domain/system/createPatchDict',
                        f'mv {VAWT_run_dir}/rotor/system/createPatchDict_rotor {VAWT_run_dir}/domain/system/createPatchDict'
                        f'./{VAWT_run_dir}/domain/run_mesh.sh'
                    ]
                    for command in command_list:
                        run_cmd(command)

