# -*- coding: utf-8 -*-
"""
Module for spots detection in the application.

@author
rlewandkow
"""

import os, sys

sys.path.insert(1, "/".join(os.path.realpath(__file__).split("/")[0:-2]))

import numpy as np
import cv2
import matplotlib.pyplot as plt
from skimage import measure, morphology, color
from scipy.spatial import KDTree
from collections import defaultdict

# def process_image(image):
#     labeled_image = morphology.label(image)
#     regions = (labeled_image)
#     return labeled_image, regions

def label_image(img):
    labeled_image, regions_num = morphology.label(img, 0, True)
    return labeled_image, regions_num

def create_color_image(labeled_image):
    # Create a color map with distinct colors
    color_image = color.label2rgb(labeled_image, bg_label=0)
    color_image = (color_image * 255).astype(np.uint8)  # Convert to 8-bit color
    return color_image