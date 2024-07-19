# -*- coding: utf-8 -*-
"""
Morphology functions

@author
"""

import os, sys

sys.path.insert(1, "/".join(os.path.realpath(__file__).split("/")[0:-2]))

import numpy as np
from skimage import exposure
from skimage import img_as_float

def GammaAdjustment(img, gamma):
    exposed_image = exposure.adjust_gamma(img, gamma)
    return exposed_image

def ContrastStretching(img, min, max):
    p_min, p_max = np.percentile(img, (min, max))
    exposed_image = exposure.rescale_intensity(img, in_range=(p_min, p_max))
    return exposed_image

def AdaptiveEqualization(img, limit):
    # image = img_as_float(img)
    exposed_image = exposure.equalize_adapthist(img, clip_limit=limit)
    return exposed_image

# from skimage import data, io
# from skimage import img_as_float
# import matplotlib.pyplot as plt

# # Load a sample grayscale image from skimage's data module
# image = io.imread('test_files/1.png', as_gray=True)

# # Define the clip limit for adaptive equalization
# clip_limit = 0.03  # Adjust this value as needed

# # Apply adaptive equalization
# equalized_image = AdaptiveEqualization(image, clip_limit)

# # Display the original and equalized images
# plt.figure(figsize=(10, 5))

# plt.subplot(1, 2, 1)
# plt.title("Original Image")
# plt.imshow(image, cmap='gray')
# plt.axis('off')

# plt.subplot(1, 2, 2)
# plt.title("Adaptive Equalized Image")
# plt.imshow(equalized_image, cmap='gray')
# plt.axis('off')

# plt.show()