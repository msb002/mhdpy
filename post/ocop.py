from __future__ import unicode_literals
from ._tools import _cut_channel, _cut_datetime_channel, _get_indextime
from nptdms import TdmsFile as TF
from nptdms import TdmsWriter, RootObject, ChannelObject
import os
from numpy import datetime64 as dt64

def multiplex_spectra(fileinpaths, mpchannel, **kwargs):
    """
    Seperates the spectra into 'on' and  'off' channels, on being where the multiplexer is reading that spectrometer.
    
    If the MP channel is not the spectrometer's channel, it will not use that data
    
    """

def cut_log_spectra(fileinpaths, times, fileoutpaths_list, **kwargs):
    for i, fileinpath in enumerate(fileinpaths):
        fileoutpaths = fileoutpaths_list[i]
        tdmsfile = TF(fileinpath)
        for j, t in enumerate(times):
            fileoutpath = fileoutpaths[j]
            
            direc = os.path.split(fileoutpath)[0]
            if not os.path.exists(direc):
                os.makedirs(direc)
            
            root_object = RootObject(properties = {})
            
            try:
                with TdmsWriter(fileoutpath, mode='w') as tdms_writer:
                    timedata = [dt64(y) for y in tdmsfile.channel_data('Global','Time')]
                    idx1, idx2 = _get_indextime(timedata, t[0], t[1])
                    if idx1==idx2:
                        pass
                    else:
                        for group in tdmsfile.groups()[1:2]:
                            for channel in tdmsfile.group_channels(group)[idx1:idx2]:
                                tdms_writer.write_segment([root_object, channel])
                        for channel in tdmsfile.group_channels('Global'):
                            if channel.channel == 'Wavelength':
                                channel_object = channel
                            else:
                                channel_object = ChannelObject( channel.group, channel.channel, channel.data[idx1:idx2])
                            tdms_writer.write_segment([
                                root_object,
                                channel_object
                            ])
            except ValueError as error:
                print(error)
                print('removing the file at: \n', fileoutpath)
                os.remove(fileoutpath)
        
