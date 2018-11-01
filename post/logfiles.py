# -*- coding: utf-8 -*-
"""
Post Processing routines that parse log files.
"""

from __future__ import unicode_literals
from ._tools import _cut_channel, _cut_datetime_channel
from nptdms import TdmsFile as TF
from nptdms import TdmsWriter, RootObject
import os
import mhdpy.timefuncs as timefuncs
import numpy as np


# Mid level post processing (processes a specific type of file)
def cut_log_file(fileinpaths, times, fileoutpaths_list, **kwargs):
    """
    Cuts up a log file based on the supplied times.
    
    This function assumes that the channels are waveforms.
    """

    for i, fileinpath in enumerate(fileinpaths):

        fileoutpaths = fileoutpaths_list[i]
        tdmsfile = TF(fileinpath)
        for j in range(len(times)):
            time1 = times[j][0]
            time2 = times[j][1]

            fileoutpath = fileoutpaths[j]
            
            direc = os.path.split(fileoutpath)[0]
            if not os.path.exists(direc):
                os.makedirs(direc)

            root_object = RootObject(properties={ #TODO root properties
            })

            try:
                with TdmsWriter(fileoutpath,mode='w') as tdms_writer:
                    for group in tdmsfile.groups():
                        for channel in tdmsfile.group_channels(group):
                            channel_object = _cut_channel(channel,time1,time2, timedata = None)
                            tdms_writer.write_segment([
                                root_object,
                                channel_object])
            except ValueError as error:
                print(error)
                print('removing the file at: \n', fileoutpath)
                os.remove(fileoutpath)

def cut_powermeter(fileinpaths, times, fileoutpaths_list, **kwargs):
    """Cut up a power meter tdms file based on input times."""
    for i in range(len(fileinpaths)):
        fileinpath = fileinpaths[i]
        fileoutpaths = fileoutpaths_list[i]
        tdmsfile = TF(fileinpath)
        for j in range(len(times)):
            time1 = times[j][0]
            time2 = times[j][1]
            fileoutpath = fileoutpaths[j]

            direc = os.path.split(fileoutpath)[0]
            if not os.path.exists(direc):
                os.makedirs(direc)

            root_object = RootObject(properties={ #TODO root properties
            })
            try:
                with TdmsWriter(fileoutpath,mode='w') as tdms_writer:
                    for group in tdmsfile.groups():
                        timedata = tdmsfile.channel_data(group,'Time_LV')                     
                        for channel in tdmsfile.group_channels(group):
                            if type(channel.data_type.size) == type(None): break #skips over non numeric channels
                            channel_object = _cut_channel(channel,time1,time2, timedata = timedata)
                            tdms_writer.write_segment([root_object,channel_object])
                        timechannel = tdmsfile.object(group,'Time_LV')
                        timechannel_cut = _cut_datetime_channel(timechannel,time1,time2)
                        tdms_writer.write_segment([root_object,timechannel_cut])
            except ValueError as error:
                print(error)
                print('removing the file at: \n', fileoutpath)
                os.remove(fileoutpath)



