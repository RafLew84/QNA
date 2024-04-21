# -*- coding: utf-8 -*-
"""
Functions for data proccessing

@author: rlewandkow
"""
from math import sqrt
import numpy as np
from statistics import mean
from PIL import Image

import logging

logger = logging.getLogger(__name__)

def calculate_I_ISET_square(data, ISET):
    return (data - ISET) ** 2

def calculate_l0(data, mapISET = None):
    if not isinstance(data, np.ndarray):
        error_msg = "calculate_l0: Input data must be a numpy array."
        logger.error(error_msg)
        raise ValueError(error_msg)

    if mapISET is not None and not isinstance(mapISET, np.ndarray):
        error_msg = "calculate_l0: mapISET must be a numpy array if provided."
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    l0 = None
    if mapISET is None:
        average = mean(data.flatten())
        if average < 0:
            error_msg = "calculate_l0: Cannot calculate l0 from negative values."
            logger.error(error_msg)
            raise ValueError(error_msg)
        l0 = sqrt(average)
    else:
        length = np.prod(data.shape)
        mapISET_sum = np.sum(mapISET)
        if mapISET_sum < 0:
            error_msg = "calculate_l0: Cannot calculate l0 from negative values."
            logger.error(error_msg)
            raise ValueError(error_msg)
        l0 = np.sqrt(mapISET_sum / length)
    return l0

def create_greyscale_image(points):
    # Create a new grayscale image
    img = Image.new('L', (len(points[0]), len(points)))

    # Normalize the values in data to the range [0, 255]
    max_z = max(map(max, points))
    min_z = min(map(min, points))
    if max_z == min_z:
        max_z += 1
    for i in range(len(points)):
        for j in range(len(points[i])):
            val = int(255 * (points[i][j] - min_z) / (max_z - min_z))
            img.putpixel((j, i), val)
    return img