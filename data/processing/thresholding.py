# -*- coding: utf-8 -*-
"""
Functions for image proccessing

@author
rlewadkow
"""

import os, sys

sys.path.insert(1, "/".join(os.path.realpath(__file__).split("/")[0:-2]))

import cv2

from skimage.filters import (
    threshold_otsu,
    threshold_local,
    threshold_multiotsu,
    threshold_niblack, 
    threshold_sauvola,
    threshold_yen,
    threshold_isodata
)


def OtsuThreshold(img):
    thresh = threshold_otsu(img)
    threshold_image = img > thresh

    return threshold_image

def LocalThreshold(img, method, block_size, offset):
    threshold_image = img < threshold_local(
        image=img, 
        method=method, 
        block_size=block_size, 
        offset=offset
        )

    return threshold_image

def NiblackThreshold(img, window_size, k):
    threshold_image = img > threshold_niblack(img, window_size=window_size, k=k)

    return threshold_image

def SauvolaThreshold(img, window_size, k, r):
    threshold_image = img < threshold_sauvola(img, window_size=window_size, k=k, r=r)

    return threshold_image

def YenThreshold(img):
    thresh = threshold_yen(img)
    threshold_image = img > thresh

    return threshold_image

def IsodataThreshold(img):
    thresh = threshold_isodata(img)
    threshold_image = img > thresh

    return threshold_image

def BinaryThreshold(img, threshold):
    _, binary_image = cv2.threshold(img, threshold, 255, cv2.THRESH_BINARY)
    return binary_image
