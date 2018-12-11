# -*- coding: utf-8 -*-

import matplotlib as mpl
import numpy as np
import pandas as pd

mpl.rcParams.update({'font.size': 18})


def cutspectraldf(spectraldf, wl1 = None,wl2 = None):
    #cut up a spectral dataframe between two wavelenghts.
    wavelength = spectraldf.index
    if wl1 == None:
        wl1 = wavelength.min()
    if wl2 == None:
        wl2 = wavelength.max()
    
    idx1 = wavelength.get_loc(wl1, method = 'nearest')
    idx2 = wavelength.get_loc(wl2, method = 'nearest')

    spectra_cut = spectraldf.iloc[idx1:idx2]
    
    return spectra_cut

def maxandarea(spectra_cut):
    #calculate the area and maximum of a peak in a cut sepectral dataframe
    areas = pd.Series(index = spectra_cut.columns)
    maximums = pd.Series(index = spectra_cut.columns)

    wavelength_cut = spectra_cut.index
    for gatedelay in spectra_cut.columns:
        areas[gatedelay] = np.trapz(spectra_cut[gatedelay],wavelength_cut)
        maximums[gatedelay] = spectra_cut[gatedelay].max()      
        
    return areas, maximums

def fitdecay(spectraldf, wl1 = None, wl2 = None, wl1_fit = None, wl2_fit = None):
    #fit the log of a PL decay to a line, and return the fit line and coefficients
    spectra_cut = cutSpectraldf(spectraldf,wl1,wl2)
    areas, maximums = maxandarea(spectra_cut)
    
    if wl1_fit == None:
        wl1_fit = maximums.index.min()
    if wl2_fit == None:
        wl2_fit = maximums.index.max()
    
    idx1 = maximums.index.get_loc(wl1_fit, method = 'nearest')
    idx2 = maximums.index.get_loc(wl2_fit, method = 'nearest')
    
    gatedelays = maximums.index[idx1:idx2]
    maximums = np.log(maximums.iloc[idx1:idx2])
    
    fitcoef = np.polyfit(gatedelays,maximums,1)
    
    gatedelays_fit = np.linspace(gatedelays.min(),gatedelays.max(),100)
    fit = fitcoef[1] + fitcoef[0]*gatedelays_fit
    
    fit = np.exp(fit)
    
    return fit, gatedelays_fit, fitcoef


def PL_peakmax(data, wavelength, wlmin,wlmax):
    idx_l = find_nearest(wavelength,wlmin)
    idx_r = find_nearest(wavelength,wlmax)
    
    wavelength_cut = wavelength[idx_l:idx_r]
    
    data_cut = data[idx_l:idx_r]
    
    data_cut_max = []
    
    for frame in data_cut:
        maximum = data_cut[frame].max()
        data_cut_max = np.append(data_cut_max, maximum)
        
    return data_cut_max, wavelength_cut, data_cut

def PL_fit_powerdep(data, fits, NDF,idx_l,idx_r):
    timedata = data['Time'][NDF]
    data_p1_ln = np.log(data['Data_p1_max_norm'][NDF])
    fits['Fit_p1_param'][NDF] =np.polyfit(timedata[idx_l:idx_r], data_p1_ln[idx_l:idx_r], 1)
    fits['Fit_p1_time'][NDF] = np.linspace(timedata[idx_l], timedata[idx_r], 100)
    fits['Fit_p1'][NDF] = np.poly1d(fits['Fit_p1_param'][NDF])
    fits['Fit_p1'][NDF] = np.exp(fits['Fit_p1'][NDF](fits['Fit_p1_time'][NDF]))
    
    data_p2_ln = np.log(data['Data_p2_max_norm'][NDF]) 
    fits['Fit_p2_param'][NDF] =np.polyfit(timedata[idx_l:idx_r], data_p2_ln[idx_l:idx_r], 1)
    fits['Fit_p2_time'][NDF] = np.linspace(timedata[idx_l], timedata[idx_r], 100)
    fits['Fit_p2'][NDF] = np.poly1d(fits['Fit_p2_param'][NDF])
    fits['Fit_p2'][NDF] = np.exp(fits['Fit_p2'][NDF](fits['Fit_p2_time'][NDF]))
