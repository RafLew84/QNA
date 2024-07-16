# -*- coding: utf-8 -*-
"""
Functions for edge detection

@author
rlewadkow
"""

import os, sys

sys.path.insert(1, "/".join(os.path.realpath(__file__).split("/")[0:-2]))

import cv2
from scipy import ndimage as ndi

import numpy as np

from skimage import feature

from PIL import Image

import logging

from data.processing.file_process import calculate_pixels_from_nm

logger = logging.getLogger(__name__)

def EdgeDetection(img, sigma=1.0):
    """
    Perform edge detection on the input image using Canny edge detector.

    Args:
        img (numpy.ndarray): Input image.
        sigma (float, optional): Standard deviation for Gaussian smoothing. Defaults to 1.0.
    Returns:
        numpy.ndarray: Edge-detected image.
    """
    try:
        edges = feature.canny(
            image=img,
            sigma=np.float64(sigma)
        )
        img = edges.astype('uint8') * 255
        return img
    except Exception as e:
        msg = f"EdgeDetection error: {e}"
        logger.error(msg)
        raise ValueError(msg)