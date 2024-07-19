# -*- coding: utf-8 -*-
"""
Morphology functions

@author
"""

import os, sys

sys.path.insert(1, "/".join(os.path.realpath(__file__).split("/")[0:-2]))

import numpy as np
from skimage import exposure

def GammaAdjustment(img, gamma):
    exposed_image = exposure.adjust_gamma(img, gamma)
    return exposed_image

def ContrastStretching(img, min, max):
    p_min, p_max = np.percentile(img, (min, max))
    exposed_image = exposure.rescale_intensity(img, in_range=(p_min, p_max))
    return exposed_image