# -*- coding: utf-8 -*-
"""
Morphology functions

@author
"""

import os, sys
import numpy as np

sys.path.insert(1, "/".join(os.path.realpath(__file__).split("/")[0:-2]))

import cv2
from scipy import ndimage
from skimage.morphology import reconstruction
from skimage import img_as_float
from skimage.morphology import (disk, white_tophat, black_tophat, 
                                square, diamond, star)

def Erosion(img, kernel_type="re", kernel_size=(5,5), iterations=1):
    kernel = binary_kernel(kernel_type, kernel_size)
    eroded_image = cv2.erode(img, kernel, iterations)
    return eroded_image

def BinaryGreyscaleErosion(img, kernel_type="re", kernel_size=(3,3)):
    kernel = binary_kernel(kernel_type, kernel_size)
    eroded_image = ndimage.grey_erosion(img, footprint=kernel)
    return eroded_image

def GaussianGreyscaleErosion(img, mask_size, sigma):
    gm = gaussian_mask(mask_size, sigma)
    eroded_image_gaussian = ndimage.grey_erosion(img, structure=gm)
    return eroded_image_gaussian

def BinaryGreyscaleDilation(img, kernel_type="re", kernel_size=(3,3)):
    kernel = binary_kernel(kernel_type, kernel_size)
    dilated_image = ndimage.grey_dilation(img, footprint=kernel)
    return dilated_image

def GaussianGreyscaleDilation(img, mask_size, sigma):
    gm = gaussian_mask(mask_size, sigma)
    dilated_image_gaussian = ndimage.grey_dilation(img, structure=gm)
    return dilated_image_gaussian

def BinaryGreyscaleOpening(img, kernel_type="re", kernel_size=(3,3)):
    kernel = binary_kernel(kernel_type, kernel_size)
    opened_image = ndimage.grey_opening(img, footprint=kernel)
    return opened_image

def GaussianGreyscaleOpening(img, mask_size, sigma):
    gm = gaussian_mask(mask_size, sigma)
    opened_image_gaussian = ndimage.grey_opening(img, structure=gm)
    return opened_image_gaussian

def BinaryGreyscaleClosing(img, kernel_type="re", kernel_size=(3,3)):
    kernel = binary_kernel(kernel_type, kernel_size)
    closed_image = ndimage.grey_closing(img, footprint=kernel)
    return closed_image

def GaussianGreyscaleClosing(img, mask_size, sigma):
    gm = gaussian_mask(mask_size, sigma)
    closed_image_gaussian = ndimage.grey_closing(img, structure=gm)
    return closed_image_gaussian

def Propagation(img, type, marker_value):
    marker = None
    img = img_as_float(img)
    if type == "dilation":
        marker = img - marker_value
        marker[marker < 0] = 0
    elif type == "erosion":
        marker = img + marker_value

    # Perform morphological reconstruction by dilation
    reconstructed_image = reconstruction(marker, img, method=type)

    return reconstructed_image

def WhiteTopHatTransformation(img, selem_type, selem_size):
    image = img_as_float(img) 
    selem = binary_selem(selem_type, selem_size)

    # Apply top-hat transformation
    tophat_image = white_tophat(image, selem)

    leveled_image_normalized = cv2.normalize(tophat_image, None, 0, 255, cv2.NORM_MINMAX)
    leveled_image_normalized = leveled_image_normalized.astype(np.uint8)

    return leveled_image_normalized

def BlackTopHatTransformation(img, selem_type, selem_size):
    image = img_as_float(img) 
    selem = binary_selem(selem_type, selem_size)

    # Apply top-hat transformation
    tophat_image = black_tophat(image, selem)

    leveled_image_normalized = cv2.normalize(tophat_image, None, 0, 255, cv2.NORM_MINMAX)
    leveled_image_normalized = leveled_image_normalized.astype(np.uint8)

    return leveled_image_normalized

def binary_selem(selem_type, selem_size):
    selem = None
    if selem_type == "disk":
        selem = disk(selem_size)
    elif selem_type == "square":
        selem = square(selem_size)
    elif selem_type == "diamond":
        selem = diamond(selem_size)
    elif selem_type == "star":
        selem = star(selem_size)
    
    return selem

def binary_kernel(kernel_type, kernel_size):
    kernel = None
    if kernel_type == "re":
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (kernel_size, kernel_size))
    if kernel_type == "el":
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kernel_size,kernel_size))
    elif kernel_type == "cr":
        kernel = cv2.getStructuringElement(cv2.MORPH_CROSS, (kernel_size,kernel_size))
    return kernel

def gaussian_kernel(size, sigma=1):
    ax = np.linspace(-(size - 1) / 2., (size - 1) / 2., size)
    xx, yy = np.meshgrid(ax, ax)
    kernel = np.exp(-0.5 * (np.square(xx) + np.square(yy)) / np.square(sigma))
    return kernel / np.sum(kernel)

def gaussian_mask(size, sigma):
    gaussian_mask = gaussian_kernel(size, sigma)
    return gaussian_mask