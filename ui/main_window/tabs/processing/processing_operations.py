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

from data.processing.thresholding import (
    OtsuThreshold,
    LocalThreshold,
    NiblackThreshold,
    SauvolaThreshold
)

def create_process_operation(processed_img, process_name, params):
    return {
        "processed_image": processed_img,
        "process_name": process_name,
        "params": params
    }

def perform_otsu_threshold(params, img):
    process_name = "Otsu Threshold"
    result_image = OtsuThreshold(
            img=np.array(img)
    )
    
    return process_name, result_image

def perform_local_threshold(params, img):
    process_name = "Local Threshold"
    result_image = LocalThreshold(
        img=np.array(img),
        method=params['method'],
        block_size=params['block_size'],
        offset=params['offset']
    )
    return process_name, result_image

def perform_niblack_threshold(params, img):
    process_name = "Niblack Threshold"
    result_image = NiblackThreshold(
        img=np.array(img),
        window_size=params['window_size'],
        k=params['k']
    )
    return process_name, result_image

def perform_sauvola_threshold(params, img):
    process_name = "Sauvola Threshold"
    result_image = SauvolaThreshold(
        img=np.array(img),
        window_size=params['window_size'],
        k=params['k'],
        r=params['r']
    )
    return process_name, result_image