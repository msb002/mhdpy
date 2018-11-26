# -*- coding: utf-8 -*-
"""
Various functions for conversions of time objects
"""
import win32com.client  # Python ActiveX Client
LabVIEW = win32com.client.Dispatch("Labview.Application")

repopath = 'C:\\Users\\aspit\\Git\\MHDLab\\'

def gen_filepath(devicename, extension = '.tdms',DAQmx = False, Logfile = False):
    VI = LabVIEW.getvireference(repopath + 'Common Subvis\\GenerateFilePaths.vi')  # Path to LabVIEW VI
    VI._FlagAsMethod("Run")

    VI.setcontrolvalue('Device Name', devicename) 
    VI.setcontrolvalue('Extension (.tdms)', extension)
    VI.setcontrolvalue('DAQmx (F)', DAQmx) 
    VI.setcontrolvalue('Logfile? (F)', Logfile) 
    VI.Run()  # Run the VI
    filepath = VI.getcontrolvalue('Path')  # Get return value
    return filepath  

def get_fileinfo():
    VI = LabVIEW.getvireference(repopath + 'Global Variables.vi')  # Path to LabVIEW VI
    fileinfo = VI.getcontrolvalue('Global File Information')  # Get return value
    return fileinfo  