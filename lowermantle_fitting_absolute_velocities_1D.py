# This file is part of BurnMan - a thermoelastic and thermodynamic toolkit for the Earth and Planetary Sciences
# Copyright (C) 2012 - 2015 by the BurnMan team, released under the GNU
# GPL v2 or later.


"""
_________________________________________________________________________
Practical Composition of the Lower Mantle
Part 1. Fitting 1D absolute velocities
_________________________________________________________________________


"""
# Import supporting libraries
from __future__ import absolute_import # Imports to be compatible with Python2 and Python3
from __future__ import print_function
import os, sys # Library used to interact with your operating system
import numpy as np # Library used for general array
import matplotlib.pyplot as plt # Library used for plotting
from matplotlib import cm  # Library used for colormap
import pickle # Library used to read in 3D seismic file
import writing_rock_to_mineosinput
# Import BurnMan
sys.path.insert(1, os.path.abspath('./burnman-0.9.0/')) # add path to burnman
import burnman
from burnman import minerals # import mineral library seperately



# This scripts should be run with an argument that gives the step you are
# working on
step = sys.argv[1]
print(step)


#________________________________________________________________________
# STEP 1
#________________________________________________________________________

if step == 'step1' or step == 'step2':
    # List of seismic 1D models
    seismic_models = [
        burnman.seismic.PREM(),
        burnman.seismic.STW105(),
        burnman.seismic.AK135()]
    # Colors used to plot models
    colors = ['r', 'b', 'm', 'k']
    # Start figure
    plt.figure(figsize=(14, 5))

    # Run through models and variables
    for m in range(len(seismic_models)):
        # get depths at which the model is defined
        depths = seismic_models[m].internal_depth_list(
            mindepth=0, maxdepth=6371e3)
        # Retrieve Vp, Vs and density from the seismic models.
        Vp, Vs, rho = seismic_models[m].evaluate(
            ['v_p', 'v_s', 'density'], depths)

        # PLOTTING the results. While all parameters from BurnMan are given in
        # SI units (e.g. m/s for velocity), they are here converted to other
        # units for plotting purposes.
        plt.subplot(1, 3, 1)
        plt.plot(depths / 1.e3, Vp / 1.e3, color=colors[m], linestyle='-')
        plt.subplot(1, 3, 2)
        plt.plot(depths / 1.e3, Vs / 1.e3, color=colors[m], linestyle='-')
        plt.subplot(1, 3, 3)
        plt.plot(depths / 1.e3, rho / 1.e3, color=colors[m], linestyle='-',
            label=seismic_models[m].__class__.__name__)

    # Beautify plots. The values are bounded to only show the lower mantle,
    # but feel free to play around with this to see the rest of the planet.
    plt.subplot(1, 3, 1)
    plt.xlabel('depth in km')
    plt.ylabel('Vp in km/s')
    plt.xlim([750., 2700.])
    plt.ylim([10.5, 14.])
    plt.subplot(1, 3, 2)
    plt.xlabel('depth in km')
    plt.ylabel('Vs in km/s')
    plt.xlim([750., 2700.])
    plt.ylim([6., 7.5])
    plt.subplot(1, 3, 3)
    plt.xlabel('depth in km')
    plt.ylabel('density in kg/m^3 ')
    plt.xlim([750., 2700.])
    plt.ylim([4., 5.5])
    plt.legend(loc=2, borderaxespad=0.)


#________________________________________________________________________
# STEP 2
#________________________________________________________________________

