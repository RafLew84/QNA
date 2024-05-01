# -*- coding: utf-8 -*-
"""


@author
"""

import tkinter as tk

from tkinter import ttk

from load_data_tab import LoadDataTab
from noise_analisys_tab import NoiseAnalysisTab
from spots_detection_tab import SpotsDetectionTab


import logging

logger = logging.getLogger(__name__)

class App:
    def __init__(self, root):
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
        self.data = new_data

    def get_data(self):
        return self.data

def main():
    root = tk.Tk()
    app = App(root)
    root.mainloop()

if __name__ == "__main__":
    main()