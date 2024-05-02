# -*- coding: utf-8 -*-
"""
Main application module.

This module defines the main application class and the entry point of the application.

@author
rlewandkow
"""

import tkinter as tk

from tkinter import ttk

from load_data_tab import LoadDataTab
from noise_analisys_tab import NoiseAnalysisTab
from spots_detection_tab import SpotsDetectionTab

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
        self.noise_analisys_tab = NoiseAnalysisTab(self.notebook, self)
        self.spots_detection_tab = SpotsDetectionTab(self.notebook, self)

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