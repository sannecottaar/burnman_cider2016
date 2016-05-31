# This file is part of BurnMan - a thermoelastic and thermodynamic toolkit for the Earth and Planetary Sciences
# Copyright (C) 2012 - 2015 by the BurnMan team, released under the GNU
# GPL v2 or later.


"""
_________________________________________________________________________
Practical Composition of the Lower Mantle
Part 2. Fitting velocity variations
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



# This scripts should be run with an argument that gives the step you are
# working on
step = sys.argv[1]
print(step)


#________________________________________________________________________
# STEP 1
# Plotting velocity variations.
#________________________________________________________________________

if step=='step1' or step=='step2':
    # Initialize plot
    fig = plt.figure( figsize = (15,8))
    ax = plt.subplot(111)
    
    # load 3D seismic model into dictionary
    # This model contains 2562 equally spaced profiles of shear wave velocity for the
    # model of French and Romanowicz(2015) filtered up to spherical harmonic degree 18.
    seis3D = np.load('SEMUCBWM1_Lmax18.npy').item()
    print(seis3D.keys())
    
    # plots one in ten profiles
    for prof in range(0,len(seis3D['lons']),10):
        plt.plot(seis3D['depths'],seis3D['dVs'][:,prof],'k',alpha=0.01)
    
    plt.plot(seis3D['depths'],np.max(seis3D['dVs'],axis=1),'k')
    plt.plot(seis3D['depths'],np.min(seis3D['dVs'],axis=1),'k')
    plt.xlim([660.,2891.])
    plt.xlabel('depth (km)')
    plt.ylabel('dlnVs')


#________________________________________________________________________
# STEP 2
# Modeling and plotting variations with temperature and iron content
#________________________________________________________________________

if step=='step2':
    # Compute reference velocities for pyrolite with a temperature 1900 K at the top of the lower mantle
    # We'll compute the velocities for different compositions at 20 points
    # within the lower mantle.
    depths = np.linspace(750e3, 2850e3, 40)
    # We use PREM to convert these depths to pressures.
    [pressures] = burnman.seismic.PREM().evaluate(['pressure'], depths)
    
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
    
    # Ca Perovsktie
    ca_perovskite = minerals.SLB_2011.ca_perovskite()
    
    # Pyrolitic composition
    pyr_pv = 0.75
    pyr_fp = 0.18
    pyr_capv = 0.07
    pyrolitic_mantle = burnman.Composite([mg_fe_perovskite, mg_fe_periclase, ca_perovskite], [pyr_pv, pyr_fp, pyr_capv])
    
    # To use an adiabatic temperature profile, one needs to pin the temperature at the top of the lower mantle
    T0 = 1900 #K
    temperatures = burnman.geotherm.adiabatic(pressures, T0, pyrolitic_mantle)
    
    print("Calculations are done for:")
    pyrolitic_mantle .debug_print()
    
    reference_vp, reference_vs, reference_rho = pyrolitic_mantle.evaluate(['v_p', 'v_s', 'density'], pressures, temperatures)
    
    
    # Compute variation in temperature
    deltaT = np.arange(-350.,350.01,100.)
    colorsT = [ cm.coolwarm(x) for x in np.linspace(0.,1.,len(deltaT)) ]
    
    for i, dT in enumerate(deltaT):
        T0 = 1900+dT #K
        temperatures = burnman.geotherm.adiabatic(pressures, T0, pyrolitic_mantle)
        
        print("Calculations are done for:")
        pyrolitic_mantle .debug_print()
        
        mod_vp, mod_vs, mod_rho = pyrolitic_mantle.evaluate(['v_p', 'v_s', 'density'], pressures, temperatures)
        
        dlnVs = (mod_vs-reference_vs)/ reference_vs
        #plt.subplot(2,2,1)
        plt.plot(depths/1.e3, dlnVs, color=colorsT[i], linewidth =2, label = str(dT) + ' K')
        plt.xlabel('depth (km)')
        plt.ylabel('dlnVs')



    # Compute variation in iron content
    deltaFe = np.arange(-0.21,0.2101,.06)
    colorsFe = [ cm.copper_r(x) for x in np.linspace(0.,1.,len(deltaFe)) ] # using the reversed copper scale



    for i, dFe in enumerate(deltaFe):
        # Rough partition of Fe deviation in Perovskite and Ferropericalse
        dFepv = 0.2* dFe
        dFefp = 0.8* dFe
        # Perovksite solide solution
        frac_mg = 0.94 - dFepv
        frac_fe = 0.06 + dFepv
        frac_al = 0.00
        mg_fe_perovskite = minerals.SLB_2011.mg_fe_perovskite()
        mg_fe_perovskite.set_composition([frac_mg, frac_fe, frac_al])
        
        # ferropericlase solid solution
        frac_mg = 0.8 - dFepv
        frac_fe = 0.2 + dFepv
        mg_fe_periclase = minerals.SLB_2011.ferropericlase()
        mg_fe_periclase.set_composition([frac_mg,frac_fe])
        
        # Ca Perovsktie
        ca_perovskite = minerals.SLB_2011.ca_perovskite()
        
        # Pyrolitic composition
        pyr_pv = 0.75
        pyr_fp = 0.18
        pyr_capv = 0.07
        pyrolitic_mantle = burnman.Composite([mg_fe_perovskite, mg_fe_periclase, ca_perovskite], [pyr_pv, pyr_fp, pyr_capv])
        T0 = 1900 #K
        temperatures = burnman.geotherm.adiabatic(pressures, T0, pyrolitic_mantle)
        
        print("Calculations are done for:")
        pyrolitic_mantle .debug_print()
        
        mod_vp, mod_vs, mod_rho = pyrolitic_mantle.evaluate(['v_p', 'v_s', 'density'], pressures, temperatures)
        
        dlnVs = (mod_vs-reference_vs)/ reference_vs
        #plt.subplot(2,2,2)
        plt.plot(depths/1.e3, dlnVs, color = colorsFe[i], linewidth =2, linestyle = '--', label = str(dFe) + ' % dFe ')
    plt.xlabel('depth (km)')
    plt.ylabel('dlnVs')
    plt.ylim([-0.04,0.04])
    
    # Shrink current axis by 20%
    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
    # Put legend to the right of the plot
    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))

plt.show()
