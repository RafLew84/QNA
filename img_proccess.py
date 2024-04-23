# -*- coding: utf-8 -*-
"""
Functions for image proccessing

@author
"""

import cv2

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