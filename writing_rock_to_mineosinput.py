# This file is part of BurnMan - a thermoelastic and thermodynamic toolkit for the Earth and Planetary Sciences
# Copyright (C) 2012 - 2015 by the BurnMan team, released under the GNU
# GPL v2 or later.


"""
_________________________________________________________________________
Writing velocities and densities to Mineos input file
_________________________________________________________________________
    

"""
# Import supporting libraries
from __future__ import absolute_import # Imports to be compatible with Python2 and Python3
from __future__ import print_function
import os, sys # Library used to interact with your operating system
import numpy as np # Library used for general array
import matplotlib.pyplot as plt # Library used for plotting
from matplotlib import cm  # Library used for colormap


# Import BurnMan
sys.path.insert(1, os.path.abspath('./burnman-0.9.0/')) # add path to burnman
import burnman
from burnman import minerals


def write_mineos_input(rock, min_depth = 670.e3, max_depth = 2890.e3, name = 'burnmantestrock'):

    # Load reference input
    lines = open('mineos_prem_noocean.txt').readlines()
    table =[]
    for line in lines[3:]:
        numbers = np.fromstring(line, sep=' ')
        table.append(numbers)
    table = np.array(table)
    ref_radius = table[:,0]
    ref_depth = 6371.e3 -ref_radius
    ref_density = table[:,1]
    ref_vpv = table[:,2]
    ref_vsv = table[:,3]
    ref_Qk = table[:,4]
    ref_Qmu = table[:,5]
    ref_vph = table[:,6]
    ref_vsh = table[:,7]
    ref_eta = table[:,8]

    # Cutting out range to input in Mineos (currently the lower mantle)
    indrange = [x for x in range(len(ref_depth)) if ref_depth[x]> min_depth and ref_depth[x] < max_depth]
    # pad both ends to include up to discontinuity, bit of a hack...
    indrange.insert(0,indrange[0]-1)
    indrange.append(indrange[-1]+1)
    depthrange = ref_depth[indrange][::-1]# Invert depthrange so adiabatic computations work!

    # convert depths to pressures
    pressures = burnman.seismic.PREM().pressure(depthrange)

    # Computing adiabatic temperatures. T0 is a choice!
    T0 = 1900 #K
    temperatures = burnman.geotherm.adiabatic(pressures, T0, rock)
    
    print("Calculations are done for:")
    rock.debug_print()
    
    rock_vp, rock_vs, rock_rho = rock.evaluate(['v_p', 'v_s', 'density'], pressures, temperatures)


    # WRITE OUT FILE
    f=open('mineos_' + name + '.txt','w')
    f.write(lines[0][:-2]+' +  '+ name +'\n')
    for line in lines[1:3]:
        f.write(line[:-2]+'\n')
    for i in range(indrange[0]):
        f.write('%8.0f %9.2f %9.2f %9.2f %9.1f %9.1f %9.2f %9.2f %9.5f \n' %( ref_radius[i], ref_density[i],
                                                                                ref_vpv[i], ref_vsv[i], ref_Qk[i], ref_Qmu[i], ref_vph[i], ref_vsh[i], ref_eta[i]))
    for i in range(indrange[0],indrange[-1]):
        ind2=-1-i+indrange[0]
        f.write('%8.0f %9.2f %9.2f %9.2f %9.1f %9.1f %9.2f %9.2f %9.5f \n' %( ref_radius[i], rock_rho[ind2],
                                                                         rock_vp[ind2], rock_vs[ind2], ref_Qk[i], ref_Qmu[i], rock_vp[ind2], rock_vs[ind2], ref_eta[i]))
    for i in range(indrange[-1],len(ref_radius)):
        f.write('%8.0f %9.2f %9.2f %9.2f %9.1f %9.1f %9.2f %9.2f %9.5f \n' %( ref_radius[i], ref_density[i],
                                                                         ref_vpv[i], ref_vsv[i], ref_Qk[i], ref_Qmu[i], ref_vph[i], ref_vsh[i], ref_eta[i]))
    f.close()

