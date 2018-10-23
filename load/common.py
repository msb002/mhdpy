# -*- coding: utf-8 -*-

import os
import nptdms
import re 
import pandas as pd


def create_tcdict(filepaths, loadfn, prefix = None ):
    """takes in a list of files and a load function, and creates a dict of a df for each file. If a prefix is passed, that is removed from the filename (typically the instrument name so only the test case is left as the dict key)"""

    dfs = {}

    for filepath in filepaths:
        filename = os.path.split(filepath)[1]
        testcase = os.path.splitext(filename)[0]

        if prefix != None:
            testcase = _remove_prefix(testcase,prefix)

        df =  loadfn(filepath)
        dfs[testcase] =df
    
    return dfs


def tcdict2mi(tcdict,regexs):
    """
    takes in a test case dict and regular expressions to create multi indexed test case df
    
    regex is in form of {'Temperature' : '^(.+?)C_', 'Reprate': '_(.+?)Hz'}
    needs to be combined with create_tcdict to just create one multiindexed df from start...
    """
    mi_array = []
    for rekey in regexs:
        regex = regexs[rekey]
        i_array = []
        for tckey in tcdict:
            m  = re.search(regex,tckey)
            if (m):
                i_array.append(float(m.groups(1)[0]))
                #print(m.groups(1)[0])
        mi_array.append(i_array)
    mi = pd.MultiIndex.from_arrays(mi_array , names = regexs.keys())
    
    df_array = [tcdict[key] for key in tcdict]
    
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