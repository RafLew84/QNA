# -*- coding: utf-8 -*-
"""
Functions for data proccessing

@author: rlewandkow
"""
from math import sqrt
import numpy as np

def calculate_I_ISET_square(data, ISET):
    return (data - ISET) ** 2

def calculate_l0(data, mapISET):
    length = np.prod(data.shape)
    print(length)
    l0 = sqrt(sum(mapISET) / length)
    return l0