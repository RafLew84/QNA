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
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression

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

def ThreePointLeveling(img):

    image = np.array(img)

    # Callback function to capture the points clicked by the user
    def click_event(event, x, y, flags, params):
        if event == cv2.EVENT_LBUTTONDOWN:
            points.append((x, y))
            cv2.circle(image_display, (x, y), 5, (255, 0, 0), -1)
            cv2.imshow("Select three points to define a plane", image_display)
            if len(points) == 3:
                cv2.destroyAllWindows()

    image_display = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

    # Display the image and set up the callback for capturing points
    points = []
    cv2.imshow("Select three points to define a plane", image_display)
    cv2.setMouseCallback("Select three points to define a plane", click_event)
    cv2.waitKey(0)

    # Ensure three points are selected
    if len(points) != 3:
        raise ValueError("You must select exactly three points.")

    # Extract the coordinates of the selected points
    (x1, y1), (x2, y2), (x3, y3) = points

    # Get the pixel values at the selected points
    z1 = image[y1, x1]
    z2 = image[y2, x2]
    z3 = image[y3, x3]

    # Create matrices to solve for plane coefficients
    A = np.array([[x1, y1, 1], [x2, y2, 1], [x3, y3, 1]])
    B = np.array([z1, z2, z3])

    # Solve for plane coefficients
    plane_params = np.linalg.solve(A, B)
    a, b, c = plane_params
    print(f'Plane parameters: a={a}, b={b}, c={c}')

    # Create the fitted plane for the whole image
    rows, cols = image.shape
    X, Y = np.meshgrid(np.arange(cols), np.arange(rows))
    fitted_plane = a * X + b * Y + c

    # Subtract the fitted plane from the original image
    leveled_image = image - fitted_plane

    leveled_image_normalized = cv2.normalize(leveled_image, None, 0, 255, cv2.NORM_MINMAX)
    leveled_image_normalized = leveled_image_normalized.astype(np.uint8)

    return leveled_image_normalized

def fit_polynomial_surface(image, order=3):
    """Fit a polynomial surface to the image."""
    m, n = image.shape
    Y, X = np.mgrid[:m, :n]
    X = X.flatten()
    Y = Y.flatten()
    Z = image.flatten()

    poly = PolynomialFeatures(degree=order)
    X_poly = poly.fit_transform(np.column_stack((X, Y)))

    model = LinearRegression()
    model.fit(X_poly, Z)
    Z_poly = model.predict(X_poly)

    fitted_surface = Z_poly.reshape(m, n)
    return fitted_surface

def level_image_polynomial(image, order):
    """Level the image by subtracting the fitted polynomial surface."""
    polynomial_surface = fit_polynomial_surface(image, order=order)
    leveled_image = image - polynomial_surface
    return leveled_image

def PolynomialLeveling(img, order):
    image = img_as_float(img)

    # Level the image using polynomial fitting
    leveled_image = level_image_polynomial(image, order=order)

    leveled_image_normalized = cv2.normalize(leveled_image, None, 0, 255, cv2.NORM_MINMAX)
    leveled_image_normalized = leveled_image_normalized.astype(np.uint8)

    return leveled_image_normalized