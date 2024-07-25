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
    perform_niblack_threshold,
    perform_sauvola_threshold,
    perform_yen_threshold,
    perform_isodata_threshold,
    perform_binary_erosion,
    perform_binary_dilation,
    perform_binary_opening,
    perform_binary_closing
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
            {"from_": -5.0, "to": 5.0, "resolution": 0.05, "value": process_params["Niblack Threshold"]["k"]}
        ]
    },
    "Sauvola Threshold": {
        "labels": [("Window size", process_params["Sauvola Threshold"]["window_size"]), ("k", process_params["Sauvola Threshold"]["k"]), ("r", process_params["Sauvola Threshold"]["r"])],
        "sliders": [
            {"from_": 3, "to": 51, "resolution": 2, "value": process_params["Sauvola Threshold"]["window_size"]},
            {"from_": -5.0, "to": 5.0, "resolution": 0.05, "value": process_params["Sauvola Threshold"]["k"]},
            {"from_": 32, "to": 512, "resolution": 32, "value": process_params["Sauvola Threshold"]["r"]}
        ]
    },
    "Binary Erosion": {
        "radio_buttons": [("Disk", "disk"), ("Square", "square"), ("Star", "star"), ("Diamond", "diamond")],
        "labels": [("Footprint Size", process_params["Binary Erosion"]["footprint_size"])],
        "sliders": [
            {"from_": 1, "to": 50, "resolution": 1, "value": process_params["Binary Erosion"]["footprint_size"]}
        ]
    },
    "Binary Dilation": {
        "radio_buttons": [("Disk", "disk"), ("Square", "square"), ("Star", "star"), ("Diamond", "diamond")],
        "labels": [("Footprint Size", process_params["Binary Dilation"]["footprint_size"])],
        "sliders": [
            {"from_": 1, "to": 50, "resolution": 1, "value": process_params["Binary Dilation"]["footprint_size"]}
        ]
    },
    "Binary Opening": {
        "radio_buttons": [("Disk", "disk"), ("Square", "square"), ("Star", "star"), ("Diamond", "diamond")],
        "labels": [("Footprint Size", process_params["Binary Opening"]["footprint_size"])],
        "sliders": [
            {"from_": 1, "to": 50, "resolution": 1, "value": process_params["Binary Opening"]["footprint_size"]}
        ]
    },
    "Binary Closing": {
        "radio_buttons": [("Disk", "disk"), ("Square", "square"), ("Star", "star"), ("Diamond", "diamond")],
        "labels": [("Footprint Size", process_params["Binary Closing"]["footprint_size"])],
        "sliders": [
            {"from_": 1, "to": 50, "resolution": 1, "value": process_params["Binary Closing"]["footprint_size"]}
        ]
    },
}

process_operations = {
    "Otsu Threshold": perform_otsu_threshold,
    "Local Threshold": perform_local_threshold,
    "Niblack Threshold": perform_niblack_threshold,
    "Sauvola Threshold": perform_sauvola_threshold,
    "Yen Threshold": perform_yen_threshold,
    "ISODATA Threshold": perform_isodata_threshold,
    "Binary Erosion": perform_binary_erosion,
    "Binary Dilation": perform_binary_dilation,
    "Binary Opening": perform_binary_opening,
    "Binary Closing": perform_binary_closing
}