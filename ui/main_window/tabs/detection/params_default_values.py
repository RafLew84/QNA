# -*- coding: utf-8 -*-
"""
Stores data for detection tab.

@author
rlewandkow
"""

import os, sys

sys.path.insert(1, "/".join(os.path.realpath(__file__).split("/")[0:-2]))

# Parameters for image preprocessing methods
preprocess_params = {
    "GaussianBlur": {"sigmaX": 5, "sigmaY": 5},
    "Non-local Mean Denoising": {"h": 3, "searchWindowSize": 21, "templateWindowSize": 7},
    "GaussianFilter": {"sigma": 4}
}

# Parameters for spot detection methods
detection_params = {
    "Canny": {"sigma": 1.}
}

# Parameters for filters
filter_params = {
    "Circularity": {"circularity_low": 0.1, "circularity_high": 0.9},
    "Area": {"min_area_[nm2]": 0.0, "max_area_[nm2]": 1000}
}