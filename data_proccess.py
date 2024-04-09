# -*- coding: utf-8 -*-
"""
Functions for data proccessing

@author: rlewandkow
"""
from math import sqrt
import numpy as np
from statistics import mean

def calculate_I_ISET_square(data, ISET):
    return (data - ISET) ** 2

def calculate_l0(data, mapISET = None):
    l0 = None
    if mapISET is None:
        average = mean(data.flatten())
        l0 = sqrt(average)
    else:
        length = np.prod(data.shape)
        l0 = sqrt(sum(mapISET) / length)
    return l0