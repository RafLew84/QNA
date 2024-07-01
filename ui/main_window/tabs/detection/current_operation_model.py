# -*- coding: utf-8 -*-
"""
Module for spots detection in the application.

@author
rlewandkow
"""

import os, sys

sys.path.insert(1, "/".join(os.path.realpath(__file__).split("/")[0:-2]))

class CurrentOperation:
    def __init__(self):
        self._processed_image = None
        self._edge_image = None
        self._filtered_contours_img = None
        self._process_name = ""
        self._contours = []
        self._contours_data = []
        self._labels = []
        self._labeled_image = None

    @property
    def processed_image(self):
        return self._processed_image

    @processed_image.setter
    def processed_image(self, value):
        self._processed_image = value

    @property
    def edge_image(self):
        return self._edge_image

    @edge_image.setter
    def edge_image(self, value):
        self._edge_image = value

    @property
    def filtered_contours_img(self):
        return self._filtered_contours_img

    @filtered_contours_img.setter
    def filtered_contours_img(self, value):
        self._filtered_contours_img = value

    @property
    def process_name(self):
        return self._process_name

    @process_name.setter
    def process_name(self, value):
        self._process_name = value

    @property
    def contours(self):
        return self._contours

    @contours.setter
    def contours(self, value):
        self._contours = value

    @property
    def contours_data(self):
        return self._contours_data

    @contours_data.setter
    def contours_data(self, value):
        self._contours_data = value

    @property
    def labels(self):
        return self._labels

    @labels.setter
    def labels(self, value):
        self._labels = value

    @property
    def labeled_image(self):
        return self._labeled_image

    @labeled_image.setter
    def labeled_image(self, value):
        self._labeled_image = value