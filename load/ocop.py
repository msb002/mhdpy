import numpy as np
from nptdms import TdmsFile as TF
import pandas as pd
import re

def ocop2df(filepath,):
    file = TF(filepath)

    #find the group name that the normalized data is in
    normdata_groupname = None
    normdata_regex = "(.+_Norm)"
    for group in file.groups():
        m = re.search(normdata_regex,group)
        if m != None:
            normdata_groupname = m.groups()[0]
            break
    
    if(normdata_groupname == None):
        print('could not find Norm group in ' + filepath)
        return pd.DataFrame()
    
    df = file.object(normdata_groupname).as_dataframe()
    df.index = file.object('Global', "Wavelength").data
    indexarr = list(zip(*[file.object('Global', 'MP Pos').data,file.object('Global', 'Time').data]))
    df.columns = pd.MultiIndex.from_tuples(indexarr, names = ['MP','Wavelength'])
    return df

# filepath = "C:\\Labview Test Data\\2018-11-20\\UnspecifiedProj\\Run3\\Log_NIRQuest512_0_Case5_seed_0.tdms"
# # df = ocop2df(filepath)
# file = TF(filepath)