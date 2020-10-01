import os
import sys
import gc
import numpy as np
import pandas as pd
import re
import math
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
match_number = re.compile('-?\ *[0-9]+\.?[0-9]*(?:[Ee]\ *-?\ *[0-9]+)?')

nu = 1e-6 #kinematic viscosity of water
rho = 1000 #density of water
mu = nu*rho #dynamic viscosity of water

'''
Due to the volume integrals being extemely expensive to both store and process,
combined with the fact that the contributions of the volume integrals are
several orders of magnitude lower than the surface integrals,
the decision has been made to remove the calculation of the volume integrals
from this script.  If it's deemed necessary it can be added back in at a later date.
'''

def main():

    t_max = float(sys.argv[1])
    delta_t = float(sys.argv[2])

    t, i, v, s = calcDragOverTime(t_max=t_max, delta_t=delta_t)




def surface_integrand(row):
    '''
    this method works out the vector which is used as the integrand for the surface integrals.

    It also multiplies it by the area of the cell so we can then sum the integrands up
    to approximate the surface integral.
    '''
    gradU = row['grad_U'].reshape(3, 3) #velocity gradient matrix
    norm_v = row['normals'] #surface normal vector
    p = row['p'] #pressure
    area = row['Area'] #cell area

    sigma = mu*(gradU + gradU.T) - p*np.identity(3)
    return (sigma@norm_v)*area


def volume_integrand(row):
    '''
    this method calculates the vector used as the integrand for the volume integrals.

    also multiplies it
    '''
    U = row['U']
    dUdt = row['dUdt']
    gradU = row['grad_U'].reshape(3, 3)
    V = row['Volume']

    #multiply each column of gradU.T by the corresponding U value
    #first column by u, second by v etc.
    r = U*gradU.T #first step of calculating (U.grad)U

    #axis = 1 to sum up the rows
    UgradU = np.sum(r, axis=1) #second step of calculating (U.grad)U

    return (dUdt + UgradU)*V


def calcDragOverTime(t_max, delta_t):
    '''
    master method to calculate the drag integrals.
    calculates the total, surface and volume integrals for each timestep then saves them to a file
    '''
    t_list = []
    TI_vectors = [] #list to hold the vectors calculated from the total integrals
    VI_vectors = [] #list to hold the vectors calculated from the volume integrals
    SI_vectors = [] #list to hold the vectors calculated from the surface integrals

    #have 3 different files for writing
    #total integral and the surface/volume contributions seperately
    total_integral_filename = 'integral_results/drag_over_time.csv'
    volume_integral_filename = 'integral_results/volumeIntegral_DOT.csv'
    surface_integral_filename = 'integral_results/surfaceIntegral_DOT.csv'

    #with open(total_integral_filename, 'w+') as TI_file, open(volume_integral_filename, 'w+') as VI_file, open(surface_integral_filename, 'w+') as SI_file:
    #removed the volume integral file
    with open(total_integral_filename, 'w+') as TI_file, open(surface_integral_filename, 'w+') as SI_file:

        TI_file.write('t, F_x, F_y, F_z\n')
        VI_file.write('t, F_x, F_y, F_z\n')
        SI_file.write('t, F_x, F_y, F_z\n')

        for t in np.arange(delta_t, t_max+delta_t, delta_t):
            t_string = "{:.1f}".format(t)
            print(t_string)

            #read in data
            df_surface = pd.read_csv('surface_data/surface_data-t='+t_string+'.csv')
            #no longer reading in volume integral
            #df_volume = pd.read_csv('volume_data/volume_data-t='+t_string+'.csv')

            #combine seperate component into arrays
            df_surface['grad_U'] = df_surface[['grad(U):0', 'grad(U):1', 'grad(U):2', 'grad(U):3', 'grad(U):4', 'grad(U):5', 'grad(U):6', 'grad(U):7', 'grad(U):8']].values.tolist()
            df_surface['grad_U'] = df_surface['grad_U'].apply(np.array)
            df_surface['normals'] = df_surface[['Normals:0', 'Normals:1', 'Normals:2']].values.tolist()
            df_surface['normals'] = df_surface['normals'].apply(np.array)

            # df_volume['grad_U'] = df_volume[['grad(U):0', 'grad(U):1', 'grad(U):2', 'grad(U):3', 'grad(U):4', 'grad(U):5', 'grad(U):6', 'grad(U):7', 'grad(U):8']].values.tolist()
            # df_volume['grad_U'] = df_volume['grad_U'].apply(np.array)
            # df_volume['dUdt'] = df_volume[['dUdt:0', 'dUdt:1', 'dUdt:2']].values.tolist()
            # df_volume['dUdt'] = df_volume['dUdt'].apply(np.array)
            # df_volume['U'] = df_volume[['U:0', 'U:1', 'U:2']].values.tolist()
            # df_volume['U'] = df_volume['U'].apply(np.array)

            #caluclate the integrands
            df_surface['surface_integrand']=df_surface.apply(surface_integrand, axis=1)
            #df_volume['volume_integrand']=df_volume.apply(volume_integrand, axis=1)

            #sum everything up to calculate the integrals
            surf_int = df_surface['surface_integrand'].sum()
            #vol_int = df_volume['volume_integrand'].sum()

            #changed the + to a - here as discussed
            #total_int = vol_int - surf_int
            #volume integral no longer calculated
            total_int = -surf_int

            #append to list and save to file
            t_list.append(t)
            TI_vectors.append(total_int)
            #VI_vectors.append(vol_int)
            SI_vectors.append(surf_int)

            TI_data_string = "{:.3f}, {:.5e}, {:.5e}, {:.5e}\n".format(t, total_int[0], total_int[1], total_int[2])
            #VI_data_string = "{:.3f}, {:.5e}, {:.5e}, {:.5e}\n".format(t, vol_int[0], vol_int[1], vol_int[2])
            SI_data_string = "{:.3f}, {:.5e}, {:.5e}, {:.5e}\n".format(t, surf_int[0], surf_int[1], surf_int[2])

            TI_file.write(TI_data_string)
            #VI_file.write(VI_data_string)
            SI_file.write(SI_data_string)

            #not sure if this does anything, but just in case this should hopefully free up some memory
            del df_surface#, df_volume
            gc.collect()

    #return t_list, TI_vectors, VI_vectors, SI_vectors
    return t_list, TI_vectors, SI_vectors


main()
