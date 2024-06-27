# -*- coding: utf-8 -*-
"""
Module for spots detection in the application.

@author
rlewandkow
"""

import os, sys

sys.path.insert(1, "/".join(os.path.realpath(__file__).split("/")[0:-2]))

saved_conoturs = []

def get_contours_data_at_index(index):
    contour_data = saved_conoturs[index]
    return contour_data

def get_contours_data():
    return saved_conoturs

def insert_contour(data):
    saved_conoturs.append(data)