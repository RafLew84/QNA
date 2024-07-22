# -*- coding: utf-8 -*-
"""
Smoothing functions

@author
"""

import os, sys

sys.path.insert(1, "/".join(os.path.realpath(__file__).split("/")[0:-2]))

import cv2
from scipy import ndimage as ndi
from scipy.ndimage import median_filter
from skimage import img_as_float
import numpy as np

import logging

logger = logging.getLogger(__name__)

def GaussianBlur(img, sigmaX=5, sigmaY=5, borderType=0):
    """
    Apply Gaussian blur to the input image.

    Args:
        img (numpy.ndarray): Input image.
        sigmaX (float, optional): Standard deviation in X direction. Defaults to 5.
        sigmaY (float, optional): Standard deviation in Y direction. Defaults to 5.
        borderType (int, optional): Border mode. Defaults to 0.

    Returns:
        numpy.ndarray: Blurred image.
    """
    try:
        if sigmaX <= 0 or sigmaX % 2 == 0:
            raise ValueError("sigmaX must be a positive odd number")
        if sigmaY <= 0 or sigmaY % 2 == 0:
            raise ValueError("sigmaY must be a positive odd number")
        blurred_image = cv2.GaussianBlur(
            img,
            (sigmaX, sigmaY),
            borderType
        )
        return blurred_image
    except Exception as e:
        msg = f"GaussianBlur error: {e}"
        logger.error(msg)
        raise ValueError(msg)
    
def GaussianFilter(img, sigma=4):
    """
    Apply Gaussian filter to the input image.

    Args:
        img (numpy.ndarray): Input image.
        sigma (float, optional): Standard deviation for Gaussian kernel. Defaults to 4.

    Returns:
        numpy.ndarray: Filtered image.
    """
    try:
        gaussian_image = ndi.gaussian_filter(
            input=img,
            sigma=sigma
        )
        return gaussian_image
    except Exception as e:
        msg = f"GaussianFilter error: {e}"
        logger.error(msg)
        raise ValueError(msg)
    

def LocalMedianFilter(image, size=5):
    image = img_as_float(image)
    """Apply median filter to smooth the background."""
    smoothed_image = median_filter(image, size=size)

    leveled_image_normalized = cv2.normalize(smoothed_image, None, 0, 255, cv2.NORM_MINMAX)
    leveled_image_normalized = leveled_image_normalized.astype(np.uint8)

    return leveled_image_normalized
