# -*- coding: utf-8 -*-
"""
Morphology functions for binary images

@author
"""

import os, sys
import numpy as np

sys.path.insert(1, "/".join(os.path.realpath(__file__).split("/")[0:-2]))

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import RectangleSelector

import logging

logger = logging.getLogger(__name__)

class ImageEditor:
    def __init__(self, image):
        self.original_image = image
        self.modified_image = image.copy()
        self.fig, self.ax = plt.subplots()
        self.rect_selector = RectangleSelector(self.ax, self.onselect,
                                               useblit=True,
                                               button=[1], minspanx=5, minspany=5,
                                               spancoords='pixels', interactive=True
                                               )
        self.ax.imshow(self.modified_image, cmap='gray')
        plt.connect('key_press_event', self.accept)
        plt.show()

    def onselect(self, eclick, erelease):
        """Callback function for rectangle selector."""
        x1, y1 = int(eclick.xdata), int(eclick.ydata)
        x2, y2 = int(erelease.xdata), int(erelease.ydata)
        self.modified_image[min(y1, y2):max(y1, y2), min(x1, x2):max(x1, x2)] = 0
        self.ax.imshow(self.modified_image, cmap='gray')
        plt.draw()

    def accept(self, event):
        if event.key == 'enter':
            plt.close(self.fig)

    def get_modified_image(self):
        return self.modified_image

def ImageEditRemoveWhite(image):
    editor = ImageEditor(image)
    return editor.get_modified_image()
