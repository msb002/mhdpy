# -*- coding: utf-8 -*-
"""
Post Processing routines to parse lightfield spe files
"""
from ._tools import _write_dataframe

from nptdms import TdmsWriter, RootObject, GroupObject, ChannelObject
import spe_loader as sl
import pandas as pd
import os
import datetime
import numpy as np
from dateutil import parser

### High level post processing (processes multiple types of files in a predefined way)
def parse_lasertiming(fileinpaths, **kwargs):
    """Takes in a series of SPE sequential images and outputs a tdms file of the maximum of each image."""
    intensities, timestamps, gatedelays = _lasertiming(fileinpaths)
    folder = os.path.split(fileinpaths[0])[0]
    fileoutpath = os.path.join(folder, 'PIMax_Timing_Parsed.tdms')

    

    with TdmsWriter(fileoutpath, mode = 'w') as tdms_writer:
        root_object = RootObject(properties={ })
        channel_object = ChannelObject('Gate Delays', 'Gate Delays' , gatedelays)
        tdms_writer.write_segment([root_object,channel_object])
        _write_dataframe(tdms_writer, intensities, "MaxIntensities")
        _write_dataframe(tdms_writer, timestamps, "Timestamps")

def SPEtoTDMS_seq(spefilepath,meastype):
    """convert a sequential SPE file (image or spectral) into a Tdms file. """
    if isinstance(spefilepath,bytes): #The labview addin passes a bytes instead of string. 
        spefilepath = spefilepath.decode("utf-8")
    
    folder = os.path.splitext(os.path.dirname(spefilepath))[0]
    base = os.path.splitext(os.path.basename(spefilepath))[0]
    tdmsfilepath = os.path.join(folder,base + ".tdms")

    spe_file = sl.load_from_files([spefilepath])

    frames  = spe_file.data   
    gatedelays = _get_gatedelays(spe_file)
    
    root_object = RootObject(properties={})    
    common_group_object = GroupObject("Common", properties={})
    
    with TdmsWriter(tdmsfilepath) as tdms_writer:   
        channel_object = ChannelObject("Common", "Gate Delays" ,gatedelays, properties={})
        tdms_writer.write_segment([root_object,common_group_object,channel_object])
    
    if(meastype == 0): 
        wavelength = spe_file.wavelength
        with TdmsWriter(tdmsfilepath, mode = 'a') as tdms_writer: 
            channel_object = ChannelObject("Common", "Wavelength" ,wavelength, properties={})
            tdms_writer.write_segment([root_object,common_group_object,channel_object])   
        write_spectra(tdmsfilepath, root_object, frames,wavelength )
    if(meastype == 1):
        write_image(tdmsfilepath, root_object, frames )

def write_image(tdmsfilepath, root_object, frames ):
    """writes a series of images to a tdms file. """
    framenum = 0
    
    with TdmsWriter(tdmsfilepath, mode = 'a') as tdms_writer:
        for frame in frames:
            rawdata_group_object = GroupObject("Frame" + str(framenum), properties={}) 
            linenum = 0
            for line in frame[0]:
                channel_object = ChannelObject("Frame" + str(framenum), "line" + str(linenum) , line, properties={})
                tdms_writer.write_segment([root_object,rawdata_group_object,channel_object])
                linenum = linenum +1
            framenum = framenum +1   
            
def write_spectra(tdmsfilepath, root_object, frames, wavelength ):
    """writes a series of spectra to a tmds file. """
    framenum = 0
    
    rawdata_group_object = GroupObject("Raw Data", properties={})
    
    with TdmsWriter(tdmsfilepath, mode = 'a') as tdms_writer:   
        for frame in frames:
            channel_object = ChannelObject("Raw Data", "Frame" + str(framenum), frame[0][0], properties={})
            tdms_writer.write_segment([root_object,rawdata_group_object,channel_object])
            framenum = framenum +1

def _lasertiming(filepaths):
    """generates a dataframe of intensities and timestamps from a list of spe filepaths"""
    #folderpath = os.path.split(filepaths[0])
    #filenames = [f for f in os.listdir(folderpath) if os.path.isfile(os.path.join(folderpath,f))]
    #filenames = [os.path.split(filepath) for filepath in filepaths if os.path.splitext(filepaths)[1] == '.spe']

    spe_files = sl.load_from_files(filepaths)
    if type(spe_files) != type(list()):
        spe_files = [spe_files]
    gatedelays = _get_gatedelays(spe_files[0])
    intensities = pd.DataFrame(index = gatedelays, columns = range(len(filepaths)))
    timestamps = pd.DataFrame(index = gatedelays, columns = range(len(filepaths)))
    i=0    
    for spe_file in spe_files:
        frames  = spe_file.data
        intensity = list(map(lambda x: x[0].max(), frames))       
        try:
            timestamps.iloc[:,i] = pd.Series(_get_starttimes(spe_file), index = timestamps.index)
            intensities.iloc[:,i] = pd.Series(intensity, index = intensities.index)
            i=i+1
        except ValueError: #comes up if there is an incomplete file. 
            print('A SPE file did not have correct number of data points. Note that first file must have correct number of data points')
    intensities = intensities.truncate(after = i, axis = 'columns')
    timestamps = timestamps.truncate(after = i, axis = 'columns')
    return intensities, timestamps, gatedelays


def _get_gatedelays(spe_file):
    """pull a gate delay array from a sequential SPE file. """
    num_frames = spe_file.nframes
    
    Gatinginfo = spe_file.footer.SpeFormat.DataHistories.DataHistory.Origin.Experiment.Devices.Cameras.Camera.Gating.Sequential
    
    start_gatedelay = int(Gatinginfo.StartingGate.Pulse['delay'])
    end_gatedelay = int(Gatinginfo.EndingGate.Pulse['delay'])
    
    gatedelays = np.linspace(start_gatedelay, end_gatedelay, num_frames)

    return gatedelays

def _get_starttimes(spe_file):
    """pulls an array of exposure start times from an spe file"""
    abstimestr = spe_file.footer.SpeFormat.MetaFormat.MetaBlock.TimeStamp[0]['absoluteTime']
    abstime = parser.parse(abstimestr)
    timestamp_idx = spe_file.metanames.index('ExposureStarted')
    starttimestamps = np.array(list(map( lambda x: x[timestamp_idx], spe_file.metadata)))
    res = int(spe_file.footer.SpeFormat.MetaFormat.MetaBlock.TimeStamp[0]['resolution'])
    starttimestamps = starttimestamps/res
    starttimedeltas = list(map(lambda x:datetime.timedelta(seconds = x),starttimestamps))
    starttimes = [abstime + starttime for starttime in starttimedeltas] 
    starttimes = [time.timestamp() for time in starttimes]
    return starttimes

