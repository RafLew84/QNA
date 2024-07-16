# -*- coding: utf-8 -*-
"""
Functions for preprocessing

@author
rlewandkow
"""

import os, sys

sys.path.insert(1, "/".join(os.path.realpath(__file__).split("/")[0:-2]))

import cv2
import numpy as np
from PIL import Image, ImageTk

from data.processing.preprocessing.smoothing import (
    GaussianBlur,
    GaussianFilter
)

from data.processing.preprocessing.noise_reduction import (
    NlMeansDenois
)

def perform_gaussian_blur(params, img):
    """
    Apply Gaussian blur to an image.

    Args:
        params (dict): Parameters for Gaussian blur, should include 'sigmaX' and 'sigmaY'.
        img (PIL.Image.Image): The input image.

    Returns:
        tuple: Process name and the resulting image.
    """
    process_name = "GaussianBlur"
    result_image = GaussianBlur(
            img=np.array(img), 
            sigmaX=params['sigmaX'],
            sigmaY=params['sigmaY']
            )
    
    return process_name, result_image

def perform_non_local_denoising(params, img):
    """
    Apply Non-local Means denoising to an image.

    Args:
        params (dict): Parameters for Non-local Means denoising, should include 'h', 'searchWindowSize', and 'templateWindowSize'.
        img (PIL.Image.Image): The input image.

    Returns:
        tuple: Process name and the resulting image.
    """
    process_name = "Non-local Mean Denoising"
    result_image = NlMeansDenois(
            img=np.array(img),
            h=params['h'],
            searchWinwowSize=params['searchWindowSize'],
            templateWindowSize=params['templateWindowSize']
            )
    return process_name, result_image

def perform_gaussian_filter(params, img):
    """
    Apply a Gaussian filter to an image.

    Args:
        params (dict): Parameters for the Gaussian filter, should include 'sigma'.
        img (PIL.Image.Image): The input image.

    Returns:
        tuple: Process name and the resulting image.
    """
    process_name = "GaussianFilter"
    result_image = GaussianFilter(
            img=np.array(img),
            sigma=params['sigma']
        )
    
    return process_name,result_image