# -*- coding: utf-8 -*-
"""
Leveling functions

@author
"""

import os, sys

sys.path.insert(1, "/".join(os.path.realpath(__file__).split("/")[0:-2]))

import cv2
import numpy as np
from scipy.optimize import least_squares
from skimage import img_as_float
import matplotlib.pyplot as plt

def fit_plane(image, region=None):
    rows, cols = image.shape
    
    # If a region is specified, use that region for fitting
    if region is not None:
        x_start, y_start, width, height = region
        x_end = x_start + width
        y_end = y_start + height
        image_region = image[y_start:y_end, x_start:x_end]
        
        X_region, Y_region = np.meshgrid(np.arange(x_start, x_end), np.arange(y_start, y_end))
        X_flat = X_region.flatten()
        Y_flat = Y_region.flatten()
        Z_flat = image_region.flatten()
    else:
        # Use the whole image
        X, Y = np.meshgrid(np.arange(cols), np.arange(rows))
        X_flat = X.flatten()
        Y_flat = Y.flatten()
        Z_flat = image.flatten()

    # Define the function to fit the plane
    def plane(params, x, y, z):
        a, b, c = params
        return a*x + b*y + c - z

    # Initial guess for the plane parameters
    initial_guess = [0, 0, np.mean(Z_flat)]

    # Perform least squares fitting
    result = least_squares(plane, initial_guess, args=(X_flat, Y_flat, Z_flat))

    # Get the fitted plane parameters
    a, b, c = result.x
    print(f'Plane parameters: a={a}, b={b}, c={c}')

    # Create the fitted plane for the whole image
    X, Y = np.meshgrid(np.arange(cols), np.arange(rows))
    fitted_plane = a * X + b * Y + c

    return fitted_plane

def RegionLeveling(img):
    image = np.array(img)

    # Display the original image for ROI selection
    cv2.imshow("Select ROI", image)
    roi = cv2.selectROI("Select ROI", image, fromCenter=False, showCrosshair=True)
    cv2.destroyAllWindows()

    # Check if ROI is selected, if not use the whole image
    if roi != (0, 0, 0, 0):
        region = roi
    else:
        region = None

    # Fit the plane
    fitted_plane = fit_plane(image, region)

    # Subtract the fitted plane from the original image
    leveled_image = image - fitted_plane
    leveled_image_normalized = cv2.normalize(leveled_image, None, 0, 255, cv2.NORM_MINMAX)
    leveled_image_normalized = leveled_image_normalized.astype(np.uint8)

    return leveled_image_normalized