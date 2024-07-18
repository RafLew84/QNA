# -*- coding: utf-8 -*-
"""
Morphology functions

@author
"""

import os, sys

sys.path.insert(1, "/".join(os.path.realpath(__file__).split("/")[0:-2]))

import cv2

def Erosion(img, kernel_type="re", kernel_size=(5,5), iterations=1):
    kernel = None
    if kernel_type == "re":
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (kernel_size, kernel_size))
    if kernel_type == "el":
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kernel_size,kernel_size))
    elif kernel_type == "cr":
        kernel = cv2.getStructuringElement(cv2.MORPH_CROSS, (kernel_size,kernel_size))
    
    eroded_image = cv2.erode(img, kernel, iterations)

    return eroded_image