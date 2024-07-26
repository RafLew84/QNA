# -*- coding: utf-8 -*-
"""
Stores default values for preprocess tab.

@author
rlewandkow
"""

import os, sys

sys.path.insert(1, "/".join(os.path.realpath(__file__).split("/")[0:-2]))

# Parameters for image preprocessing methods
process_params = {
    "Otsu Threshold": {},
    "Local Threshold": {"method": "gaussian", "block_size": 3, "offset": 10},
    "Niblack Threshold": {"window_size": 5, "k": 0.8},
    "Sauvola Threshold": {"window_size": 5, "k": 0.8, "r": 128},
    "Yen Threshold": {},
    "ISODATA Threshold": {},
    "Binary Erosion": {"footprint_type": "disk", "footprint_size": 2},
    "Binary Dilation": {"footprint_type": "disk", "footprint_size": 2},
    "Binary Opening": {"footprint_type": "disk", "footprint_size": 2},
    "Binary Closing": {"footprint_type": "disk", "footprint_size": 2},
    "Remove Small Holes": {"area_threshold": 64, "connectivity": 1},
    "Remove Small Objects": {"min_size": 64, "connectivity": 1},
    "Manual Erase": {}
}