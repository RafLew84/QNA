# -*- coding: utf-8 -*-
"""
File consisting code for Intersection over Union window to pop from spots detection tab.

@author
rlewandkow
"""

import tkinter as tk
from tkinter import ttk

import copy

import logging

logger = logging.getLogger(__name__)

class IntersectionOverUnionWindow:
    """Class representing the iou window for spots detection in the application."""

    def __init__(self, app):
        self.app = app
        self.root = app.root

        self.data_for_analisys = []

    def open_new_window(self, data):
        new_window = tk.Toplevel(self.root)
        new_window.title("Intersection over Union")

        self.data_for_analisys = data