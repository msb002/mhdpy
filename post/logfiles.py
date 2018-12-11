# -*- coding: utf-8 -*-
"""
Post Processing routines that parse log files.
"""

from __future__ import unicode_literals
from ._tools import _cut_channel, _cut_datetime_channel, _get_indextime
from nptdms import TdmsFile as TF
from nptdms import TdmsWriter, RootObject
import nptdms
import os
import mhdpy.timefuncs as timefuncs
import numpy as np
import tzlocal
import pytz
import pandas as pd
import re



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

            timegroupwritten = False

            try:
                with TdmsWriter(fileoutpath,mode='w') as tdms_writer:
                    for group in tdmsfile.groups():
                        if 'TimeChannelName' in kwargs:
                            if 'TimeGroupName' in kwargs:
                                timegroup = kwargs['TimeGroupName']
                            else:
                                timegroup = group
                                timegroupwritten = False
                            timechannel = tdmsfile.object(timegroup,kwargs['TimeChannelName'])
                            timedata = timechannel.data    
                            timedata = np.array(list(map(lambda x: np.datetime64(x),timedata)))   
                            timedata = timedata.astype('M8[us]')

                            if timegroupwritten == False:
                                timechannel_cut = _cut_datetime_channel(timechannel,time1,time2)
                                tdms_writer.write_segment([root_object,timechannel_cut])
                                timegroupwritten = True

                            waveform = False
                        else:
                            waveform = True

                        for channel in tdmsfile.group_channels(group):
                            # if type(channel.data_type.size) == type(None): break #skips over non numeric channels
                            if channel.data_type == nptdms.types.DoubleFloat:
                                if waveform:
                                    timedata = channel.time_track(absolute_time = True)
                                idx1, idx2 =  _get_indextime(timedata, time1,time2)
                                channel_object = _cut_channel(channel,idx1,idx2,waveform)
                                tdms_writer.write_segment([root_object,channel_object])
            except ValueError as error:
                print(error)
                print('removing the file at: \n', fileoutpath)
                os.remove(fileoutpath)

def cut_powermeter(fileinpaths, times, fileoutpaths_list, **kwargs):
    kwargs = {**kwargs, 'TimeChannelName' : "Time_LV"}
    cut_log_file(fileinpaths, times, fileoutpaths_list, **kwargs)

def cut_alicat(fileinpaths, times, fileoutpaths_list, **kwargs):
    kwargs = {**kwargs, 'TimeChannelName' : "Time"}
    cut_log_file(fileinpaths, times, fileoutpaths_list, **kwargs)

def cut_motor(fileinpaths, times, fileoutpaths_list, **kwargs):
    kwargs = {**kwargs, 'TimeChannelName' : "Time"}
    cut_log_file(fileinpaths, times, fileoutpaths_list, **kwargs)


def _df_to_csvs(df, times, fileoutpaths):
    """
    Cuts up a dataframe with a date time index and saves to a csv

    df index should be pandas datetime in UTC
    """
    
    for j in range(len(times)):
        time1 = times[j][0]
        time2 = times[j][1]

        fileoutpath = fileoutpaths[j]
        fileoutpath = fileoutpath.replace(".tdms", ".csv")   
        direc = os.path.split(fileoutpath)[0]
        if not os.path.exists(direc):
            os.makedirs(direc)

        df_cut = df[time1:time2]
        df_cut.to_csv(fileoutpath)       

def cut_jp(fileinpaths, times, fileoutpaths_list, **kwargs):
    """
    cuts jp csv.
    
    This function just get the data into a format to be used by _df_to_csvs
    """
    localtz = tzlocal.get_localzone()
    for i, fileinpath in enumerate(fileinpaths):
        fileoutpaths = fileoutpaths_list[i]
        df = pd.read_csv(fileinpath, index_col = 0)
  
        timeindex = pd.to_datetime(df.index, format = '%m-%d-%Y_%H:%M:%S')
        timeindex = timeindex.tz_localize(localtz)
        timeindex = timeindex.tz_convert(None)

        df = df.set_index(timeindex)

        _df_to_csvs(df,times,fileoutpaths)


def cut_hene(fileinpaths, times, fileoutpaths_list, **kwargs):
    """
    cuts up text file generated from starlab. 
    
    This function just get the data into a format to be used by _df_to_csvs
    """
    localtz = tzlocal.get_localzone()
    for i, fileinpath in enumerate(fileinpaths):
        fileoutpaths = fileoutpaths_list[i]

        with open(fileinpath) as fp:
            lines = fp.readlines()
        timeinfo = lines[34]
        regex = ";First Pulse Arrived : (.+) at (.+)\n"
        m = re.search(regex,timeinfo)
        timestr = m.groups()[0] + " " + m.groups()[1]
        dt_0= pd.to_datetime(timestr, dayfirst = True)
        # dt_0 = dt_0 + pd.Timedelta('1 hour')

        df = pd.read_csv(fileinpath, skiprows = 35, delimiter = '\t')

        dts = df[df.columns[0]]
        timedeltas = [pd.Timedelta(dt, unit = 's') for dt in dts]
        timelist = [dt_0 + timedelta for timedelta in timedeltas]
        timeindex = pd.to_datetime(timelist)
        timeindex = timeindex.tz_localize(localtz)
        timeindex = timeindex.tz_convert(None)

        df = df.set_index(timeindex)

        _df_to_csvs(df,times,fileoutpaths)