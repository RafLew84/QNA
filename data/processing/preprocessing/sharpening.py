# -*- coding: utf-8 -*-
"""
Smoothing functions

@author
"""

import os, sys

sys.path.insert(1, "/".join(os.path.realpath(__file__).split("/")[0:-2]))

import cv2
from skimage.filters import unsharp_mask


import logging

logger = logging.getLogger(__name__)

def GaussianSharpening(img, radius=1.0, amount=1.0):

    # Apply unsharp masking
    sharpened_image = unsharp_mask(img, radius=radius, amount=amount)

    return sharpened_image