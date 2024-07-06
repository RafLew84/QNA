# -*- coding: utf-8 -*-
"""
Module for data analisys in the application.

@author
rlewandkow
"""

import os, sys

sys.path.insert(1, "/".join(os.path.realpath(__file__).split("/")[0:-2]))

import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, messagebox, Scrollbar, Text

from PIL import ImageTk
from data.processing.data_process import convert_data_to_greyscale_image

import logging

logger = logging.getLogger(__name__)

class NoiseAnalysisTab:
    """Class representing the Noise Analysis tab in the application."""

    def __init__(self, notebook, app):
        """
        Initialize the NoiseAnalysisTab.

        Args:
            notebook (ttk.Notebook): The parent notebook where the tab will be added.
            app: The parent application instance.
        """

        self.noise_analisys_tab = ttk.Frame(notebook)
        notebook.add(self.noise_analisys_tab, text="Noise Analysis")
        self.app = app

        self.data = []

        self.create_noise_analisys_tab()


    def create_noise_analisys_tab(self):
        """
        Create the layout of the Noise Analysis tab.

        This method creates and organizes the widgets for the Noise Analysis tab.
        """

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
        """
        Handle the click event for the Load Data button.

        This method retrieves data from the parent application and inserts it into the analysis.
        """
        try:
            self.data = self.app.get_data()
            self.insert_data_to_analisys()
        except Exception as e:
            error_msg = f"Error loading data: {e}"
            logger.error(error_msg)
            messagebox.showerror("Error", error_msg)

    def resize_canvas_scrollregion(self, event):
        """
        Resize the scroll region of the canvas to cover the entire canvas area.

        This method is called when the size of the canvas changes to ensure that the scroll region
        is adjusted accordingly.
        
        :param event: The event object associated with the resizing event.
        """
            
        try:
        # Update the scroll region to cover the entire canvas
            self.data_canvas.config(scrollregion=self.data_canvas.bbox("all"))
        except Exception as e:
            error_msg = f"Error resizing canvas scroll region: {e}"
            logger.error(error_msg)
            messagebox.showerror("Error", error_msg)
    
    def insert_data_to_analisys(self):
        """
        Insert loaded data into the listbox for analysis.

        This method clears the existing items in the listbox and inserts filenames or frame names,
        depending on the file type, into the listbox for further analysis.
        """
        try:
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
        except Exception as e:
            error_msg = f"Error inserting data into analysis listbox: {e}"
            logger.error(error_msg)
            messagebox.showerror("Error", error_msg)

    def show_data_for_analisys(self, event):
        """
        Display selected data for analysis.

        This method retrieves the selected data from the listbox and displays it for analysis.
        """

        try:
            file_ext = self.data[0]['file_name'][-3:]
            # Get the index of the selected filename
            selected_index = self.data_listbox_analisys.curselection()
            if selected_index:
                index = int(selected_index[0])
                # Get the corresponding data
                if file_ext.lower() == "stp" or file_ext.lower() == "s94":
                    selected_data = self.data[index]
                    self.display_analisys_image(selected_data)
                # Extract data from mpp file
                elif file_ext.lower() == "mpp":
                    selected_name = self.data_listbox_analisys.get(index)
                    mpp_file_name, frame_number = self.extract_names_from_mpp_file(selected_name)
                    selected_data = self.get_data_from_frame(mpp_file_name, frame_number)
                    self.display_analisys_image(selected_data, True)
        except Exception as e:
            error_msg = f"Error displaying selected data for analysis: {e}"
            logger.error(error_msg)
            messagebox.showerror("Error", error_msg)

    def get_data_from_frame(self, mpp_file_name, frame_number):
        """
        Retrieve data from a specific frame of an MPP file.

        Parameters:
            mpp_file_name (str): The name of the MPP file.
            frame_number (int): The number of the frame to retrieve.

        Returns:
            numpy.ndarray: The data from the specified frame.

        Raises:
            ValueError: If the frame number is invalid.
            FileNotFoundError: If the MPP file is not found.
        """
        mpp_data = None
        for item in self.data:
            filename_only = os.path.basename(item['file_name'])
            if filename_only == mpp_file_name:
                mpp_data = item
                break
        if mpp_data is None:
            raise FileNotFoundError(f"MPP file '{mpp_file_name}' not found.")
        
        if frame_number < 1 or frame_number > len(mpp_data['data']):
            raise ValueError(f"Invalid frame number: {frame_number}")

        selected_data = mpp_data['data'][frame_number - 1]
        return selected_data

    def extract_names_from_mpp_file(self, selected_name):
        """
        Extract MPP file name and frame number from the selected name.

        Parameters:
            selected_name (str): The selected name from the listbox.

        Returns:
            tuple: A tuple containing the MPP file name and the frame number.

        Raises:
            ValueError: If the selected name format is invalid.
        """
        parts = selected_name.split(':')
        if len(parts) != 2:
            raise ValueError("Invalid selected name format.")
        mpp_file_name = parts[0].strip()
        frame_number = int(parts[1].strip().split()[1])
        return mpp_file_name, frame_number

    def display_analisys_image(self, data, mpp=False):
        """
        Display the analysis image on the canvas.

        Parameters:
            data (dict): The data to display.
            mpp (bool): Whether the data is from an MPP file.

        Raises:
            ValueError: If the data format is invalid.
            FileNotFoundError: If the image file is not found.
            Exception: For any other unexpected errors.
        """

        try:
            # Clear previous data
            self.data_canvas.delete("all")
            points = self.extract_data_from_file_dic(data, mpp)

            img = convert_data_to_greyscale_image(points)

            # Convert the PIL image to a Tkinter PhotoImage
            photo = ImageTk.PhotoImage(img)

            # Display the image on the canvas
            self.data_canvas.create_image(0, 0, anchor="nw", image=photo)

            # Save a reference to the PhotoImage to prevent garbage collection
            self.data_canvas.image = photo
        except ValueError as ve:
            msg = f"ValueError encountered while displaying analysis image: {ve}"
            logger.error(msg)
            raise ValueError(msg)
        except FileNotFoundError as fe:
            msg = f"FileNotFoundError encountered while displaying analysis image: {fe}"
            logger.error(msg)
            raise FileNotFoundError(msg)
        except Exception as e:
            msg = f"Error encountered while displaying analysis image: {e}"
            logger.error(msg)
            raise

    def extract_data_from_file_dic(self, data, mpp):
        """
        Extract data from the file dictionary depend on the filetype.

        Parameters:
            data (dict): The dictionary containing the data.
            mpp (bool): Whether the data is from an MPP file.

        Returns:
            list: The extracted data points.

        Raises:
            ValueError: If the data format is invalid.
            Exception: For any other unexpected errors.
        """
        try:
            if mpp:
                points = data
            else:
                points = data['data']
            return points
        except KeyError as ke:
            error_msg = f"KeyError encountered while extracting data from file dictionary: {ke}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        except Exception as e:
            error_msg = f"Error encountered while extracting data from file dictionary: {e}"
            logger.error(error_msg)
            raise