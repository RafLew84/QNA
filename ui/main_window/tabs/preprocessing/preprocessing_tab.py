# -*- coding: utf-8 -*-
"""
Module for preprocessing in the application.

@author
rlewandkow
"""

import os, sys

sys.path.insert(1, "/".join(os.path.realpath(__file__).split("/")[0:-2]))

import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

from ui.main_window.tabs.preprocessing.preprocessing_data import (
    data_for_preprocessing,
    get_file_extension,
    get_filename_at_index,
    get_header_info_at_index,
    get_framenumber_at_index,
    get_mpp_labels,
    get_s94_labels,
    get_stp_labels
)

from ui.main_window.tabs.preprocessing.preprocess_params_default import (
    preprocess_params
)

import logging

logger = logging.getLogger(__name__)

class PreprocessingTab:
    """Class representing the tab for spots detection in the application."""

    def __init__(self, notebook, app):

        self.preprocessing_tab = ttk.Frame(notebook)
        notebook.add(self.preprocessing_tab, text="Preprocessing")
        self.app = app
        self.root = app.root

        self.selected_preprocess_option = None

        self.load_params()

        self.create_preprocessing_tab()

    def create_preprocessing_tab(self):
        self.configure_tab()
        self.create_data_ui()
        self.create_canvas_ui()
        self.create_scaling_ui()
        self.create_navigation_ui()

        # Display header information labels
        self.header_section_frame = ttk.Frame(self.preprocessing_tab, padding="5")
        self.header_section_frame.grid(row=0, column=2, padx=5, pady=2, sticky="nsew")

        # Header section name label
        self.header_section_name_label = tk.Label(self.header_section_frame, text="Header Info:")
        self.header_section_name_label.grid(row=0, column=0, padx=5, pady=2, sticky="e")

        # Display Proccess Options
        self.preprocess_section_menu = ttk.Frame(self.preprocessing_tab, padding="3")
        self.preprocess_section_menu.grid(row=0, column=5,rowspan=2, columnspan=2, padx=5, pady=2, sticky="nsew")

        self.display_header_info_labels()
        self.display_detection_section_menu()
    
    def load_params(self):
        """
        Load parameters for detection, filtering, and preprocessing.

        Attributes:
            preprocess_params (dict): Parameters for image preprocessing methods.
            detection_params (dict): Parameters for spot detection methods.
            filter_params (dict): Parameters for filtering methods.
        """
        self.preprocess_params = preprocess_params

    def configure_tab(self):
        # Set row and column weights
        self.preprocessing_tab.grid_rowconfigure(1, weight=1)
        self.preprocessing_tab.grid_columnconfigure(2, weight=1)

    def create_data_ui(self):
        # Button to load data
        self.load_data_button = tk.Button(
            self.preprocessing_tab, 
            text="Load Data", 
            command=self.load_data_onClick
            )
        self.load_data_button.grid(row=0, column=0, padx=5, pady=5)
        
        # Create listbox to display filenames
        self.data_listbox_detection = tk.Listbox(
            self.preprocessing_tab, 
            width=20, 
            height=10, 
            selectmode=tk.SINGLE
            )
        self.data_listbox_detection.grid(row=1, column=0, rowspan=2, padx=5, pady=5, sticky="nsew")
        self.listbox_scrollbar_detection = tk.Scrollbar(
            self.preprocessing_tab, 
            orient=tk.VERTICAL, 
            command=self.data_listbox_detection.yview
            )
        self.listbox_scrollbar_detection.grid(row=1, column=1, rowspan=2, sticky="ns")
        self.data_listbox_detection.config(yscrollcommand=self.listbox_scrollbar_detection.set)
        self.data_listbox_detection.bind("<<ListboxSelect>>", self.show_data_onDataListboxSelect)

    def load_data_onClick(self):
        pass

    def show_data_onDataListboxSelect(self):
        pass

    def create_navigation_ui(self):
        # Slider for navigation
        self.navigation_slider = tk.Scale(
            self.preprocessing_tab, 
            from_=1, 
            to=1, 
            orient=tk.HORIZONTAL, 
            command=self.update_image_from_navigation_slider_onChange
            )
        self.navigation_slider.grid(row=4, column=1, columnspan=3, padx=5, pady=5, sticky="ew")

        # Navigation buttons
        self.prev_button = tk.Button(self.preprocessing_tab, text="Prev", command=self.navigate_prev_onClick)
        self.prev_button.grid(row=4, column=0, padx=5, pady=5)
        self.next_button = tk.Button(self.preprocessing_tab, text="Next", command=self.navigate_next_onClick)
        self.next_button.grid(row=4, column=4, padx=5, pady=5)
        
    def create_scaling_ui(self):
        # Scale factor label and slider
        self.scale_factor_label = tk.Label(self.preprocessing_tab, text="Scale Factor:")
        self.scale_factor_label.grid(row=3, column=1, padx=5, pady=5, sticky="e")
        self.scale_factor_var = tk.DoubleVar()
        self.scale_factor_var.set(1.0)  # Default scale factor
        self.scale_factor_slider = tk.Scale(
            self.preprocessing_tab, 
            from_=0.1, 
            to=10.0, 
            resolution=0.1, 
            orient=tk.HORIZONTAL, 
            variable=self.scale_factor_var, 
            length=200
            )
        self.scale_factor_slider.grid(row=3, column=2, padx=5, pady=5, sticky="ew")
        
        # Bind event for slider changes
        self.scale_factor_slider.bind("<ButtonRelease-1>", self.update_image_on_rescale_slider_change)
        
    def create_canvas_ui(self):
        self.data_canvas_detection = tk.Canvas(self.preprocessing_tab, bg="white")
        self.data_canvas_detection.grid(row=1, column=2, padx=5, pady=5, sticky="nsew")
        self.vertical_scrollbar_detection = tk.Scrollbar(
            self.preprocessing_tab, 
            orient=tk.VERTICAL, 
            command=self.data_canvas_detection.yview
            )
        self.vertical_scrollbar_detection.grid(row=1, column=3, sticky="ns")
        self.data_canvas_detection.configure(yscrollcommand=self.vertical_scrollbar_detection.set)
        self.horizontal_scrollbar_detection = tk.Scrollbar(
            self.preprocessing_tab, 
            orient=tk.HORIZONTAL, 
            command=self.data_canvas_detection.xview
            )
        self.horizontal_scrollbar_detection.grid(row=2, column=2, sticky="ew")
        self.data_canvas_detection.configure(xscrollcommand=self.horizontal_scrollbar_detection.set)
        
        # Bind event for canvas resizing
        self.data_canvas_detection.bind("<Configure>", self.resize_canvas_detection_scrollregion)

    def update_image_from_navigation_slider_onChange(self):
        pass

    def navigate_prev_onClick(self):
        pass

    def navigate_next_onClick(self):
        pass

    def update_image_on_rescale_slider_change(self):
        pass

    def resize_canvas_detection_scrollregion(self, event):
        pass

    def display_header_info_labels(self):
        try:
            # Clear previous header
            for widget in self.header_section_frame.winfo_children():
                widget.destroy()
            # Header info labels
            header_labels = []

            selected_index = self.data_listbox_detection.curselection()
            if selected_index:
                index = int(selected_index[0])
                file_ext = get_file_extension()
                header_labels = self.create_data_for_header_labels_based_on_file_ext(index, file_ext)
                # Create labels and grid them
                self.create_header_labels(header_labels)
        except Exception as e:
            # Handle any unexpected errors and log them
            error_msg = f"Error displaying header information labels: {e}"
            logger.error(error_msg)

    def display_detection_section_menu(self):
        """
        Display the dropdown menu for selecting preprocess and detection options.

        This method creates and places a dropdown menu for selecting preprocess and detection options,
        such as "Preprocess" and "Detection".

        Raises:
            ValueError: If an error occurs while creating the dropdown menu.

        """
        
        try:
            self.display_preprocess_options_menu()

            # Listbox to show all operations
            self.operations_listbox = tk.Listbox(self.preprocess_section_menu)
            self.operations_listbox.grid(row=0, column=1,rowspan=5, padx=5, pady=5, sticky="nsew")

            self.operations_listbox.bind("<<ListboxSelect>>", self.show_operations_image_listboxOnSelect)

            # Add scrollbar to the listbox
            self.operations_scrollbar = tk.Scrollbar(self.preprocess_section_menu, orient="vertical", command=self.operations_listbox.yview)
            self.operations_scrollbar.grid(row=0, column=2, rowspan=5, padx=5, pady=5, sticky="ns")
            self.operations_listbox.config(yscrollcommand=self.operations_scrollbar.set)
        except Exception as e:
            error_msg = f"Error occurred while creating the detection section menu: {e}"
            logger.error(error_msg)
            raise ValueError(error_msg)
    
    def display_preprocess_options_menu(self):
        try:
            # Preprocess Dropdown menu options
            preprocessing_options = list(self.preprocess_params.keys())

            # Create and place dropdown menu
            choose_preprocess_option_dropdown_var = tk.StringVar()
            choose_preprocess_option_dropdown_var.set("")  # Set default option
            choose_preprocess_option_dropdown = tk.OptionMenu(
                self.preprocess_section_menu, 
                choose_preprocess_option_dropdown_var, 
                *preprocessing_options, 
                command=self.choose_preprocess_options_dropdownOnChange
                )
            choose_preprocess_option_dropdown.config(width=10)
            choose_preprocess_option_dropdown.grid(row=1, column=0, padx=5, pady=1, sticky="n")

            # Labels for function parameters
            self.parameter_preprocess_entries = {}
            self.parameter_preprocess_labels = {}
            self.parameter_preprocess_buttons = []
        except Exception as e:
            error_msg = f"Error displaying preprocess options menu: {e}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
    def choose_preprocess_options_dropdownOnChange(self, selected_option):
        """
        Handle the event when an option is selected from the preprocess options dropdown menu.

        This method updates the parameter labels and entries based on the selected preprocessing option.

        Args:
            selected_option (str): The selected preprocessing option from the dropdown menu.
        """
        self.selected_preprocess_option = selected_option
        for widget in [*self.parameter_preprocess_entries.values(), *self.parameter_preprocess_labels.values(),
                       *self.parameter_preprocess_buttons]:
            widget.destroy()
        self.parameter_preprocess_entries.clear()
        self.parameter_preprocess_labels.clear()
        self.parameter_preprocess_buttons.clear()
        # # Update labels with function parameters based on selected option
        row = 3
        for param_name, param_value in self.preprocess_params[selected_option].items():
            self.create_preprocess_menu_items(row, param_name, param_value)
            row += 2
        # Apply button
        apply_button = tk.Button(self.preprocess_section_menu, text="Apply", command=self.apply_preprocessing_onClick)
        apply_button.grid(row=row, column=0, padx=5, pady=5)
        self.parameter_preprocess_buttons.append(apply_button)

    def create_preprocess_menu_items(self, row, param_name, param_value):
        """
        Create GUI elements for displaying a preprocessing parameter.

        This method creates a label and an entry field for a preprocessing parameter.

        Args:
            row (int): The row index where the GUI elements should be placed.
            param_name (str): The name of the preprocessing parameter.
            param_value: The value of the preprocessing parameter.
        """
        label = tk.Label(self.preprocess_section_menu, text=param_name, width=15)
        label.grid(row=row, column=0, padx=5, pady=1, sticky="w")
        entry = tk.Entry(self.preprocess_section_menu)
        entry.grid(row=row + 1, column=0, padx=5, pady=1, sticky="w")
        entry.insert(0, str(param_value))
        self.parameter_preprocess_entries[param_name] = entry
        self.parameter_preprocess_labels[param_name] = label

    def apply_preprocessing_onClick(self):
        pass

    def show_operations_image_listboxOnSelect(self):
        pass


    def create_data_for_header_labels_based_on_file_ext(self, index, file_ext):
        try:
            header_labels_generator = {
                "s94": self.get_header_labels_from_s94_file,
                "stp": self.get_header_labels_from_stp_file,
                "mpp": self.get_header_labels_from_mpp_file
            }

            header_labels_func = header_labels_generator.get(file_ext.lower())
            if header_labels_func:
                return header_labels_func(index)
            else:
                raise KeyError(f"Header information for file extension '{file_ext}' is missing.")
        except KeyError as e:
            error_msg = f"Error occurred: {e}"
            logger.error(error_msg)
            raise

    def get_header_labels_from_stp_file(self, index):
        """
        Retrieve header labels for an STP file based on the index.

        Args:
            index (int): Index of the data.

        Returns:
            list: List of header labels for the STP file.

        Notes:
            - Retrieves header information using helper functions `get_header_info_at_index` and `get_filename_at_index`.
            - Constructs a list of formatted strings with relevant header information.
        """
        header_info = get_header_info_at_index(index)
        filename = get_filename_at_index(index)
        stp_labels = get_stp_labels(header_info, filename)
        return stp_labels
    
    def get_header_labels_from_s94_file(self, index):
        """
        Retrieve header labels for an S94 file based on the index.

        Args:
            index (int): Index of the data.

        Returns:
            list: List of header labels for the S94 file.

        Notes:
            - Retrieves header information using helper functions `get_header_info_at_index` and `get_filename_at_index`.
            - Constructs a list of formatted strings with relevant header information.
        """
        header_info = get_header_info_at_index(index)
        filename = get_filename_at_index(index)
        s94_labels = get_s94_labels(header_info, filename)
        return s94_labels

    def get_header_labels_from_mpp_file(self, index):
        """
        Retrieve header labels for an MPP file based on the index.

        Args:
            index (int): Index of the data.

        Returns:
            list: List of header labels for the MPP file.

        Notes:
            - Retrieves header information using helper functions `get_header_info_at_index`, `get_filename_at_index`, and `get_framenumber_at_index`.
            - Constructs a list of formatted strings with relevant header information.
        """
        header_info = get_header_info_at_index(index)
        filename = get_filename_at_index(index)
        framenumber = get_framenumber_at_index(index)
        mpp_labels = get_mpp_labels(header_info, filename, framenumber)
        return mpp_labels
    
    def create_header_labels(self, header_labels):

        try:
            num_labels_per_row = (len(header_labels) + 2) // 3  # Distribute labels into three rows
            for i, label_text in enumerate(header_labels):
                row = i // num_labels_per_row
                column = i % num_labels_per_row
                label = tk.Label(self.header_section_frame, text=label_text)
                label.grid(row=row, column=column, padx=5, pady=2, sticky="e")
        except Exception as e:
            # Handle any unexpected errors and log them
            error_msg = f"Error creating header labels: {e}"
            logger.error(error_msg)