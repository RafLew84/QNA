# -*- coding: utf-8 -*-
"""
Functions for image proccessing

@author
"""

import cv2
from scipy import ndimage as ndi

import numpy as np

from skimage import feature

from PIL import Image

import logging

from file_process import calculate_pixels_from_nm

logger = logging.getLogger(__name__)

def NlMeansDenois(img, h=3, searchWinwowSize=21, templateWindowSize=7):
    """
    Apply Non-Local Means Denoising to the input image.

    Args:
        img (numpy.ndarray): Input image.
        h (float, optional): Parameter regulating filter strength. Higher h value removes noise better, but removes details of image also. Defaults to 3.
        searchWinwowSize (int, optional): Size in pixels of the window to be used for searching matches. Larger value implies that farther pixels will influence each other. Defaults to 21.
        templateWindowSize (int, optional): Size in pixels of the window to be used for gathering pixel values. Defaults to 7.

    Returns:
        numpy.ndarray: Denoised image.
    """
    try:
        denoised_image = cv2.fastNlMeansDenoising(
            img, None,
            h=h,
            searchWindowSize=searchWinwowSize,
            templateWindowSize=templateWindowSize
        )
        return denoised_image
    except Exception as e:
        msg = f"NlMeansDenois error: {e}"
        logger.error(msg)
        raise ValueError(msg)

def GaussianBlur(img, sigmaX=5, sigmaY=5, borderType=0):
    """
    Apply Gaussian blur to the input image.

    Args:
        img (numpy.ndarray): Input image.
        sigmaX (float, optional): Standard deviation in X direction. Defaults to 5.
        sigmaY (float, optional): Standard deviation in Y direction. Defaults to 5.
        borderType (int, optional): Border mode. Defaults to 0.

    Returns:
        numpy.ndarray: Blurred image.
    """
    try:
        if sigmaX <= 0 or sigmaX % 2 == 0:
            raise ValueError("sigmaX must be a positive odd number")
        if sigmaY <= 0 or sigmaY % 2 == 0:
            raise ValueError("sigmaY must be a positive odd number")
        blurred_image = cv2.GaussianBlur(
            img,
            (sigmaX, sigmaY),
            borderType
        )
        return blurred_image
    except Exception as e:
        msg = f"GaussianBlur error: {e}"
        logger.error(msg)
        raise ValueError(msg)

def GaussianFilter(img, sigma=4):
    """
    Apply Gaussian filter to the input image.

    Args:
        img (numpy.ndarray): Input image.
        sigma (float, optional): Standard deviation for Gaussian kernel. Defaults to 4.

    Returns:
        numpy.ndarray: Filtered image.
    """
    try:
        gaussian_image = ndi.gaussian_filter(
            input=img,
            sigma=sigma
        )
        return gaussian_image
    except Exception as e:
        msg = f"GaussianFilter error: {e}"
        logger.error(msg)
        raise ValueError(msg)

def EdgeDetection(img, sigma=1.0):
    """
    Perform edge detection on the input image using Canny edge detector.

    Args:
        img (numpy.ndarray): Input image.
        sigma (float, optional): Standard deviation for Gaussian smoothing. Defaults to 1.0.
    Returns:
        numpy.ndarray: Edge-detected image.
    """
    try:
        edges = feature.canny(
            image=img,
            sigma=np.float64(sigma)
        )
        img = edges.astype('uint8') * 255
        return img
    except Exception as e:
        msg = f"EdgeDetection error: {e}"
        logger.error(msg)
        raise ValueError(msg)

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
        # area = cv2.contourArea(contour)
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
        (x, y), radius = cv2.minEnclosingCircle(contour)
        aprox_area = np.pi * (radius ** 2)
        contour_data.append({
            "name": name,
            "contour": contour,
            "area": aprox_area * area_coefficient,
            "moments": M,
            "distance_to_nearest_neighbour": min_distance,
            "nearest_neighbour": f"{min_index:03}"
        })

    return contour_data

def DrawLabels(img, contours_data, draw_contours=False, draw_labels=False, color=False, highlight_index=None):
    for i, item in enumerate(contours_data):
        if color:
            text_color = (255,255,255)
        elif highlight_index == i:
            text_color = (169, 169, 169)
        else:
            text_color = (0,0,0)
        M = item['moments']
        name = item['name']
        img = np.array(img).astype(np.uint8)
        if M["m00"] != 0:
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
            if draw_labels:
                img = cv2.putText(img, name, (cX, cY), cv2.FONT_HERSHEY_SIMPLEX, 0.3, text_color, 1)
        if draw_contours:
                img = cv2.drawContours(img, [item['contour']], 0, text_color, 1)
    
    return img
    
