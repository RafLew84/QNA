# -*- coding: utf-8 -*-
"""
Functions for image proccessing

@author
rlewadkow
"""

import os, sys

sys.path.insert(1, "/".join(os.path.realpath(__file__).split("/")[0:-2]))

import cv2
from scipy import ndimage as ndi

import numpy as np

from skimage import feature

from PIL import Image

import logging

from data.processing.file_process import calculate_pixels_from_nm

from data.processing.contours.contour_detection import (
    ContourFilter
)

logger = logging.getLogger(__name__)

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
