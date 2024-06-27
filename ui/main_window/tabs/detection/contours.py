# -*- coding: utf-8 -*-
"""
Module for spots detection in the application.

@author
rlewandkow
"""

import os, sys

sys.path.insert(1, "/".join(os.path.realpath(__file__).split("/")[0:-2]))

def create_contour_data(filename, framenumber, operation, contours_num, originally_processed_image, original_data_index, x_coeff, y_coeff, area_coeff):
    data_to_save = {
        "filename": filename,
        "frame": framenumber,
        "operation": operation,
        "contours_num": contours_num,
        "originally_processed_image": originally_processed_image,
        "original_data_index": original_data_index,
        "x_coeff": x_coeff,
        "y_coeff": y_coeff,
        "area_coeff": area_coeff
    }

    return data_to_save