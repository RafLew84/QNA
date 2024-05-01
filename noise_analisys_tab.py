# -*- coding: utf-8 -*-
"""


@author
"""

import os

import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, messagebox, Scrollbar, Text

from PIL import Image, ImageTk

import logging

logger = logging.getLogger(__name__)

class NoiseAnalysisTab:
    def __init__(self, notebook, app):
        self.noise_analisys_tab = ttk.Frame(notebook)
        notebook.add(self.noise_analisys_tab, text="Noise Analysis")
        self.app = app

        self.data = []

        self.create_noise_analisys_tab()


    def create_noise_analisys_tab(self):

        # Button to load data
        self.load_data_button = tk.Button(self.noise_analisys_tab, text="Load Data", command=self.load_data_onClick)
        self.load_data_button.grid(row=0, column=0, padx=5, pady=5)

        # Create listbox to display filenames
        self.data_listbox_analisys = tk.Listbox(self.noise_analisys_tab, width=20, height=10, selectmode=tk.SINGLE)
        self.data_listbox_analisys.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        self.data_listbox_analisys.bind("<<ListboxSelect>>", self.show_data_for_analisys)

        # Add a scrollbar for the listbox
        listbox_scrollbar = tk.Scrollbar(self.noise_analisys_tab, orient=tk.VERTICAL)
        listbox_scrollbar.grid(row=1, column=1, sticky="ns")
        self.data_listbox_analisys.config(yscrollcommand=listbox_scrollbar.set)
        listbox_scrollbar.config(command=self.data_listbox_analisys.yview)

        # Add a canvas to display the data
        self.data_canvas = tk.Canvas(self.noise_analisys_tab, bg="white")
        self.data_canvas.grid(row=0, column=2, rowspan=2, padx=5, pady=5, sticky="nsew")

        # Add vertical scrollbar
        v_scrollbar = tk.Scrollbar(self.noise_analisys_tab, orient=tk.VERTICAL, command=self.data_canvas.yview)
        v_scrollbar.grid(row=0, column=3, rowspan=2, sticky="ns")
        self.data_canvas.configure(yscrollcommand=v_scrollbar.set)

        # Add horizontal scrollbar
        h_scrollbar = tk.Scrollbar(self.noise_analisys_tab, orient=tk.HORIZONTAL, command=self.data_canvas.xview)
        h_scrollbar.grid(row=2, column=2, sticky="ew")
        self.data_canvas.configure(xscrollcommand=h_scrollbar.set)

        # Configure row and column weights for rescaling
        self.noise_analisys_tab.grid_rowconfigure(1, weight=1)
        self.noise_analisys_tab.grid_columnconfigure(0, weight=1)
        self.noise_analisys_tab.grid_columnconfigure(2, weight=1)

        # Bind the function to handle resizing events
        self.noise_analisys_tab.bind("<Configure>", self.resize_canvas_scrollregion)

    def load_data_onClick(self):
        self.data = self.app.get_data()
        self.insert_data_to_analisys()

    def resize_canvas_scrollregion(self, event):
        # Update the scroll region to cover the entire canvas
        self.data_canvas.config(scrollregion=self.data_canvas.bbox("all"))
    
    def insert_data_to_analisys(self):
        self.data_listbox_analisys.delete(0, tk.END)

        file_ext = self.data[0]['file_name'][-3:]
        for item in self.data:
            if file_ext.lower() == "stp" or file_ext.lower() == "s94":
                filename_only = os.path.basename(item['file_name'])
                self.data_listbox_analisys.insert(tk.END, filename_only)
            elif file_ext.lower() == "mpp":
                filename_only = os.path.basename(item['file_name'])
                for i, frame in enumerate(item['data'], start=1):
                    frame_name = f"{filename_only}: frame {i}"
                    self.data_listbox_analisys.insert(tk.END, frame_name)

    def show_data_for_analisys(self, event):
        file_ext = self.data[0]['file_name'][-3:]
        # Get the index of the selected filename
        selected_index = self.data_listbox_analisys.curselection()
        if selected_index:
            index = int(selected_index[0])
            # Get the corresponding data
            if file_ext.lower() == "stp" or file_ext.lower() == "s94":
                selected_data = self.data[index]
                self.display_analisys_image(selected_data)
            elif file_ext.lower() == "mpp":
                selected_name = self.data_listbox_analisys.get(index)
                parts = selected_name.split(':')
                mpp_file_name = parts[0].strip()
                frame_number = int(parts[1].strip().split()[1])
                mpp_data = None
                for item in self.data:
                    filename_only = os.path.basename(item['file_name'])
                    if filename_only == mpp_file_name:
                        mpp_data = item
                        break
                selected_data = mpp_data['data'][frame_number - 1]
                self.display_analisys_image(selected_data, True)

    def display_analisys_image(self, data, mpp=False):
        # Clear previous data
        self.data_canvas.delete("all")
        points = []
        if mpp:
            points = data
        else:
            points = data['data']
        
        # Create a new grayscale image
        img = Image.new('L', (len(points[0]), len(points)))

        # Normalize the values in data to the range [0, 255]
        max_z = max(map(max, points))
        min_z = min(map(min, points))
        if max_z == min_z:
            max_z += 1
        for i in range(len(points)):
            for j in range(len(points[i])):
                val = int(255 * (points[i][j] - min_z) / (max_z - min_z))
                img.putpixel((j, i), val)

        # Convert the PIL image to a Tkinter PhotoImage
        photo = ImageTk.PhotoImage(img)

        # Display the image on the canvas
        self.data_canvas.create_image(0, 0, anchor="nw", image=photo)

        # Save a reference to the PhotoImage to prevent garbage collection
        self.data_canvas.image = photo