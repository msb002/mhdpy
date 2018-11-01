# -*- coding: utf-8 -*-
"""
Functions for use in Data Analysis
"""
import numpy as np


def find_nearest(a, a0):
    "Element in nd array `a` closest to the scalar value `a0`"
    idx = np.abs(a - a0).argmin()
    return idx


