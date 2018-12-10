# -*- coding: utf-8 -*-
"""
Various functions for conversions of time objects
"""
import datetime
import win32com.client  # Python ActiveX Client
import os

<<<<<<< Updated upstream
repopath = 'C:\\Users\\aspitarl\\Git\\MHDLab\\'
=======
repopath = os.path.split(os.path.dirname(os.path.abspath(__file__)))[0]
>>>>>>> Stashed changes

def gen_filepath(LabVIEW, devicename, extension = '.tdms',DAQmx = False, Logfile = False):
    vipath = os.path.join(repopath,'Common Subvis\\GenerateFilePaths.vi')
    print(vipath)
    VI = LabVIEW.getvireference(vipath)  # Path to LabVIEW VI
    VI._FlagAsMethod("Run")

    VI.setcontrolvalue('Device Name', devicename) 
    VI.setcontrolvalue('Extension (.tdms)', extension)
    VI.setcontrolvalue('DAQmx (F)', DAQmx) 
    VI.setcontrolvalue('Logfile? (F)', Logfile) 
    VI.Run()  # Run the VI
    filepath = VI.getcontrolvalue('Path')  # Get return value
    return filepath  

def get_fileinfo(LabVIEW):
    VI = LabVIEW.getvireference(repopath + 'Global Variables.vi')  # Path to LabVIEW VI
    fileinfo = VI.getcontrolvalue('Global File Information')  # Get return value
    return fileinfo  

def get_rawdatafolder(LabVIEW):
    VI = LabVIEW.getvireference(repopath + 'Global Variables.vi')  # Path to LabVIEW VI
    datafolder = VI.getcontrolvalue('Data folder')  # Get return value
    datestring = datetime.date.today().strftime("%Y-%m-%d")
    datafolder = os.path.join(datafolder,datestring)
    return datafolder


LabVIEW = win32com.client.Dispatch("Labview.Application")
# print(get_rawdatafolder(LabVIEW))
