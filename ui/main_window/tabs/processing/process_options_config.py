# -*- coding: utf-8 -*-
"""
Configuration options for proces.

@author
rlewandkow
"""

import os, sys

sys.path.insert(1, "/".join(os.path.realpath(__file__).split("/")[0:-2]))

from ui.main_window.tabs.processing.process_params_default import process_params

from ui.main_window.tabs.processing.processing_operations import (
    perform_otsu_threshold,
    perform_local_threshold,
    perform_niblack_threshold
)

options_config = {
    "Local Threshold": {
        "radio_buttons": [("Gaussian", "gaussian"), ("Mean", "mean"), ("Median", "median")],
        "labels": [("Block Size", process_params["Local Threshold"]["block_size"]), ("Offset", process_params["Local Threshold"]["offset"])],
        "sliders": [
            {"from_": 3, "to": 21, "resolution": 2, "value": process_params["Local Threshold"]["block_size"]},
            {"from_": 1, "to": 30, "resolution": 1, "value": process_params["Local Threshold"]["offset"]}
        ]
    },
    "Niblack Threshold": {
        "labels": [("Window size", process_params["Niblack Threshold"]["window_size"]), ("k", process_params["Niblack Threshold"]["k"])],
        "sliders": [
            {"from_": 3, "to": 51, "resolution": 2, "value": process_params["Niblack Threshold"]["window_size"]},
            {"from_": -1.0, "to": 1.0, "resolution": 0.05, "value": process_params["Niblack Threshold"]["k"]}
        ]
    },
}

process_operations = {
    "Otsu Threshold": perform_otsu_threshold,
    "Local Threshold": perform_local_threshold,
    "Niblack Threshold": perform_niblack_threshold
}