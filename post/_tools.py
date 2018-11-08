# -*- coding: utf-8 -*-
"""
Low level functions (example: cutting a tdms channel) used by higher-level post processing routines
"""

from __future__ import unicode_literals
import numpy as np
from nptdms import RootObject, ChannelObject
import datetime
import mhdpy.timefuncs as timefuncs
import scipy.stats as stats

#Low level post processing (Functions inside a file)

def _join_tdms(fileinpaths, **kwargs):
    """join two tdms files, not working currently. Just use TDMS combine labview VI"""
    #folder,filename1 = os.path.split(fileinpaths[0])
    #fileoutname = os.path.splitext(filename1)[0] + '_join.tmds'
    # joined = pd.DataFrame()
    # for i in range(len(fileinpaths)):
    #     fileinpath = fileinpaths[i]
    #     tdmsfile = TF(fileinpath)
    #     df = tdmsfile.as_dataframe()
    #     print(df.columns)
    #     if joined.empty:
    #         joined = df
    #     else:
    #         joined = joined.append(df)
    pass


def _cut_channel(channel,time1,time2, timedata = None):
    """
    Cut an individual channel based on input times.
    
    If no time data is passed the channel is assumed to be a waveform and time_track is used to get a numpy array of the times
    """
    waveform = False
    if(timedata == None): #if no timedata is passed, assume channel is a waveform
        timedata = channel.time_track(absolute_time = True)
        waveform = True
    idx1, idx2 =  _get_indextime(timedata, time1,time2)

    if(idx1 == idx2): #times are not within file
        raise ValueError('times not in channel') #.tdms_file.object().properties['name']

    props = channel.properties.copy() #watch out, dicts must be explicity copied to not alter the time track
    # print(type(props))

    if(waveform):
        start= props['wf_start_time']
        offset = datetime.timedelta(milliseconds = props['wf_increment']*1000*idx1)
        props['wf_start_time'] = start + offset


    data = channel.data[idx1:idx2]
    props = {**props, **_calc_stats(data)}

    return ChannelObject(channel.group, channel.channel, data , properties=props)
    
def _cut_datetime_channel(channel,time1,time2):
    """
    cut an array of datetimes. This is a temporary function

    used for powermeter for now, which logs times from labview (Time_LV), which is an array of datetime objects. In the future this, cutting of np64 time arrays, waveforms, and numeric channels should all be combined. 
    """
    timedata = channel.data
    idx1, idx2 =  _get_indextime(timedata, time1,time2)

    if(idx1 == idx2): #times are not within file
        raise ValueError('times not in channel') #.tdms_file.object().properties['name']

    props = channel.properties.copy()
    return ChannelObject(channel.group, channel.channel, timedata[idx1:idx2], properties=props)



def _get_indextime(timedata, time1,time2):
    """Get the nearest indicies of two times in a time array, maintaining time order."""
    if(time2 > time1):
        idx1 = timefuncs.nearest_timeind(timedata,time1)
        idx2 = timefuncs.nearest_timeind(timedata,time2)
    else:
        idx2 = timefuncs.nearest_timeind(timedata,time1)
        idx1 = timefuncs.nearest_timeind(timedata,time2)

    return idx1,idx2    

def _write_dataframe(tdms_writer, dataframe, name):
    """Write a dataframe to a tdms group."""
    root_object = RootObject(properties={ })
    i=0
    for column in dataframe.iteritems():
        column = column[1].as_matrix()
        channel_object = ChannelObject(name, name + "_" + str(i) , column)
        tdms_writer.write_segment([root_object,channel_object])
        i=i+1


def _calc_stats(channel_data):
    statistics = {}
    statistics['stats_mean'] = np.mean(channel_data)
    statistics['stats_median'] = np.median(channel_data)
    statistics['stats_skew'] = stats.skew(channel_data)
    statistics['stats_stddev'] = np.std(channel_data)
    return statistics 