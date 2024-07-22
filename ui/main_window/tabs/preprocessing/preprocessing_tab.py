# -*- coding: utf-8 -*-
"""
Module for preprocessing in the application.

@author
rlewandkow
"""

import os, sys

sys.path.insert(1, "/".join(os.path.realpath(__file__).split("/")[0:-2]))

import tkinter as tk
import numpy as np
from tkinter import ttk
from PIL import Image, ImageTk

from ui.main_window.tabs.detection.preprocess_operations import create_preprocess_operation

from ui.main_window.tabs.preprocessing.preprocessing_data import (
    data_for_preprocessing,
    insert_data,
    clear_preprocessing_data
)

from ui.main_window.tabs.tabs_data import (
    get_filename_at_index,
    get_all_operations,
    get_file_extension,
    get_framenumber_at_index,
    get_greyscale_image_at_index,
    get_header_info_at_index,
    get_mpp_labels,
    get_preprocessed_image_data_at_index,
    get_s94_labels,
    get_stp_labels,
    insert_operation_at_index
)

from data.processing.img_process import (
    concatenate_two_images
)

from ui.main_window.tabs.canvas_operations import (
    scale_factor_resize_image
)

from ui.main_window.tabs.preprocessing.preprocess_params_default import preprocess_params
from ui.main_window.tabs.preprocessing.options_config import (
    options_config, preprocess_operations
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

        self.current_data_index = 0

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
        self.data_listbox_preprocessing = tk.Listbox(
            self.preprocessing_tab, 
            width=20, 
            height=10, 
            selectmode=tk.SINGLE
            )
        self.data_listbox_preprocessing.grid(row=1, column=0, rowspan=2, padx=5, pady=5, sticky="nsew")
        self.listbox_scrollbar_preprocessing = tk.Scrollbar(
            self.preprocessing_tab, 
            orient=tk.VERTICAL, 
            command=self.data_listbox_preprocessing.yview
            )
        self.listbox_scrollbar_preprocessing.grid(row=1, column=1, rowspan=2, sticky="ns")
        self.data_listbox_preprocessing.config(yscrollcommand=self.listbox_scrollbar_preprocessing.set)
        self.data_listbox_preprocessing.bind("<<ListboxSelect>>", self.show_data_onDataListboxSelect)

        self.save_data_button = tk.Button(
            self.preprocessing_tab, 
            text="Save Data", 
            command=self.save_data_onClick
        )
        self.save_data_button.grid(row=3, column=0, padx=5, pady=5)
    
    def save_data_onClick(self):
        self.app.update_data(data_for_preprocessing)

    def load_data_onClick(self):
        try:
            # self.data_for_detection = self.app.get_data()
            self.insert_formated_data_to_process()
        except Exception as e:
            error_msg = f"Error loading data for spots detection: {e}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
    def insert_formated_data_to_process(self):
        clear_preprocessing_data()
        self.data_listbox_preprocessing.delete(0, tk.END)

        data = self.app.get_data()
        file_ext = data[0]['file_name'][-3:]
        for item in data:
            data_name = insert_data(file_ext, item)
            self.data_listbox_preprocessing.insert(tk.END, *data_name)
        self.update_navigation_slider_range()

    def show_data_onDataListboxSelect(self, event):
        # Get the index of the selected filename
        selected_index = self.data_listbox_preprocessing.curselection()
        if selected_index:
            index = int(selected_index[0])
            self.current_data_index = index
            # Update navigation slider
            self.navigation_slider.set(index + 1)
            self.display_image(index)
            self.refresh_data_in_operations_listbox()
    
    def display_image(self, index):
        # Clear previous data
        self.data_canvas_preprocessing.delete("all")
        self.display_header_info_labels()

        # Load greyscale image
        img = get_greyscale_image_at_index(data_for_preprocessing, index)
        self.handle_displaying_image_on_canvas(img)

    def refresh_data_in_operations_listbox(self):
        self.operations_listbox.delete(0, tk.END)
        index = self.current_data_index      
        operations = get_all_operations(data_for_preprocessing, index)
        self.operations_listbox.insert(tk.END, *operations)

    def handle_displaying_image_on_canvas(self, img):
        # Retrieve the scale factor
        scale_factor = self.scale_factor_var.get()
        # Resize the image
        img = scale_factor_resize_image(img, scale_factor)

        # Convert the PIL image to a Tkinter PhotoImage
        photo = ImageTk.PhotoImage(img)

        # Display the image on the canvas
        self.data_canvas_preprocessing.create_image(0, 0, anchor="nw", image=photo)

        # Save a reference to the PhotoImage to prevent garbage collection
        self.data_canvas_preprocessing.image = photo

    def update_navigation_slider_range(self):
        num_items = len(self.data_listbox_preprocessing.get(0, tk.END))
        self.navigation_slider.config(from_=1, to=num_items)

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
        self.data_canvas_preprocessing = tk.Canvas(self.preprocessing_tab, bg="white")
        self.data_canvas_preprocessing.grid(row=1, column=2, padx=5, pady=5, sticky="nsew")
        self.vertical_scrollbar_preprocessing = tk.Scrollbar(
            self.preprocessing_tab, 
            orient=tk.VERTICAL, 
            command=self.data_canvas_preprocessing.yview
            )
        self.vertical_scrollbar_preprocessing.grid(row=1, column=3, sticky="ns")
        self.data_canvas_preprocessing.configure(yscrollcommand=self.vertical_scrollbar_preprocessing.set)
        self.horizontal_scrollbar_preprocessing = tk.Scrollbar(
            self.preprocessing_tab, 
            orient=tk.HORIZONTAL, 
            command=self.data_canvas_preprocessing.xview
            )
        self.horizontal_scrollbar_preprocessing.grid(row=2, column=2, sticky="ew")
        self.data_canvas_preprocessing.configure(xscrollcommand=self.horizontal_scrollbar_preprocessing.set)
        
        # Bind event for canvas resizing
        self.data_canvas_preprocessing.bind("<Configure>", self.resize_canvas_detection_scrollregion)

    def update_image_from_navigation_slider_onChange(self, event):
        selected_index = self.data_listbox_preprocessing.curselection()
        if selected_index:
            try:
                index = int(self.navigation_slider.get())
            except ValueError:
                logger.error("Invalid slider value")
                return
            if index <= 0:
                logger.error("Slider value out of range")
                return
            self.display_image(index - 1)

            # Update listbox selection
            self.data_listbox_preprocessing.selection_clear(0, tk.END)
            self.data_listbox_preprocessing.selection_set(index - 1)
            self.data_listbox_preprocessing.see(index - 1)

            self.refresh_data_in_operations_listbox()
        self.resize_canvas_detection_scrollregion()

    def navigate_prev_onClick(self):
        try:
            current_value = self.navigation_slider.get()
            if current_value > 0:
                self.navigation_slider.set(current_value - 1)
        except ValueError:
            error_msg = "Invalid current value for navigation slider"
            logger.error(error_msg)
            raise ValueError(error_msg)

    def navigate_next_onClick(self):
        try:
            current_value = self.navigation_slider.get()
            self.navigation_slider.set(current_value + 1)
        except ValueError:
            error_msg = "Invalid current value for navigation slider"
            logger.error(error_msg)
            raise ValueError(error_msg)

    def update_image_on_rescale_slider_change(self, event=None):
        selected_index = self.data_listbox_preprocessing.curselection()
        if selected_index:
            index = int(selected_index[0])
            self.display_image(index)
        selected_index = self.operations_listbox.curselection()
        if selected_index:
            opertation_index = int(selected_index[0])
            self.display_processed_image(opertation_index)
        self.resize_canvas_detection_scrollregion()

    def display_processed_image(self, operation_index):

        # Clear previous data
        try:
            self.data_canvas_preprocessing.delete("all")
            img = None
            index = self.current_data_index
            img_data = get_preprocessed_image_data_at_index(data_for_preprocessing, index, operation_index)
            processed_img = Image.fromarray(img_data)
            original_img = get_greyscale_image_at_index(data_for_preprocessing, index)
            # Concatenate the images horizontally
            img = concatenate_two_images(processed_img, original_img)
            self.handle_displaying_image_on_canvas(img)
        except Exception as e:
            # Handle any unexpected errors and log them
            error_msg = f"Error displaying processed image: {e}"
            logger.error(error_msg)

    def resize_canvas_detection_scrollregion(self, event=None):
        self.data_canvas_preprocessing.config(scrollregion=self.data_canvas_preprocessing.bbox("all"))

    def display_header_info_labels(self):
        try:
            # Clear previous header
            for widget in self.header_section_frame.winfo_children():
                widget.destroy()
            # Header info labels
            header_labels = []

            selected_index = self.data_listbox_preprocessing.curselection()
            if selected_index:
                index = int(selected_index[0])
                file_ext = get_file_extension(data_for_preprocessing)
                header_labels = self.create_data_for_header_labels_based_on_file_ext(index, file_ext)
                # Create labels and grid them
                self.create_header_labels(header_labels)
        except Exception as e:
            # Handle any unexpected errors and log them
            error_msg = f"Error displaying header information labels: {e}"
            logger.error(error_msg)

    def display_detection_section_menu(self):
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
            choose_preprocess_option_dropdown.config(width=20)
            choose_preprocess_option_dropdown.grid(row=1, column=0, padx=5, pady=1, sticky="n")

            # Labels for function parameters
            self.parameter_preprocess_entries = {}
            self.parameter_preprocess_labels = {}
            self.parameter_preprocess_buttons = []
            self.parameter_preprocess_sliders = []
            self.parameter_preprocess_radio = []
            self.parameter_preprocess_dropdown = []
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
        for widget in [*self.parameter_preprocess_entries.values(),
                    *self.parameter_preprocess_labels.values(),
                    *self.parameter_preprocess_buttons,
                    *self.parameter_preprocess_sliders,
                    *self.parameter_preprocess_radio,
                    *self.parameter_preprocess_dropdown]:
            widget.destroy()
    
        # Clear the collections
        self.parameter_preprocess_entries.clear()
        self.parameter_preprocess_labels.clear()
        self.parameter_preprocess_buttons.clear()
        self.parameter_preprocess_sliders.clear()
        self.parameter_preprocess_radio.clear()
        self.parameter_preprocess_dropdown.clear()

        # options_config

        config = options_config.get(selected_option, {})
        row = 2 # Initialize row for layout

        # Handle radio buttons
        if "radio_buttons" in config:
            self.selected_option_var = tk.StringVar()
            self.selected_option_var.set(config["radio_buttons"][0][1])  # Set default value
            
            for text, value in config["radio_buttons"]:
                radio = tk.Radiobutton(self.preprocess_section_menu, text=text, variable=self.selected_option_var, value=value, command=self.process_and_display_image)
                radio.grid(row=row, column=0, padx=5, pady=1, sticky="w")
                self.parameter_preprocess_radio.append(radio)
                row += 1

        # Handle labels and sliders
        if "labels" in config:
            for label_text, default_value in config["labels"]:
                label = tk.Label(self.preprocess_section_menu, text=label_text, width=20)
                label.grid(row=row, column=0, padx=5, pady=1, sticky="w")
                self.parameter_preprocess_labels[label_text] = label
                
                slider_config = next((item for item in config.get("sliders", []) if item.get("value") == default_value), {})
                if slider_config:
                    slider = tk.Scale(self.preprocess_section_menu, from_=slider_config.get("from_", 0), to=slider_config.get("to", 100), resolution=slider_config.get("resolution", 1), orient=tk.HORIZONTAL, command=self.update_sliders_onChange, length=150)
                    slider.set(default_value)
                    slider.grid(row=row + 1, column=0, padx=5, pady=2, sticky="w")
                    self.parameter_preprocess_sliders.append(slider)
                
                row += 2

        # Handle single slider configurations
        if "slider_config" in config:
            label_text = config["label_text"]
            default_value = config["slider_config"].get("value")
            label = tk.Label(self.preprocess_section_menu, text=label_text, width=20)
            label.grid(row=row, column=0, padx=5, pady=1, sticky="w")
            self.parameter_preprocess_labels[label_text] = label
            
            slider = tk.Scale(self.preprocess_section_menu, from_=config["slider_config"].get("from_", 0), to=config["slider_config"].get("to", 100), resolution=config["slider_config"].get("resolution", 1), orient=tk.HORIZONTAL, command=self.update_sliders_onChange, length=150)
            slider.set(default_value)
            slider.grid(row=row + 1, column=0, padx=5, pady=2, sticky="w")
            self.parameter_preprocess_sliders.append(slider)
            
            row += 2

        # Apply button
        self.setup_common_widgets(row)
    
    def setup_common_widgets(self, row):
        """Set up common widgets, such as the Apply button."""
        apply_button = tk.Button(self.preprocess_section_menu, text="Apply", command=self.apply_preprocessing_onClick)
        apply_button.grid(row=row + 2, column=0, padx=5, pady=5)
        self.parameter_preprocess_buttons.append(apply_button)

    def create_preprocess_menu_items(self, row, param_name, param_value):
        label = tk.Label(self.preprocess_section_menu, text=param_name, width=15)
        label.grid(row=row, column=0, padx=5, pady=1, sticky="w")
        entry = tk.Entry(self.preprocess_section_menu)
        entry.grid(row=row + 1, column=0, padx=5, pady=1, sticky="w")
        entry.insert(0, str(param_value))
        self.parameter_preprocess_entries[param_name] = entry
        self.parameter_preprocess_labels[param_name] = label

    def apply_preprocessing_onClick(self):
        if self.selected_preprocess_option is None:
            return  # No option selected
        params = {}
        index = self.current_data_index
        focuse_widget = self.root.focus_get()
        img = self.get_image_based_on_selected_file_in_listbox(index, focuse_widget)

        result_image = None
        process_name = None

        self.get_values_from_preprocess_menu_items(params)
        # Apply preprocessing based on selected option and parameters
        result_image, process_name = self.apply_preprocessing_operation(params, img)
        operation = create_preprocess_operation(result_image, process_name, params)

        insert_operation_at_index(data_for_preprocessing, index, operation)

        # Refresh data and display processed image
        self.refresh_data_in_operations_listbox()
        operations_index = self.operations_listbox.size() - 1
        self.display_processed_image(operations_index)

        # Set focus and selection on operations listbox
        self.operations_listbox.focus()
        self.operations_listbox.selection_set(tk.END)

    def apply_preprocessing_operation(self, params, img):

        if self.selected_preprocess_option in preprocess_operations:
            process_function = preprocess_operations[self.selected_preprocess_option]
            process_name, result_image = process_function(params, img)
        else:
            msg = f"Invalid preprocessing option: {self.selected_preprocess_option}"
            logger.error(msg)
            raise ValueError(msg)
            
        return result_image, process_name
    
    def get_values_from_preprocess_menu_items(self, params):
        option = self.selected_preprocess_option

        def add_odd_value(slider):
            value = slider.get()
            return value + 1 if value % 2 == 0 else value


        preprocess_map = {
            "GaussianFilter": lambda: params.update({'sigma': self.parameter_preprocess_sliders[0].get()}),
            "Gamma Adjustment": lambda: params.update({'gamma': self.parameter_preprocess_sliders[0].get()}),
            "Adaptive Equalization": lambda: params.update({'limit': self.parameter_preprocess_sliders[0].get()}),
            "Contrast Stretching": lambda: params.update({
                'min': self.parameter_preprocess_sliders[0].get(),
                'max': self.parameter_preprocess_sliders[1].get()
            }),
            "Non-local Mean Denoising": lambda: params.update({
                'h': self.parameter_preprocess_sliders[0].get(),
                'templateWindowSize': self.parameter_preprocess_sliders[1].get(),
                'searchWindowSize': add_odd_value(self.parameter_preprocess_sliders[2])
            }),
            "Erosion": lambda: params.update({
                'kernel_type': self.selected_option_var.get(),
                'iterations': self.parameter_preprocess_sliders[1].get(),
                'kernel_size': add_odd_value(self.parameter_preprocess_sliders[0])
            }),
            "Propagation": lambda: params.update({
                'type': self.selected_option_var.get(),
                'marker_value': self.parameter_preprocess_sliders[0].get(),
            }),
            "Polynomial Leveling": lambda: params.update({
                'order': self.parameter_preprocess_sliders[0].get(),
            }),
            "Adaptive Leveling": lambda: params.update({
                'disk_size': self.parameter_preprocess_sliders[0].get(),
            }),
            "Local Median Filter": lambda: params.update({
                'size': self.parameter_preprocess_sliders[0].get(),
            }),
            "Binary Greyscale Erosion": lambda: params.update({
                'kernel_type': self.selected_option_var.get(),
                'kernel_size': add_odd_value(self.parameter_preprocess_sliders[0])
            }),
            "Gaussian Greyscale Erosion": lambda: params.update({
                'mask_size': add_odd_value(self.parameter_preprocess_sliders[0]),
                'sigma': self.parameter_preprocess_sliders[1].get()
            }),
            "Binary Greyscale Dilation": lambda: params.update({
                'kernel_type': self.selected_option_var.get(),
                'kernel_size': add_odd_value(self.parameter_preprocess_sliders[0])
            }),
            "Gaussian Greyscale Dilation": lambda: params.update({
                'mask_size': add_odd_value(self.parameter_preprocess_sliders[0]),
                'sigma': self.parameter_preprocess_sliders[1].get()
            }),
            "Binary Greyscale Opening": lambda: params.update({
                'kernel_type': self.selected_option_var.get(),
                'kernel_size': add_odd_value(self.parameter_preprocess_sliders[0])
            }),
            "Gaussian Greyscale Opening": lambda: params.update({
                'mask_size': add_odd_value(self.parameter_preprocess_sliders[0]),
                'sigma': self.parameter_preprocess_sliders[1].get()
            }),
            "Binary Greyscale Closing": lambda: params.update({
                'kernel_type': self.selected_option_var.get(),
                'kernel_size': add_odd_value(self.parameter_preprocess_sliders[0])
            }),
            "White Top Hat": lambda: params.update({
                'selem_type': self.selected_option_var.get(),
                'selem_size': self.parameter_preprocess_sliders[0].get()
            }),
            "Black Top Hat": lambda: params.update({
                'selem_type': self.selected_option_var.get(),
                'selem_size': self.parameter_preprocess_sliders[0].get()
            }),
            "Gaussian Greyscale Closing": lambda: params.update({
                'mask_size': add_odd_value(self.parameter_preprocess_sliders[0]),
                'sigma': self.parameter_preprocess_sliders[1].get()
            }),
            "Gaussian Sharpening": lambda: params.update({
                'radius': self.parameter_preprocess_sliders[0].get(),
                'amount': self.parameter_preprocess_sliders[1].get()
            })
        }

        # Apply the corresponding function based on the selected preprocess option
        if option in preprocess_map:
            preprocess_map[option]()

        # Handle any additional parameters from preprocess menu items
        for param_name, entry in self.parameter_preprocess_entries.items():
            try:
                params[param_name] = int(entry.get())
            except ValueError:
                params[param_name] = entry.get()

    def get_image_based_on_selected_file_in_listbox(self, index, focuse_widget):
        img = None
        if focuse_widget == self.data_listbox_preprocessing:
            img = get_greyscale_image_at_index(data_for_preprocessing, index)
        elif focuse_widget == self.operations_listbox:
            operations_selected_index = self.operations_listbox.curselection()
            operations_index = int(operations_selected_index[0])
            img = Image.fromarray(get_preprocessed_image_data_at_index(data_for_preprocessing, index, operations_index))
        return img

    def show_operations_image_listboxOnSelect(self, event=None):
        try:
            operations_selected_index = self.operations_listbox.curselection()
            operations_index = int(operations_selected_index[0])

            self.display_processed_image(operations_index)
        except IndexError:
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
        header_info = get_header_info_at_index(data_for_preprocessing, index)
        filename = get_filename_at_index(data_for_preprocessing, index)
        stp_labels = get_stp_labels(header_info, filename)
        return stp_labels
    
    def get_header_labels_from_s94_file(self, index):
        header_info = get_header_info_at_index(data_for_preprocessing, index)
        filename = get_filename_at_index(data_for_preprocessing, index)
        s94_labels = get_s94_labels(header_info, filename)
        return s94_labels

    def get_header_labels_from_mpp_file(self, index):
        header_info = get_header_info_at_index(data_for_preprocessing, index)
        filename = get_filename_at_index(data_for_preprocessing, index)
        framenumber = get_framenumber_at_index(data_for_preprocessing, index)
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

    def update_sliders_onChange(self, event=None):
        self.process_and_display_image()
    
    def dropdown_onChange(self, event=None):
        self.process_and_display_image()

    def process_and_display_image(self):
        params = {}
        index = self.current_data_index
        focuse_widget = self.root.focus_get()
        img = self.get_image_based_on_selected_file_in_listbox(index, focuse_widget)

        original_img = get_greyscale_image_at_index(data_for_preprocessing, index)

        self.get_values_from_preprocess_menu_items(params)
        result_image, _ = self.apply_preprocessing_operation(params, img)
        if isinstance(result_image, np.ndarray):
            result_image = Image.fromarray(result_image)
        img = concatenate_two_images(result_image, original_img)
        self.handle_displaying_image_on_canvas(img)