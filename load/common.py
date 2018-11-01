# -*- coding: utf-8 -*-

import os
import nptdms
import re 
import pandas as pd
import numpy as np

def create_tcdict(filepaths, loadfn, prefixes = None ):
    """takes in a list of files and a load function, and creates a dict of a df for each file. If a prefix is passed, that is removed from the filename (typically the instrument name so only the test case is left as the dict key)"""

    dfs = {}

    for filepath in filepaths:
        filename = os.path.split(filepath)[1]
        testcase = os.path.splitext(filename)[0]

        if prefixes != None:
            for prefix in prefixes:
                if prefix in testcase:
                    testcase = _remove_prefix(testcase,prefix)

        
        df =  loadfn(filepath)
        dfs[testcase] =df

    return dfs


def tcdict2mi(tcdict,regexs,drop = True):
    """
    takes in a test case dict and regular expressions to create multi indexed test case df
    
    regex is in form of {'Temperature' : '(\d+)C_', 'Power': '_(\d+)kV', 'Reprate': '_(\d+)Hz' }
    Note: There will be problems if there are duplicates! each file need to have unique testcase including meas number
    need to play wit the order of regex to get the multiindex right
    Todo: with create_tcdict to just create one multiindexed df from start...
    """
    regexs['Measnum'] = '(\d+)$'

    mi_array = []
    tcdict_trim = tcdict.copy()
    for tckey in tcdict:
        i_array = []
        for rekey in regexs:
            regex = regexs[rekey]
            m  = re.search(regex,tckey)
            if (m):
                i_array.append(float(m.groups(1)[0]))
        if(len(i_array) == len(regexs)):
            mi_array.append(i_array)
        else:
            del tcdict_trim[tckey]
                
    mi_array = np.array(mi_array).T.tolist()
    mi = pd.MultiIndex.from_arrays(mi_array , names = regexs.keys())

    df_array = [tcdict_trim[key] for key in tcdict_trim]
    
    # if(drop):
    #     mi = mi.drop_duplicates(keep='last')
    # print(mi)
    df = pd.DataFrame(df_array, index = mi)

    return df

def tdms2df(filepath):
    tdmsfile = nptdms.TdmsFile(filepath)
    df = tdmsfile.as_dataframe()

    #test if a waveform channel
    channel1 = tdmsfile.group_channels(tdmsfile.groups()[0])[0]
    waveform = True
    try:
        channel1.time_track()
    except KeyError:
        waveform = False
    #find the longest waveform
    if waveform:
        longestchannel = None
        length = 0
        for group in tdmsfile.groups():
            for channel in tdmsfile.group_channels(group):
                newlength = len(channel.data)
                if newlength > length:
                    length = newlength
                    longestchannel = channel
        timedata = longestchannel.time_track(absolute_time = True) 
        df = df.set_index(timedata)

    return df


def _remove_prefix(s, prefix):
    return s[len(prefix):] if s.startswith(prefix) else s


def last_measnum(df):
    """Iterates through the multiindex and only uses the last measurement number"""
    trim_index = df.index.droplevel(3).drop_duplicates()

    trim_index
    trim_arr = []
    for testcase in trim_index:
        df_temp = df.loc[testcase]
        df_temp = df_temp.iloc[-1]
        trim_arr.append(df_temp)

    trim_df = pd.DataFrame(trim_arr, index = trim_index)
    
    return trim_df