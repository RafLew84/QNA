# -*- coding: utf-8 -*-
"""
Functions for image proccessing

@author
"""

import cv2
from scipy import ndimage as ndi

import numpy as np

from skimage import feature

def NlMeansDenois(img, h=3, searchWinwowSize=21, templateWindowSize=7):
    denoised_image = cv2.fastNlMeansDenoising(
        img, None, 
        h=h, 
        searchWindowSize=searchWinwowSize, 
        templateWindowSize=templateWindowSize
        )
    return denoised_image

def GaussianBlur(img, sigmaX=5, sigmaY=5, borderType=0):
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

def GaussianFilter(img, sigma=4):
    gaussian_image = ndi.gaussian_filter(
        input=img,
        sigma=sigma
    )
    return gaussian_image

def EdgeDetection(img, sigma=1.0, low_threshold=None, high_threshold=None):
    edges = feature.canny(
        image=img, 
        sigma=np.float64(sigma),
        low_threshold=low_threshold, 
        high_threshold=high_threshold
    )
    img = edges.astype('uint8') * 255
    return img

def ContourFinder(img):
    contours, _ = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    return contours