def ContourFilter(contours, circularity_low=0.1, circularity_high=0.9, min_area=0.0, max_area=200):
    filtered_contours = []
    for contour in contours:
        area = AreaOfContour(contour)
        perimeter = PerimieterOfContour(contour)
        circularity = FindCircularityOfContour(area, perimeter)

        if circularity_low < circularity < circularity_high and max_area > area > min_area:
            filtered_contours.append(contour)
    
    return filtered_contours

def DrawContours(image, contours, color=(255, 255, 255), thickness=1):
    """
    Draw contours on the input image.

    Args:
        image (numpy.ndarray): Input image.
        contours (list): List of contours.
        color (tuple, optional): Contour color. Defaults to (255, 255, 255).
        thickness (int, optional): Contour thickness. Defaults to 1.

    Returns:
        numpy.ndarray: Image with contours drawn.
    """
    img_with_contours = np.zeros_like(image)
    cv2.drawContours(img_with_contours, contours, -1, color, thickness)
    return img_with_contours
    
def concatenate_two_images(processed_img, original_img):
    """
    Concatenate two images side by side.

    Args:
        processed_img (PIL.Image.Image): The processed image.
        original_img (PIL.Image.Image): The original image.

    Returns:
        PIL.Image.Image: The concatenated image.
    """
    img = Image.new('RGB', (processed_img.width + original_img.width + 10, max(processed_img.height, original_img.height)))
    img.paste(processed_img, (0, 0))
    img.paste(original_img, (processed_img.width + 10, 0))
    return img

def concatenate_four_images(processed_img, original_img, edged_image, filtered_contoures_image):
    # Calculate the widths and heights of the images
    widths = sorted([processed_img.width, original_img.width, edged_image.width, filtered_contoures_image.width], reverse=True)[:2]
    heights = sorted([processed_img.height, original_img.height, edged_image.height, filtered_contoures_image.height], reverse=True)[:2]

    # Calculate the width and height of the concatenated image
    width = sum(widths)
    height = sum(heights)

    # Create a new blank image with the calculated dimensions
    img = Image.new('RGB', (width, height))

    # Paste the images onto the blank image
    img.paste(original_img, (0, 0))
    img.paste(edged_image, (0, processed_img.height + 10))
    img.paste(filtered_contoures_image, (processed_img.width + 10, 0))
    img.paste(processed_img, (processed_img.width + 10, processed_img.height + 10))

    return img

def get_mouse_position_in_canvas(scale_factor, x_canvas, y_canvas, event):
    x, y = event.x, event.y

    # Recalculate the mouse coordinates relative to the resized canvas
    x = event.x / scale_factor
    y = event.y / scale_factor

    x = x_canvas / scale_factor
    y = y_canvas / scale_factor
    return x,y

def get_contour_info_at_position(current_operation, x, y):
    # Iterate through contours and check if the mouse position is within any contour
    contours_data = current_operation['contours_data']
    for item in contours_data:
        if is_point_inside_contour((x, y), item['contour']):
            return item
    return None

def is_point_inside_contour(point, contour):
    # Convert contour to numpy array of shape (n, 1, 2)
    contour_np = np.array(contour).reshape((-1, 1, 2))
    # Convert point to tuple
    point_tuple = tuple(point)
    # Use cv2.pointPolygonTest to determine if the point is inside the contour
    distance = cv2.pointPolygonTest(contour_np, point_tuple, False)
    # If distance is positive, point is inside the contour
    return distance >= 0

def calculate_contour_avg_area(contour_data):
    total_area = sum(contour['area'] for contour in contour_data)
    avg_area = 0
    if len(contour_data) > 0:
        avg_area = total_area / len(contour_data)
    return avg_area

def process_contours_filters(filter_params, edge_img, contours, coeff):
    min_area_nm = filter_params['min_area_[nm2]']
    max_area_nm = filter_params['max_area_[nm2]']

    min_area_px = calculate_pixels_from_nm(min_area_nm, coeff)
    max_area_px = calculate_pixels_from_nm(max_area_nm, coeff)
    
    filtered_contours = ContourFilter(
            contours= contours,
            circularity_low= filter_params['circularity_low'],
            circularity_high= filter_params['circularity_high'],
            min_area= min_area_px,
            max_area= max_area_px
        )
    result_image = DrawContours(
            image= edge_img,
            contours= filtered_contours
        )
    
    return result_image,filtered_contours
