# -*- coding: utf-8 -*-
"""
Functions for image proccessing

@author
rlewadkow
"""

import os, sys

sys.path.insert(1, "/".join(os.path.realpath(__file__).split("/")[0:-2]))

import cv2

import numpy as np

import logging

logger = logging.getLogger(__name__)

def ContourFinder(img):
    """
    Find contours in the input image.

    Args:
        img (numpy.ndarray): Input image.

    Returns:
        list: List of contours.
    """
    try:
        contours, _ = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        return contours
    except Exception as e:
        msg = f"ContourFinder error: {e}"
        logger.error(msg)
        raise ValueError(msg)
    
def AreaOfContour(contour):
    area = cv2.contourArea(contour)
    return area

def PerimieterOfContour(contour):
    perimeter = cv2.arcLength(contour, True)
    return perimeter

def FindCircularityOfContour(area, perimeter):
    if perimeter > 0:
        circularity = 4 * np.pi * area / (perimeter * perimeter)
    else:
        circularity = 0
    return circularity

def distance_between_points_in_nm(point1, point2, x_coeff, y_coeff):
    """
    Calculate Euclidean distance between two points in nanometers (nm).
    Assumes point coordinates are given in pixels and converts them to nanometers using the provided coefficients.
    """
    
    # Convert pixel coordinates to nanometers using the provided coefficients
    point1_nm = np.array([point1[0] * x_coeff, point1[1] * y_coeff])
    point2_nm = np.array([point2[0] * x_coeff, point2[1] * y_coeff])
    
    # Calculate Euclidean distance in nanometers
    distance_nm = np.linalg.norm(point1_nm - point2_nm)
    
    return distance_nm

def GetContourData(filtered_contours, x_size_coefficient, y_size_coefficient, avg_coefficient):
    contour_data = []
    centroids = []
    area_coefficient = avg_coefficient
    for i, contour in enumerate(filtered_contours):
        M = cv2.moments(contour)
        if M["m00"] != 0:
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
            centroids.append((cX, cY))

    for i, contour in enumerate(filtered_contours):
        name = f"{i:03}"
        # calculate nearest neighbour for filtered_contour
        distances_to_other_contours = []
        min_distance = None
        min_index = None
        area = cv2.contourArea(contour)
        M = cv2.moments(contour)
        if M["m00"] != 0:
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
        if centroids:
            for j in range(len(filtered_contours)):
                if i != j:
                    distance = distance_between_points_in_nm(centroids[i], centroids[j], x_size_coefficient, y_size_coefficient)
                    distances_to_other_contours.append((distance, j))
            if len(distances_to_other_contours) > 1:
                min_distance, min_index = min(distances_to_other_contours)
        else:
            min_distance = 0.0
        # add distance and nearest_neighbour to dic
        if not min_distance:
            min_distance = 0.0
        if not min_index:
            min_index = -1
        
        contour_data.append({
            "name": name,
            "contour": contour,
            "area": area * area_coefficient,
            "moments": M,
            "distance_to_nearest_neighbour": min_distance,
            "nearest_neighbour": f"{min_index:03}"
        })

    return contour_data

def ContourFilter(contours, circularity_low=0.1, circularity_high=0.9, min_area=0.0, max_area=200):
    filtered_contours = []
    for contour in contours:
        area = AreaOfContour(contour)
        perimeter = PerimieterOfContour(contour)
        circularity = FindCircularityOfContour(area, perimeter)

        if circularity_low < circularity < circularity_high and max_area > area > min_area:
            filtered_contours.append(contour)
    
    return filtered_contours

def calculate_contour_avg_area(contour_data):
    total_area = sum(contour['area'] for contour in contour_data)
    avg_area = 0
    if len(contour_data) > 0:
        avg_area = total_area / len(contour_data)
    return avg_area