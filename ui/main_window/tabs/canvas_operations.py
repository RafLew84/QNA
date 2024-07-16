# -*- coding: utf-8 -*-
"""
Functions for operations on canvas

@author
rlewandkow
"""

import os, sys

sys.path.insert(1, "/".join(os.path.realpath(__file__).split("/")[0:-2]))

from PIL import Image, ImageTk

def scale_factor_resize_image(img, scale_factor):
    """
    Resize an image by a given scale factor.

    Args:
        img (PIL.Image.Image): The input image.
        scale_factor (float): The scale factor to resize the image.

    Returns:
        PIL.Image.Image: The resized image.
    """
    return img.resize((int(img.width * scale_factor), int(img.height * scale_factor)), Image.LANCZOS)