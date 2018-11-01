# -*- coding: utf-8 -*-


import matplotlib as mpl
import numpy as np
from nptdms import TdmsFile as TF
import spe_loader as sl
import pandas as pd

from mhdpy.post.spe import _get_gatedelays

mpl.rcParams.update({'font.size': 18})


def spe2df_spect(spefilepath, gatingtype = 'rep'):
    #convert a sequential spectral SPE file to a pandas dataframe with one axis wl and other axis gate delay.
    spe_file = sl.load_from_files([spefilepath])

    frames  = spe_file.data
    gatedelays = _get_gatedelays(spe_file)
    wavelength = spe_file.wavelength
    
    datamatrix = np.zeros((len(wavelength),len(gatedelays)))
    
    i = 0
    for frame in frames:
        datamatrix[:,i] = frame[0]
        i = i+1
    if gatingtype == 'rep':
        spectraldf = pd.DataFrame(datamatrix, index = wavelength)
    elif gatingtype == 'seq':
        spectraldf = pd.DataFrame(datamatrix, index = wavelength, columns = gatedelays)
    
    return spectraldf



def getlaserdata():
    #pull the laser profile from a specific tdms file. The format of this tdms file is likely only used once
    pathnames_laser= _get_pathnames("C:\\Users\\aspit\\OneDrive\\Data\\LaserProfile")
    file_laser = TF(pathnames_laser['Test1_20Hz.tdms'])
    
    laser_common = file_laser.object('Raw').as_dataframe()
    laser_data = file_laser.object('Average').as_dataframe()
    
    laser_time = laser_common['Time1']
    laser_data = laser_data['Mean']
    laser_data_norm = laser_data/laser_data.max()
    #offset_time = 870
    offset_time = 35
    laser_time_off = laser_time - offset_time
    
    laserseries = pd.Series(laser_data_norm.values, index = laser_time_off)
    
    return laserseries