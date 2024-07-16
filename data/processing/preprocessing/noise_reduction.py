# -*- coding: utf-8 -*-
"""
Functions for Noise reduction proccessing

@author
rlewadkow
"""

import os, sys

sys.path.insert(1, "/".join(os.path.realpath(__file__).split("/")[0:-2]))

import cv2

import logging

from data.processing.file_process import calculate_pixels_from_nm

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