# -*- coding: utf-8 -*-
"""
Functions for operations on canvas

@author
rlewandkow
"""

import os, sys

sys.path.insert(1, "/".join(os.path.realpath(__file__).split("/")[0:-2]))

import cv2
import numpy as np
from PIL import Image, ImageTk

def get_mouse_position_in_canvas(scale_factor, x_canvas, y_canvas, event):
    """
    Calculate the mouse position on the canvas accounting for a given scale factor.

    Args:
        scale_factor (float): The factor by which the canvas is scaled.
        x_canvas (float): The x-coordinate of the mouse on the canvas.
        y_canvas (float): The y-coordinate of the mouse on the canvas.

    Returns:
        tuple: The recalculated x and y coordinates.
    """
    # x, y = event.x, event.y

    # # Recalculate the mouse coordinates relative to the resized canvas
    # x = event.x / scale_factor
    # y = event.y / scale_factor

    x = x_canvas / scale_factor
    y = y_canvas / scale_factor
    return x,y

def get_contour_info_at_position(current_operation, x, y):
    """
    Check if a point (x, y) is inside any contour in the current operation.

    Args:
        current_operation: The current operation containing contour data.
        x (float): The x-coordinate of the point.
        y (float): The y-coordinate of the point.

    Returns:
        dict or None: The contour data if the point is inside a contour, otherwise None.
    """
    # Iterate through contours and check if the mouse position is within any contour
    contours_data = current_operation.contours_data
    for item in contours_data:
        if is_point_inside_contour((x, y), item['contour']):
            return item
    return None

def is_point_inside_contour(point, contour):
    """
    Check if a point is inside a given contour.

    Args:
        point (tuple): The (x, y) coordinates of the point.
        contour (list): The contour points.

    Returns:
        bool: True if the point is inside the contour, False otherwise.
    """
    # Convert contour to numpy array of shape (n, 1, 2)
    contour_np = np.array(contour).reshape((-1, 1, 2))
    # Convert point to tuple
    point_tuple = tuple(point)
    # Use cv2.pointPolygonTest to determine if the point is inside the contour
    distance = cv2.pointPolygonTest(contour_np, point_tuple, False)
    # If distance is positive, point is inside the contour
    return distance >= 0