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
    "Erosion": {"kernel_type": "re", "kernel_size": 5, "iterations": 1}
}