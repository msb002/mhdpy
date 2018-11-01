# -*- coding: utf-8 -*-
"""
Various functions for conversions of time objects
"""

from __future__ import unicode_literals
import numpy as np
import time

import datetime
import pytz
import tzlocal


#time conversion.
def np64_to_utc(np64_dt):
    """converts a np64 datetime into a datetime datetime with utc timezone, converting through a timestamp first."""
    return datetime.datetime.utcfromtimestamp(np64_to_unix(np64_dt)).replace(tzinfo=pytz.utc)

def np64_to_unix(timestamp):
    """converts a np64 datetiem to a unix timestamp"""
    return (timestamp - np.datetime64('1970-01-01T00:00:00Z')) / np.timedelta64(1, 's')

def datetime_to_unix(timestamp):
    """converts a datetime datetime into a unix timestamp"""
    return (timestamp - datetime.datetime(1970,1,1,tzinfo = pytz.utc)).total_seconds()

def labview_to_unix(timestamps):
    """converts a labview timestamp into a unix timestamp"""
    return list(map(lambda x: x -2082844800 ,timestamps))

def nearest_timeind(timearray, pivot, dtype = 'datetime'):
    """
    Returns the nearest index in a time array corresponding to the pivot time.
    
    The method varies depending on the datatype. datetime.datetime objects require lambda functions to convert an array to timestamps. numpy datetimes can just undergo simple element by element subtraction, which is much quicker. 
    """
    if(dtype == 'datetime'):
        seconds = np.array(list(map(lambda x: abs(x - pivot).total_seconds(),timearray))) 
    else:
        seconds = abs(timearray - pivot)
    return seconds.argmin()