if step == 'step2':

    # We'll compute the velocities for different compositions at 20 points
    # within the lower mantle. Here we define the array of those depths.
    depths = np.linspace(750e3, 2700e3, 20)
    # We use PREM to convert these depths to pressure values.
    [pressures] = seismic_models[0].evaluate(['pressure'], depths)
    
    """
    -Defining the rock-
    
    The object burnman.Composite expects two lists, one with the minerals
    themselves and one with the molar fractions of the different minerals 
    making up the rock
    
    
    Here we test the models for a Pyrolitic and Chondritic lower mantle. 
    
    
    """
    
    
    # Perovksite solide solution
    frac_mg = 0.94
    frac_fe = 0.06
    frac_al = 0.00
    mg_fe_perovskite = minerals.SLB_2011.mg_fe_perovskite()
    mg_fe_perovskite.set_composition([frac_mg, frac_fe, frac_al])

    # ferropericlase solid solution
    frac_mg = 0.8
    frac_fe = 0.2
    mg_fe_periclase = minerals.SLB_2011.ferropericlase()
    mg_fe_periclase.set_composition([frac_mg,frac_fe])
    
    # Ca Perovskite
    ca_perovskite = minerals.SLB_2011.ca_perovskite()
    
    # Pyrolitic composition
    pyr_pv = 0.75
    pyr_fp = 0.18
    pyr_capv = 0.07
    pyrolitic_mantle = burnman.Composite(
        [mg_fe_perovskite, mg_fe_periclase, ca_perovskite], [pyr_pv, pyr_fp, pyr_capv])


    # Chondritic composition
    chon_pv = 0.88
    chon_fp = 0.05
    chon_capv = 0.07
    chondritic_mantle = burnman.Composite(
        [mg_fe_perovskite, mg_fe_periclase, ca_perovskite], [chon_pv, chon_fp, chon_capv])


    # To use an adiabatic temperature profile, one needs to pin the temperature at the top of the lower mantle
    T0 = 1900 #K
    temperatures = burnman.geotherm.adiabatic(pressures, T0, pyrolitic_mantle)
    # An alternative is the Brown+Shankland (1981)
    # geotherm for mapping pressure to temperature.
    # To use this include the line below.
    #temperature = burnman.geotherm.brown_shankland(pressure)


    print("Calculations are done for:")
    pyrolitic_mantle .debug_print()

    pyrolitic_vp, pyrolitic_vs, pyrolitic_rho = pyrolitic_mantle.evaluate(
        ['v_p', 'v_s', 'density'], pressures, temperatures)
    chondritic_vp, chondritic_vs, chondritic_rho = chondritic_mantle.evaluate(
        ['v_p', 'v_s', 'density'], pressures, temperatures)


    # writing mineos input!
    writing_rock_to_mineosinput.write_mineos_input(pyrolitic_mantle, name = 'pyrolite')
    writing_rock_to_mineosinput.write_mineos_input(chondritic_mantle, name = 'chondrite')

    # PLOTTING

    # plot vp
    plt.subplot(1, 3, 1)
    plt.plot(depths / 1.e3, pyrolitic_vp / 1.e3, color='g', linestyle='-', marker='o',
             markerfacecolor='g', markersize=4, label='pyrolitic mantle')
    plt.plot(depths / 1.e3, chondritic_vp / 1.e3, color='y', linestyle='-', marker='o',
             markerfacecolor='y', markersize=4, label='chondritic mantle')
    plt.legend(loc='lower right')

    # plot Vs
    plt.subplot(1, 3, 2)
    plt.plot(depths / 1.e3, pyrolitic_vs / 1.e3, color='g', linestyle='-', marker='o',
             markerfacecolor='g', markersize=4)
    plt.plot(depths / 1.e3, chondritic_vs / 1.e3, color='y', linestyle='-', marker='o',
             markerfacecolor='y', markersize=4)

    # plot density
    plt.subplot(1, 3, 3)
    plt.plot(depths / 1.e3, pyrolitic_rho / 1.e3, color='g', linestyle='-', marker='o',
             markerfacecolor='g', markersize=4)
    plt.plot(depths / 1.e3, chondritic_rho / 1.e3, color='y', linestyle='-', marker='o',
             markerfacecolor='y', markersize=4)

plt.show()
