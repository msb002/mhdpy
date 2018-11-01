import numpy as np
from nptdms import TdmsFile as TF
import pandas as pd

def ocop2df(filepath,):
    file = TF(filepath)
    df = file.object(file.groups()[2]).as_dataframe()
    df.index = file.object('Global', "Wavelength").data
    indexarr = list(zip(*[file.object('Global', 'MP Pos').data,file.object('Global', 'Time').data]))
    df.columns = pd.MultiIndex.from_tuples(indexarr, names = ['MP','Wavelength'])
    return df