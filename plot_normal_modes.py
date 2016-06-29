# This file is part of BurnMan - a thermoelastic and thermodynamic toolkit for the Earth and Planetary Sciences
# Copyright (C) 2012 - 2015 by the BurnMan team, released under the GNU
# GPL v2 or later.


"""
_________________________________________________________________________
Practical Composition of the Lower Mantle
Comparing eigenfrequencies between synthetics and/or synthetics and data

First argument: Type of plot, choose from 
    'dispersion_curve', 'quality_factor', 'compare_with_data'
Second argument: Choose modes to look at
    'S' (spheroidal), 'T' (toroidal), 'R' (radial)
Third and other arguments: model names to be plotted, e.g. 'prem_noocean' (output files from mineos need to be present in the directory, e.g. prem_noocean_R.out.

For example
    python plot_normal_modes.py compare_with_data S pyrolite prem_noocean
_________________________________________________________________________


"""
# Import supporting libraries
from __future__ import absolute_import # Imports to be compatible with Python2 and Python3
from __future__ import print_function
import os, sys # Library used to interact with your operating system
import numpy as np # Library used for general array
import matplotlib.pyplot as plt # Library used for plotting
from matplotlib import cm  # Library used for colormap


# Subroutine that reads the synthetic results
def read_mineos_output(model, component):
    filename = model + '_' + component + '.out'
    datastream = open(filename,'r')
    datalines = [line for line in datastream.readlines() if line.strip()]
    overtone_number =[]
    angular_order = []
    frequency = []
    inv_Q =[]
    for line in datalines:
        val = line.split()
        if (val[0] != '#'):
            overtone_number.append(int(val[0]))
            angular_order.append(int(val[2]))
            frequency.append(float(val[3]))
            inv_Q.append((1000./float(val[4])))
    return np.array(overtone_number),np.array(angular_order), np.array(frequency), np.array(inv_Q)

# Subroutine that reads the measured eigenfrequencies
def read_data(component):
    filename = 'mes_' + component + '.dat'
    datastream = open(filename,'r')
    datalines = [line for line in datastream.readlines() if line.strip()]
    overtone_number =[]
    angular_order = []
    frequency = []
    microerror =[]
    for line in datalines:
        val = line.split()
        if (val[0] != '#'):
            overtone_number.append(int(val[0]))
            angular_order.append(int(val[2]))
            frequency.append(float(val[3]))
            try:
                microerror.append((float(val[4])))
            except:
                microerror.append(np.nan)
    return np.array(overtone_number),np.array(angular_order), np.array(frequency), np.array(microerror)

plot = sys.argv[1]
models_to_plot = sys.argv[3:]
component = sys.argv[2]

if plot == 'dispersion_curve':
    """
    Plots angular order vs frequency for the models given and for observations.
    """
    plot_data = False
    for model_to_plot in models_to_plot:
        overtone_number, angular_order,frequency, inv_Q = read_mineos_output(model_to_plot,component)
        plt.plot(angular_order,frequency, '.', markersize=10, label = model_to_plot)
    if plot_data:
        overtone_number, angular_order,frequency, error = read_data(component)
        plt.plot(angular_order,frequency, 'dk', markersize=5, label = 'selected data')
    plt.legend()
    plt.xlabel('Angular order (l)')
    plt.ylabel('Frequency (mHz)')

if plot == 'quality_factor':
    """
    Plots frequency vs. quality factor (no observations)
    """
    for model_to_plot in models_to_plot:
        overtone_number, angular_order,frequency, inv_Q = read_mineos_output(model_to_plot,component)
        plt.plot(frequency, inv_Q, '.', markersize=10, label = model_to_plot)
    plt.legend()
    plt.ylabel('Inverse of quality factor (1000/Q)')
    plt.xlabel('Frequency (mHz)')

if plot == 'compare_with_data':
    """
    Plots differences in eigenfrequency between different models and the observations for different values of overtone number and angular order
    """
    nmin=0  # minimum overtone number to be plotted
    nmax=8 # maximum overtone number to be plotted
    lmax=25 # maximum angular order to be plotted
    colors=['.r','.b','.g','.c'] # colors to use for the different models
    f, axarr = plt.subplots(nmax+1-nmin, sharex=True,sharey=True,figsize=(7,8))
    f.subplots_adjust(hspace=0)
    # Read in observed values
    overtone_number_ref, angular_order_ref,frequency_ref, error_ref = read_data(component)
    for m, model_to_plot in enumerate(models_to_plot):
        # Read in computed values
        overtone_number_syn, angular_order_syn,frequency_syn, inv_Q_syn = read_mineos_output(model_to_plot,component)
        l=0
        # Loop through and plot if there is an observed value
        for i in range(len(overtone_number_syn)):
            if overtone_number_syn[i] >= nmin and overtone_number_syn[i] <= nmax and angular_order_syn[i] <= lmax :
                ind = [ n for n in range(len(overtone_number_ref)) if (overtone_number_ref[n]== overtone_number_syn[i] and angular_order_ref[n] == angular_order_syn[i])]
                if len(ind)>0:
                    l=l+1
                    plotind = int(overtone_number_syn[i]) - nmin
                    axarr[plotind].plot(angular_order_syn[i], frequency_syn[i]-frequency_ref[ind[0]],colors[m],markersize=10, label=model_to_plot if l == 1 else "")
                    axarr[plotind].plot([0-0.2, lmax+0.2],[0,0], '--k')
                    axarr[plotind].text(22,0.04, 'n = ' +str(int(overtone_number_syn[i])))
        axarr[0].legend(bbox_to_anchor=(.8, 1.75))
        axarr[nmax-nmin].set_xlabel('Angular order (l)')
        axarr[round((nmax-nmin)/2.)].set_ylabel('Frequency difference (mHz)')
        plt.ylim([-0.08, 0.08])
        plt.xlim([-0.2, lmax+0.2])
        plt.gca().set_yticks([-0.05,0,0.05])



plt.show()
