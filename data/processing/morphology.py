# -*- coding: utf-8 -*-
"""
Morphology functions for binary images

@author
"""

import os, sys
import numpy as np

sys.path.insert(1, "/".join(os.path.realpath(__file__).split("/")[0:-2]))

import cv2
from scipy import ndimage
from skimage.morphology import reconstruction
from skimage import img_as_float
from skimage.morphology import (disk, binary_erosion, binary_closing, binary_dilation, binary_opening,
                                square, diamond, star, remove_small_holes, remove_small_objects)

def BinaryErosion(img, footprint_type, footprint_size):
    footprint = binary_selem(footprint_type, footprint_size)
    eroded_image = binary_erosion(img, footprint=footprint)

    return eroded_image

def BinaryDilation(img, footprint_type, footprint_size):
    footprint = binary_selem(footprint_type, footprint_size)
    dilated_image = binary_dilation(img, footprint=footprint)

    return dilated_image

def BinaryOpening(img, footprint_type, footprint_size):
    footprint = binary_selem(footprint_type, footprint_size)
    opened_image = binary_opening(img, footprint=footprint)

    return opened_image

def BinaryClosing(img, footprint_type, footprint_size):
    footprint = binary_selem(footprint_type, footprint_size)
    closed_image = binary_closing(img, footprint=footprint)

    return closed_image

def RemoveSmallHoles(img, area_threshold,connectivity):
    result_image = remove_small_holes(img, area_threshold, connectivity)
    return result_image

def RemoveSmallObjects(img, min_size,connectivity):
    result_image = remove_small_objects(img, min_size, connectivity)
    return result_image


def binary_selem(selem_type, selem_size):
    selem = None
    if selem_type == "disk":
        selem = disk(selem_size)
    elif selem_type == "square":
        selem = square(selem_size)
    elif selem_type == "diamond":
        selem = diamond(selem_size)
    elif selem_type == "star":
        selem = star(selem_size)
    
    return selem