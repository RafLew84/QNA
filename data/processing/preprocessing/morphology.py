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