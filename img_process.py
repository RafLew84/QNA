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

def EdgeDetection(img, sigma=1.0, low_threshold=None, high_threshold=None):
    """
    Perform edge detection on the input image using Canny edge detector.

    Args:
        img (numpy.ndarray): Input image.
        sigma (float, optional): Standard deviation for Gaussian smoothing. Defaults to 1.0.
        low_threshold (float, optional): Lower bound for hysteresis thresholding. If None, low_threshold is set to 0.1 * np.max(image_grad). Defaults to None.
        high_threshold (float, optional): Upper bound for hysteresis thresholding. If None, high_threshold is set to 0.2 * np.max(image_grad). Defaults to None.

    Returns:
        numpy.ndarray: Edge-detected image.
    """
    try:
        edges = feature.canny(
            image=img,
            sigma=np.float64(sigma),
            low_threshold=low_threshold,
            high_threshold=high_threshold
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

def AreaFinder(contours, nm):
    areas = []
    for contour in contours:
        area = AreaOfContour(contour)
        areas.append({
          "contour": contour,
          "area": area * nm  
        })
    return areas

def GetContourData(self, filtered_contours):
    contour_data = []
    for i, contour in enumerate(filtered_contours):
        name = f"P{i:03}"
        area = cv2.contourArea(contour)
        M = cv2.moments(contour)

        contour_data.append({
            "name": name,
            "contour": contour,
            "area": area,
            "moments": M
        })

    return contour_data

def DrawLabels(img, contours_data):
    for item in contours_data:
        M = item['moments']
        name = item['name']
        img = np.asanyarray(img)
        if M["m00"] != 0:
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
            # Draw contour
            # Put text
            labeled_img = cv2.putText(img, name, (cX, cY), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (0, 255, 255), 1)
        labeled_img = cv2.drawContours(img, [item['contour']], 0, (0, 255, 255), 1)
    
    return labeled_img
    
def ContourFilter(contours, circularity_low=0.1, circularity_high=0.9, min_area=0.0):
    filtered_contours = []
    for contour in contours:
        area = AreaOfContour(contour)
        perimeter = PerimieterOfContour(contour)
        circularity = FindCircularityOfContour(area, perimeter)

        if circularity_low < circularity < circularity_high and area > min_area:
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
    img.paste(processed_img, (0, 0))
    img.paste(original_img, (0, processed_img.height + 10))
    img.paste(edged_image, (processed_img.width + 10, 0))
    img.paste(filtered_contoures_image, (processed_img.width + 10, processed_img.height + 10))

    return img