# -*- coding: utf-8 -*-
"""
Main application module.

This module defines the main application class and the entry point of the application.

@author
rlewandkow
"""

import os, sys

sys.path.insert(1, "/".join(os.path.realpath(__file__).split("/")[0:-2]))

import tkinter as tk

from tkinter import ttk

from ui.main_window.tabs.load_data.load_data_tab import LoadDataTab
from ui.main_window.tabs.noise.noise_analisys_tab import NoiseAnalysisTab
from ui.main_window.tabs.detection.spots_detection_tab import SpotsDetectionTab
from ui.main_window.tabs.preprocessing.preprocessing_tab import PreprocessingTab
from ui.main_window.tabs.processing.processing_tab import ProcessingTab
from ui.main_window.tabs.spots_measurement.spots_measurement_tab import SpotsMeasurementTab

import logging

logger = logging.getLogger(__name__)

class App:
    """
    Main application class.

    This class represents the main application window and manages its components.

    Attributes:
        root (tk.Tk): The root Tkinter window.
        data (list): List to store application data.
        notebook (ttk.Notebook): Notebook widget for tabbed interface.
        load_data_tab (LoadDataTab): Tab for loading data.
        noise_analisys_tab (NoiseAnalysisTab): Tab for noise analysis.
        spots_detection_tab (SpotsDetectionTab): Tab for spots detection.
    """
    def __init__(self, root):
        """
        Initialize the main application.

        Args:
            root (tk.Tk): The root Tkinter window.
        """
        self.root = root
        self.root.title("QNA Software")

        self.data = []

        # Create a notebook (tabbed interface)
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self.load_data_tab = LoadDataTab(self.notebook, self)
        self.preprocessing_tab = PreprocessingTab(self.notebook, self)
        self.processing_tab = ProcessingTab(self.notebook, self)
        self.measurement_tab = SpotsMeasurementTab(self.notebook, self)
        self.spots_detection_tab = SpotsDetectionTab(self.notebook, self)
        self.noise_analisys_tab = NoiseAnalysisTab(self.notebook, self)

        # Configure grid row and column weights for rescaling
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

    def update_data(self, new_data):
        """
        Update application data.

        Args:
            new_data (list): New data to update the application data.
        """
        self.data = new_data

    def get_data(self):
        """
        Get application data.

        Returns:
            list: Application data.
        """
        return self.data

def main():
    root = tk.Tk()
    app = App(root)
    root.mainloop()

if __name__ == "__main__":
    main()