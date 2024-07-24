# -*- coding: utf-8 -*-
"""
Functions for image proccessing

@author
rlewadkow
"""

import os, sys

sys.path.insert(1, "/".join(os.path.realpath(__file__).split("/")[0:-2]))

from skimage.filters import threshold_otsu

def OtsuThreshold(img):
    thresh = threshold_otsu(img)
    binary_global = img > thresh

    return binary_global