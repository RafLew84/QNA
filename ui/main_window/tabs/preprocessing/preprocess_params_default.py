# -*- coding: utf-8 -*-
"""
Stores default values for preprocess tab.

@author
rlewandkow
"""

import os, sys

sys.path.insert(1, "/".join(os.path.realpath(__file__).split("/")[0:-2]))

# Parameters for image preprocessing methods
preprocess_params = {
    "GaussianBlur": {"sigmaX": 5, "sigmaY": 5},
    "Non-local Mean Denoising": {"h": 3, "searchWindowSize": 21, "templateWindowSize": 7},
    "GaussianFilter": {"sigma": 4},
    "Erosion": {"kernel_type": "re", "kernel_size": 5, "iterations": 1},
    "Binary Greyscale Erosion": {"kernel_type": "re", "kernel_size": 3},
    "Gaussian Greyscale Erosion": {"mask_size": 3, "sigma": 1.0},
    "Binary Greyscale Dilation": {"kernel_type": "re", "kernel_size": 3},
    "Gaussian Greyscale Dilation": {"mask_size": 3, "sigma": 1.0},
    "Binary Greyscale Opening": {"kernel_type": "re", "kernel_size": 3},
    "Gaussian Greyscale Opening": {"mask_size": 3, "sigma": 1.0},
    "Binary Greyscale Closing": {"kernel_type": "re", "kernel_size": 3},
    "Gaussian Greyscale Closing": {"mask_size": 3, "sigma": 1.0},
    "Gamma Adjustment": {"gamma": 3.5},
    "Contrast Stretching": {"min": 2, "max": 98},
    "Adaptive Equalization": {"limit": 0.03},
    "Region Leveling": {},
    "Three Point Leveling": {},
    "Gaussian Sharpening": {"radius": 1.0, "amount": 1.0},
    "Propagation": {"type": "dilation", "marker_value": 0.3},
    "Polynomial Leveling": {"order": 3},
    "Adaptive Leveling": {"disk_size": 50},
    "Local Median Filter": {'size': 5}
}