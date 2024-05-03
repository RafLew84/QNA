# -*- coding: utf-8 -*-
"""
Functions for data proccessing

@author: rlewandkow
"""
from math import sqrt
import numpy as np
from statistics import mean
from PIL import Image

import logging

logger = logging.getLogger(__name__)

def calculate_I_ISET_square(data, ISET):
    """
    Calculate the square of the difference between data and ISET.

    Parameters:
        data (numpy.ndarray): The data array.
        ISET (int or float): The ISET value.

    Returns:
        numpy.ndarray: The squared difference between data and ISET.

    Raises:
        TypeError: If data is not a numpy array or if ISET is not numeric.
        ValueError: If data is empty or if ISET is not a scalar value.
    """
    try:
        # Input validation
        if not isinstance(data, np.ndarray):
            raise TypeError("data must be a numpy array")
        if not np.isscalar(ISET) or isinstance(ISET, bool):
            raise TypeError("ISET must be a scalar numeric value")

        if not data.size:
            raise ValueError("data is empty")

        # Calculate square of difference
        return (data - ISET) ** 2
    except TypeError as te:
        msg = f"TypeError in calculate_I_ISET_square: {te}"
        logger.error(msg)
        raise TypeError(msg)
    except ValueError as ve:
        msg = f"ValueError in calculate_I_ISET_square: {ve}"
        logger.error(msg)
        raise ValueError(msg)
    except Exception as e:
        logger.error(f"Error in calculate_I_ISET_square: {e}")
        raise

def calculate_l0(data, mapISET = None):
    """
    Calculate the l0 value from input data.

    Parameters:
        data (numpy.ndarray): The input data array.
        mapISET (numpy.ndarray, optional): The mapISET array. Default is None.

    Returns:
        float: The calculated l0 value.

    Raises:
        ValueError: If input data is not a numpy array or if mapISET is provided but not a numpy array.
                    If the mean of data is negative or if the sum of mapISET is negative.
    """
    try:
        # Input validation
        if not isinstance(data, np.ndarray):
            raise ValueError("Input data must be a numpy array.")
        if mapISET is not None and not isinstance(mapISET, np.ndarray):
            raise ValueError("mapISET must be a numpy array if provided.")

        # Calculate l0
        l0 = None
        if mapISET is None:
            average = mean(data.flatten())
            if average < 0:
                raise ValueError("Cannot calculate l0 from negative values.")
            l0 = sqrt(average)
        else:
            length = np.prod(data.shape)
            mapISET_sum = np.sum(mapISET)
            if mapISET_sum < 0:
                raise ValueError("Cannot calculate l0 from negative values.")
            l0 = np.sqrt(mapISET_sum / length)

        return l0
    except ValueError as ve:
        msg = f"ValueError in calculate_l0: {ve}"
        logger.error(msg)
        raise ValueError(msg)
    except Exception as e:
        logger.error(f"Error in calculate_l0: {e}")
        raise

def create_greyscale_image(points):
    """
    Create a grayscale image from input data.

    Parameters:
        points (list): List of lists containing the data points.

    Returns:
        PIL.Image.Image: The created grayscale image.

    Raises:
        ValueError: If points is not a list of lists.
    """
    try:
        # Input validation
        if not isinstance(points, list) or not all(isinstance(row, list) for row in points):
            raise ValueError("Input points must be a list of lists.")

        # Create a new grayscale image
        img = Image.new('L', (len(points[0]), len(points)))

        # Normalize the values in data to the range [0, 255]
        max_z = max(map(max, points))
        min_z = min(map(min, points))
        if max_z == min_z:
            max_z += 1
        for i in range(len(points)):
            for j in range(len(points[i])):
                val = int(255 * (points[i][j] - min_z) / (max_z - min_z))
                img.putpixel((j, i), val)

        return img
    except ValueError as ve:
        msg = f"ValueError in create_greyscale_image: {ve}"
        logger.error(msg)
        raise ValueError(msg)
    except Exception as e:
        logger.error(f"Error in create_greyscale_image: {e}")
        raise