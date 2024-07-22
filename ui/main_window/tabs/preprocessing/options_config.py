# -*- coding: utf-8 -*-
"""
Configuration options for preproces.

@author
rlewandkow
"""

import os, sys

sys.path.insert(1, "/".join(os.path.realpath(__file__).split("/")[0:-2]))

from ui.main_window.tabs.preprocessing.preprocess_params_default import preprocess_params

options_config = {
    "GaussianFilter": {
        "label_text": "sigma",
        "slider_config": {"from_": 0.1, "to": 4.0, "resolution": 0.05, "value": preprocess_params["GaussianFilter"]["sigma"]}
    },
    "Gamma Adjustment": {
        "label_text": "gamma",
        "slider_config": {"from_": 0.1, "to": 10.0, "resolution": 0.05, "value": preprocess_params["Gamma Adjustment"]["gamma"]}
    },
    "Adaptive Equalization": {
        "label_text": "limit",
        "slider_config": {"from_": 0.01, "to": 0.20, "resolution": 0.005, "value": preprocess_params["Adaptive Equalization"]["limit"]}
    },
    "Contrast Stretching": {
        "labels": [("min", preprocess_params["Contrast Stretching"]["min"]), ("max", preprocess_params["Contrast Stretching"]["max"])],
        "sliders": [
            {"from_": 1, "to": 99, "resolution": 1, "value": preprocess_params["Contrast Stretching"]["min"]},
            {"from_": 1, "to": 99, "resolution": 1, "value": preprocess_params["Contrast Stretching"]["max"]}
        ]
    },
    "Non-local Mean Denoising": {
        "labels": [
            ("h", preprocess_params["Non-local Mean Denoising"]["h"]),
            ("Template Window Size", preprocess_params["Non-local Mean Denoising"]["templateWindowSize"]),
            ("Search Window Size", preprocess_params["Non-local Mean Denoising"]["searchWindowSize"])
        ],
        "sliders": [
            {"from_": 0.1, "to": 10.0, "resolution": 0.1, "value": preprocess_params["Non-local Mean Denoising"]["h"]},
            {"from_": 3, "to": 21, "resolution": 1, "value": preprocess_params["Non-local Mean Denoising"]["templateWindowSize"]},
            {"from_": 3, "to": 51, "resolution": 1, "value": preprocess_params["Non-local Mean Denoising"]["searchWindowSize"]}
        ]
    },
    "Erosion": {
        "radio_buttons": [("Rectangle", "re"), ("Ellipse", "el"), ("Cross", "cr")],
        "labels": [("Kernel Size", preprocess_params["Erosion"]["kernel_size"]), ("Iterations", preprocess_params["Erosion"]["iterations"])],
        "sliders": [
            {"from_": 3, "to": 21, "resolution": 1, "value": preprocess_params["Erosion"]["kernel_size"]},
            {"from_": 1, "to": 5, "resolution": 1, "value": preprocess_params["Erosion"]["iterations"]}
        ]
    },
    "Propagation": {
        "radio_buttons": [("Dilation", "dilation"), ("Erosion", "erosion")],
        "labels": [("Margker value", preprocess_params["Propagation"]["marker_value"])],
        "sliders": [
            {"from_": 0.05, "to": 0.95, "resolution": 0.05, "value": preprocess_params["Propagation"]["marker_value"]}
        ]
    },
    "Polynomial Leveling": {
        "labels": [("Order", preprocess_params["Polynomial Leveling"]["order"])],
        "sliders": [
            {"from_": 2, "to": 20, "resolution": 1, "value": preprocess_params["Polynomial Leveling"]["order"]}
        ]
    },
    "Adaptive Leveling": {
        "labels": [("Disk size", preprocess_params["Adaptive Leveling"]["disk_size"])],
        "sliders": [
            {"from_": 2, "to": 50, "resolution": 1, "value": preprocess_params["Adaptive Leveling"]["disk_size"]}
        ]
    },
    "Local Median Filter": {
        "labels": [("Size", preprocess_params["Local Median Filter"]["size"])],
        "sliders": [
            {"from_": 2, "to": 20, "resolution": 1, "value": preprocess_params["Local Median Filter"]["size"]}
        ]
    },
    "Binary Greyscale Erosion": {
        "radio_buttons": [("Rectangle", "re"), ("Ellipse", "el"), ("Cross", "cr")],
        "label_text": "Kernel Size",
        "slider_config": {"from_": 3, "to": 21, "resolution": 1, "value": preprocess_params["Binary Greyscale Erosion"]["kernel_size"]}
    },
    "Gaussian Greyscale Erosion": {
        "labels": [("Mask Size", preprocess_params["Gaussian Greyscale Erosion"]["mask_size"]), ("Sigma", preprocess_params["Gaussian Greyscale Erosion"]["sigma"])],
        "sliders": [
            {"from_": 3, "to": 21, "resolution": 1, "value": preprocess_params["Gaussian Greyscale Erosion"]["mask_size"]},
            {"from_": 0.1, "to": 10, "resolution": 0.05, "value": preprocess_params["Gaussian Greyscale Erosion"]["sigma"]}
        ]
    },
    "Binary Greyscale Dilation": {
        "radio_buttons": [("Rectangle", "re"), ("Ellipse", "el"), ("Cross", "cr")],
        "label_text": "Kernel Size",
        "slider_config": {"from_": 3, "to": 21, "resolution": 1, "value": preprocess_params["Binary Greyscale Dilation"]["kernel_size"]}
    },
    "Gaussian Greyscale Dilation": {
        "labels": [("Mask Size", preprocess_params["Gaussian Greyscale Dilation"]["mask_size"]), ("Sigma", preprocess_params["Gaussian Greyscale Dilation"]["sigma"])],
        "sliders": [
            {"from_": 3, "to": 21, "resolution": 1, "value": preprocess_params["Gaussian Greyscale Dilation"]["mask_size"]},
            {"from_": 0.1, "to": 10, "resolution": 0.05, "value": preprocess_params["Gaussian Greyscale Dilation"]["sigma"]}
        ]
    },
    "Binary Greyscale Opening": {
        "radio_buttons": [("Rectangle", "re"), ("Ellipse", "el"), ("Cross", "cr")],
        "label_text": "Kernel Size",
        "slider_config": {"from_": 3, "to": 21, "resolution": 1, "value": preprocess_params["Binary Greyscale Opening"]["kernel_size"]}
    },
    "Gaussian Greyscale Opening": {
        "labels": [("Mask Size", preprocess_params["Gaussian Greyscale Opening"]["mask_size"]), ("Sigma", preprocess_params["Gaussian Greyscale Opening"]["sigma"])],
        "sliders": [
            {"from_": 3, "to": 21, "resolution": 1, "value": preprocess_params["Gaussian Greyscale Opening"]["mask_size"]},
            {"from_": 0.1, "to": 10, "resolution": 0.05, "value": preprocess_params["Gaussian Greyscale Opening"]["sigma"]}
        ]
    },
    "Binary Greyscale Closing": {
        "radio_buttons": [("Rectangle", "re"), ("Ellipse", "el"), ("Cross", "cr")],
        "label_text": "Kernel Size",
        "slider_config": {"from_": 3, "to": 21, "resolution": 1, "value": preprocess_params["Binary Greyscale Closing"]["kernel_size"]}
    },
    "White Top Hat": {
        "radio_buttons": [("Disk", "disk"), ("Square", "square"), ("Diamond", "diamond"), ("Star", "star")],
        "label_text": "Selem Size",
        "slider_config": {"from_": 2, "to": 30, "resolution": 1, "value": preprocess_params["White Top Hat"]["selem_size"]}
    },
    "Black Top Hat": {
        "radio_buttons": [("Disk", "disk"), ("Square", "square"), ("Diamond", "diamond"), ("Star", "star")],
        "label_text": "Selem Size",
        "slider_config": {"from_": 2, "to": 30, "resolution": 1, "value": preprocess_params["Black Top Hat"]["selem_size"]}
    },
    "Gaussian Greyscale Closing": {
        "labels": [("Mask Size", preprocess_params["Gaussian Greyscale Closing"]["mask_size"]), ("Sigma", preprocess_params["Gaussian Greyscale Closing"]["sigma"])],
        "sliders": [
            {"from_": 3, "to": 21, "resolution": 1, "value": preprocess_params["Gaussian Greyscale Closing"]["mask_size"]},
            {"from_": 0.1, "to": 10, "resolution": 0.05, "value": preprocess_params["Gaussian Greyscale Closing"]["sigma"]}
        ]
    },
    "Gaussian Sharpening": {
        "labels": [("Radius", preprocess_params["Gaussian Sharpening"]["radius"]), ("Amount", preprocess_params["Gaussian Sharpening"]["amount"])],
        "sliders": [
            {"from_": 0.1, "to": 10.0, "resolution": 0.05, "value": preprocess_params["Gaussian Sharpening"]["radius"]},
            {"from_": 0.1, "to": 10.0, "resolution": 0.05, "value": preprocess_params["Gaussian Sharpening"]["amount"]}
        ]
    }
}