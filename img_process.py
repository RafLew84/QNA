# -*- coding: utf-8 -*-
"""
Functions for image proccessing

@author
"""

import cv2
from scipy import ndimage as ndi

import numpy as np

from skimage import feature

import logging

logger = logging.getLogger(__name__)

def NlMeansDenois(img, h=3, searchWinwowSize=21, templateWindowSize=7):
    """
    Apply Non-Local Means Denoising to the input image.

    Args:
        img (numpy.ndarray): Input image.
        h (float, optional): Parameter regulating filter strength. Higher h value removes noise better, but removes details of image also. Defaults to 3.
        searchWinwowSize (int, optional): Size in pixels of the window to be used for searching matches. Larger value implies that farther pixels will influence each other. Defaults to 21.
        templateWindowSize (int, optional): Size in pixels of the window to be used for gathering pixel values. Defaults to 7.

    Returns:
        numpy.ndarray: Denoised image.
    """
    try:
        denoised_image = cv2.fastNlMeansDenoising(
            img, None,
            h=h,
            searchWindowSize=searchWinwowSize,
            templateWindowSize=templateWindowSize
        )
        return denoised_image
    except Exception as e:
        msg = f"NlMeansDenois error: {e}"
        logger.error(msg)
        raise ValueError(msg)

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

def EdgeDetection(img, sigma=1.0, low_threshold=None, high_threshold=None):
    """
    Perform edge detection on the input image using Canny edge detector.

    Args:
        img (numpy.ndarray): Input image.
        sigma (float, optional): Standard deviation for Gaussian smoothing. Defaults to 1.0.
        low_threshold (float, optional): Lower bound for hysteresis thresholding. If None, low_threshold is set to 0.1 * np.max(image_grad). Defaults to None.
        high_threshold (float, optional): Upper bound for hysteresis thresholding. If None, high_threshold is set to 0.2 * np.max(image_grad). Defaults to None.

    Returns:
        numpy.ndarray: Edge-detected image.
    """
    try:
        edges = feature.canny(
            image=img,
            sigma=np.float64(sigma),
            low_threshold=low_threshold,
            high_threshold=high_threshold
        )
        img = edges.astype('uint8') * 255
        return img
    except Exception as e:
        msg = f"EdgeDetection error: {e}"
        logger.error(msg)
        raise ValueError(msg)

def ContourFinder(img):
    """
    Find contours in the input image.

    Args:
        img (numpy.ndarray): Input image.

    Returns:
        list: List of contours.
    """
    try:
        contours, _ = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        return contours
    except Exception as e:
        msg = f"ContourFinder error: {e}"
        logger.error(msg)
        raise ValueError(msg)