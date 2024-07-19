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

from data.processing.preprocessing.morphology import (
    Erosion,
    BinaryGreyscaleErosion,
    GaussianGreyscaleErosion,
    BinaryGreyscaleDilation,
    GaussianGreyscaleDilation,
    BinaryGreyscaleOpening,
    GaussianGreyscaleOpening,
    BinaryGreyscaleClosing,
    GaussianGreyscaleClosing
)

from data.processing.preprocessing.intensity import (
    GammaAdjustment
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

def perform_erosion(params, img):
    """
    Apply a Erosion to an image.

    Args:
        params (dict): Parameters for the Erosion.
        img (PIL.Image.Image): The input image.

    Returns:
        tuple: Process name and the resulting image.
    """
    process_name = "Erosion"
    result_image = Erosion(
            img=np.array(img),
            kernel_type=params['kernel_type'],
            kernel_size=params['kernel_size'],
            iterations=params['iterations']
        )
    
    return process_name,result_image

def perform_binary_greyscale_erosion(params, img):
    process_name = "Binary Greyscale Erosion"
    result_image = BinaryGreyscaleErosion(
        img=np.array(img),
        kernel_type=params['kernel_type'],
        kernel_size=params['kernel_size']
    )

    return process_name, result_image

def perform_gaussian_greyscale_erosion(params, img):
    process_name = "Gaussian Greyscale Erosion"
    result_image = GaussianGreyscaleErosion(
        img=np.array(img),
        mask_size=params['mask_size'],
        sigma=params['sigma']
    )

    return process_name, result_image

def perform_binary_greyscale_dilation(params, img):
    process_name = "Binary Greyscale Dilation"
    result_image = BinaryGreyscaleDilation(
        img=np.array(img),
        kernel_type=params['kernel_type'],
        kernel_size=params['kernel_size']
    )

    return process_name, result_image

def perform_gaussian_greyscale_dilation(params, img):
    process_name = "Gaussian Greyscale Dilation"
    result_image = GaussianGreyscaleDilation(
        img=np.array(img),
        mask_size=params['mask_size'],
        sigma=params['sigma']
    )

    return process_name, result_image

def perform_binary_greyscale_opening(params, img):
    process_name = "Binary Greyscale Opening"
    result_image = BinaryGreyscaleOpening(
        img=np.array(img),
        kernel_type=params['kernel_type'],
        kernel_size=params['kernel_size']
    )

    return process_name, result_image

def perform_gaussian_greyscale_opening(params, img):
    process_name = "Gaussian Greyscale Opening"
    result_image = GaussianGreyscaleOpening(
        img=np.array(img),
        mask_size=params['mask_size'],
        sigma=params['sigma']
    )

    return process_name, result_image

def perform_binary_greyscale_closing(params, img):
    process_name = "Binary Greyscale Closing"
    result_image = BinaryGreyscaleClosing(
        img=np.array(img),
        kernel_type=params['kernel_type'],
        kernel_size=params['kernel_size']
    )

    return process_name, result_image

def perform_gaussian_greyscale_closing(params, img):
    process_name = "Gaussian Greyscale Closing"
    result_image = GaussianGreyscaleClosing(
        img=np.array(img),
        mask_size=params['mask_size'],
        sigma=params['sigma']
    )

    return process_name, result_image

def perform_gamma_adjustment(params, img):
    process_name = "Gamma Adjustment"
    result_image = GammaAdjustment(
        img=np.array(img),
        gamma=params['gamma']
    )

    return process_name, result_image