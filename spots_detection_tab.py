# -*- coding: utf-8 -*-
"""
Module for spots detection in the application.

@author
rlewandkow
"""

import os
import cv2

import tkinter as tk
from tkinter import ttk, messagebox

from PIL import Image, ImageTk

import numpy as np

from data_process import create_greyscale_image

from img_process import NlMeansDenois, GaussianBlur, GaussianFilter, EdgeDetection, concatenate_two_images
from img_process import ContourFinder, ContourFilter, DrawContours, concatenate_four_images
from img_process import GetContourData, DrawLabels, get_mouse_position_in_canvas
from img_process import get_contour_info_at_position

from file_process import calculate_avg_nm_per_px, calculate_pixel_to_nm_coefficients

import logging

logger = logging.getLogger(__name__)

class SpotsDetectionTab:
    """Class representing the tab for spots detection in the application."""

    def __init__(self, notebook, app):
        """
        Initialize the SpotsDetectionTab instance.

        Args:
            notebook (ttk.Notebook): The notebook to which the tab will be added.
            app: The application instance.

        Attributes:
            spots_detection_tab (ttk.Frame): The frame representing the spots detection tab.
            app: The application instance.
            root: The root Tkinter instance.
            data_for_detection (list): List of data for spots detection.
            header_info (dict): Header information for the data.
            preprocess_params (dict): Parameters for image preprocessing methods.
            detection_params (dict): Parameters for spot detection methods.
            selected_option: The selected detection option.
        """

        self.spots_detection_tab = ttk.Frame(notebook)
        notebook.add(self.spots_detection_tab, text="Detection")
        self.app = app
        self.root = app.root

        self.data_for_detection = []

        self.header_info = {}

        self.preprocess_params = {
            "GaussianBlur": {"sigmaX": 5, "sigmaY": 5},
            "Non-local Mean Denoising": {"h": 3, "searchWindowSize": 21, "templateWindowSize": 7},
            "GaussianFilter": {"sigma": 4}
        }

        self.current_size_x_coefficient = 0
        self.current_size_y_coefficient = 0
        self.current_area_coefficient = 0

        self.detection_params = {
            "Canny": {"sigma": 1.}
        }

        self.filter_params = {
            "Circularity": {"circularity_low": 0.1, "circularity_high": 0.9},
            "Area": {"min_area": 0.0, "max_area": 200}
        }

        self.current_operation = {
            "processed_image": None,
            "edge_image": None,
            "filtered_contours_img": None,
            "process_name": "",
            "contours": [],
            "contours_data": [],
            "labels": [],
            "labeled_image": None
        }

        self.selected_option = None

        self.create_spots_detection_tab()
    
    def load_data_onClick(self):
        """
        Load data for spots detection when the load data button is clicked.

        Raises:
            ValueError: If there is an issue loading the data.
        """
        try:
            # self.data_for_detection = self.app.get_data()
            self.insert_formated_data_to_process()
        except Exception as e:
            error_msg = f"Error loading data for spots detection: {e}"
            logger.error(error_msg)
            raise ValueError(error_msg)

    def create_spots_detection_tab(self):
        """
        Create the GUI components for the spots detection tab.

        This method initializes and lays out the widgets for the spots detection tab.

        Raises:
            ValueError: If there is an issue creating the GUI components.
        """
        try:
            # Data for analisys
            self.original_data_index = None

            # Button to load data
            self.load_data_button = tk.Button(
                self.spots_detection_tab, 
                text="Load Data", 
                command=self.load_data_onClick
                )
            self.load_data_button.grid(row=0, column=0, padx=5, pady=5)
            
            # Create listbox to display filenames
            self.data_listbox_detection = tk.Listbox(
                self.spots_detection_tab, 
                width=20, 
                height=10, 
                selectmode=tk.SINGLE
                )
            self.data_listbox_detection.grid(row=1, column=0, rowspan=2, padx=5, pady=5, sticky="nsew")
            self.listbox_scrollbar_detection = tk.Scrollbar(
                self.spots_detection_tab, 
                orient=tk.VERTICAL, 
                command=self.data_listbox_detection.yview
                )
            self.listbox_scrollbar_detection.grid(row=1, column=1, rowspan=2, sticky="ns")
            self.data_listbox_detection.config(yscrollcommand=self.listbox_scrollbar_detection.set)
            self.data_listbox_detection.bind("<<ListboxSelect>>", self.show_data_onDataListboxSelect)

            # Add a canvas to display the data
            # Add Motions and add action on hover
            self.data_canvas_detection = tk.Canvas(self.spots_detection_tab, bg="white")
            self.data_canvas_detection.grid(row=1, column=2, padx=5, pady=5, sticky="nsew")
            self.data_canvas_detection.bind("<Motion>", self.on_canvas_hover)
            self.vertical_scrollbar_detection = tk.Scrollbar(
                self.spots_detection_tab, 
                orient=tk.VERTICAL, 
                command=self.data_canvas_detection.yview
                )
            self.vertical_scrollbar_detection.grid(row=1, column=3, sticky="ns")
            self.data_canvas_detection.configure(yscrollcommand=self.vertical_scrollbar_detection.set)
            self.horizontal_scrollbar_detection = tk.Scrollbar(
                self.spots_detection_tab, 
                orient=tk.HORIZONTAL, 
                command=self.data_canvas_detection.xview
                )
            self.horizontal_scrollbar_detection.grid(row=2, column=2, sticky="ew")
            self.data_canvas_detection.configure(xscrollcommand=self.horizontal_scrollbar_detection.set)

            # Set row and column weights
            self.spots_detection_tab.grid_rowconfigure(1, weight=1)
            self.spots_detection_tab.grid_columnconfigure(2, weight=1)

            # Scale factor label and slider
            self.scale_factor_label = tk.Label(self.spots_detection_tab, text="Scale Factor:")
            self.scale_factor_label.grid(row=3, column=1, padx=5, pady=5, sticky="e")
            self.scale_factor_var = tk.DoubleVar()
            self.scale_factor_var.set(1.0)  # Default scale factor
            self.scale_factor_slider = tk.Scale(
                self.spots_detection_tab, 
                from_=0.1, 
                to=10.0, 
                resolution=0.1, 
                orient=tk.HORIZONTAL, 
                variable=self.scale_factor_var, 
                length=200
                )
            self.scale_factor_slider.grid(row=3, column=2, padx=5, pady=5, sticky="ew")

            # Slider for navigation
            self.navigation_slider = tk.Scale(
                self.spots_detection_tab, 
                from_=1, 
                to=1, 
                orient=tk.HORIZONTAL, 
                command=self.update_image_from_navigation_slider_onChange
                )
            self.navigation_slider.grid(row=4, column=1, columnspan=3, padx=5, pady=5, sticky="ew")

            # Navigation buttons
            self.prev_button = tk.Button(self.spots_detection_tab, text="Prev", command=self.navigate_prev_onClick)
            self.prev_button.grid(row=4, column=0, padx=5, pady=5)
            self.next_button = tk.Button(self.spots_detection_tab, text="Next", command=self.navigate_next_onClick)
            self.next_button.grid(row=4, column=4, padx=5, pady=5)

            # Bind event for canvas resizing
            self.data_canvas_detection.bind("<Configure>", self.resize_canvas_detection_scrollregion)

            # Bind event for slider changes
            self.scale_factor_slider.bind("<ButtonRelease-1>", self.update_image_on_rescale_slider_change)

            # Display header information labels
            self.header_section_frame = ttk.Frame(self.spots_detection_tab, padding="5")
            self.header_section_frame.grid(row=0, column=2, padx=5, pady=2, sticky="nsew")

            # Header section name label
            self.header_section_name_label = tk.Label(self.header_section_frame, text="Header Info:")
            self.header_section_name_label.grid(row=0, column=0, padx=5, pady=2, sticky="e")

            # Display Proccess Options
            self.detection_section_menu = ttk.Frame(self.spots_detection_tab, padding="3")
            self.detection_section_menu.grid(row=0, column=4,rowspan=2, columnspan=2, padx=5, pady=2, sticky="nsew")

            self.display_header_info_labels()
            self.display_detection_section_menu()
        except Exception as e:
            error_msg = f"Error creating spots detection tab: {e}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
    def on_canvas_hover(self, event):
        x, y = get_mouse_position_in_canvas(
            scale_factor= self.scale_factor_var.get(),
            x_canvas= self.data_canvas_detection.canvasx(event.x),
            y_canvas= self.data_canvas_detection.canvasy(event.y),
            event= event
        )

        # Check if the mouse is over a contour
        item = get_contour_info_at_position(
            current_operation= self.current_operation,
            x= x, 
            y= y
            )
        if item:
            # contour_name = item['name']
            self.update_contour_labels(
                name= item['name'],
                area= item['area'],
                distance= item['distance_to_nearest_neighbour']
            )

            self.update_nearest_neighbour_labe(item['nearest_neighbour'])
            
        else:
            pass

    def display_preprocess_options_menu(self):
        """
        Display the preprocess options menu.

        This method creates and places dropdown menus for selecting preprocessing options.

        Raises:
            ValueError: If there is an issue creating the preprocess options menu.
        """
        try:
            # Preprocess Dropdown menu options
            preprocessing_options = list(self.preprocess_params.keys())

            self.image_show_options = {
                "Preprocess": ["processed", "both", "original"]
            }

            # Create and place dropdown menu
            choose_preprocess_option_dropdown_var = tk.StringVar()
            choose_preprocess_option_dropdown_var.set("")  # Set default option
            choose_preprocess_option_dropdown = tk.OptionMenu(
                self.detection_section_menu, 
                choose_preprocess_option_dropdown_var, 
                *preprocessing_options, 
                command=self.choose_preprocess_options_dropdownOnChange
                )
            choose_preprocess_option_dropdown.config(width=10)
            choose_preprocess_option_dropdown.grid(row=1, column=0, padx=5, pady=1, sticky="n")

            # Create and place second dropdown menu
            self.choose_display_image_option_dropdown_var = tk.StringVar()
            self.choose_display_image_option_dropdown_var.set("")  # Set default option
            self.choose_display_image_option_dropdown = tk.OptionMenu(
                self.detection_section_menu, 
                self.choose_display_image_option_dropdown_var, 
                *self.image_show_options["Preprocess"], 
                command=self.choose_image_display_option_dropdownOnChange
                )
            self.choose_display_image_option_dropdown.config(width=10)
            self.choose_display_image_option_dropdown.grid(row=2, column=0, padx=5, pady=1, sticky="n")

            # Labels for function parameters
            self.parameter_preprocess_entries = {}
            self.parameter_preprocess_labels = {}
            self.parameter_preprocess_buttons = []
        except Exception as e:
            error_msg = f"Error displaying preprocess options menu: {e}"
            logger.error(error_msg)
            raise ValueError(error_msg)

    def display_detection_options_menu(self):
        """
        Display the dropdown menu for selecting detection options.

        This method creates and places a dropdown menu for selecting detection options,
        such as "Canny".

        Raises:
            ValueError: If an error occurs while creating the dropdown menu.

        """
        try:

            detection_options = list(self.detection_params.keys())

            # Create and place dropdown menu for detection options
            detection_dropdown_var = tk.StringVar()
            detection_dropdown_var.set("")  # Set default option
            detection_dropdown = tk.OptionMenu(
                self.detection_section_menu, 
                detection_dropdown_var, 
                *detection_options, 
                command=self.choose_spots_detection_options_dropdopwnOnChange
                )
            detection_dropdown.config(width=10)
            detection_dropdown.grid(row=1, column=0, padx=5, pady=1, sticky="n")

            # Labels for function parameters
            self.parameter_detection_entries = {}
            self.parameter_detection_labels = {}
            self.parameter_detection_sliders = {}
            self.parameter_detection_buttons = []
            self.parameter_filter_sliders = {}
            self.parameter_filter_labels = {}

        except Exception as e:
            error_msg = f"Error occurred while creating the detection dropdown menu: {e}"
            logger.error(error_msg)
            raise ValueError(error_msg)

    def display_detection_section_menu(self):
        """
        Display the dropdown menu for selecting preprocess and detection options.

        This method creates and places a dropdown menu for selecting preprocess and detection options,
        such as "Preprocess" and "Detection".

        Raises:
            ValueError: If an error occurs while creating the dropdown menu.

        """
        
        try:
            display_options = ["Preprocess", "Detection"]

            # Create and place dropdown menu for detection options
            self.doperation_menu_dropdown_var = tk.StringVar()
            self.doperation_menu_dropdown_var.set("Preprocess")  # Set default option
            self.operation_menu_dropdown = tk.OptionMenu(
                self.detection_section_menu, 
                self.doperation_menu_dropdown_var, 
                *display_options, 
                command=self.display_menu_dropdownOnChange
                )
            self.operation_menu_dropdown.config(width=10)
            self.operation_menu_dropdown.grid(row=0, column=0, padx=5, pady=1, sticky="n")

            self.display_preprocess_options_menu()

            # Listbox to show all operations
            self.operations_listbox = tk.Listbox(self.detection_section_menu)
            self.operations_listbox.grid(row=0, column=1,rowspan=5, padx=5, pady=5, sticky="nsew")

            self.operations_listbox.bind("<<ListboxSelect>>", self.show_operations_image_listboxOnSelect)

            # Add scrollbar to the listbox
            self.operations_scrollbar = tk.Scrollbar(self.detection_section_menu, orient="vertical", command=self.operations_listbox.yview)
            self.operations_scrollbar.grid(row=0, column=2, rowspan=5, padx=5, pady=5, sticky="ns")
            self.operations_listbox.config(yscrollcommand=self.operations_scrollbar.set)
        except Exception as e:
            error_msg = f"Error occurred while creating the detection section menu: {e}"
            logger.error(error_msg)
            raise ValueError(error_msg)

    def display_menu_dropdownOnChange(self, selected_option):
        """
        Update the display menu based on the selected dropdown menu option.

        This method destroys the existing widgets in the detection section menu
        and displays the appropriate options based on the selected option.

        Args:
            selected_option (str): The selected option from the dropdown menu.

        Raises:
            ValueError: If an error occurs while updating the display.

        """
        try:
            for widget in self.detection_section_menu.winfo_children():
                if not widget in (self.operations_listbox, self.operations_scrollbar, self.operation_menu_dropdown):
                    widget.destroy()
            
            if selected_option == "Preprocess":
                self.display_preprocess_options_menu()
            elif selected_option == "Detection":
                self.display_detection_options_menu()
        except Exception as e:
            error_msg = f"Error occurred while changing the dropdown menu option: {e}"
            logger.error(error_msg)
            raise ValueError(error_msg)

    def choose_spots_detection_options_dropdopwnOnChange(self, selected_option):
        """
        Update the display based on the selected detection option.

        This method dynamically updates the display by creating widgets for the selected detection option's parameters.
        It clears any existing widgets related to the previous selection.

        Args:
            selected_option (str): The selected detection option.

        Raises:
            ValueError: If the selected option is not found in the detection parameters dictionary.

        """
        try:
            self.selected_detection_option = selected_option
            # Destroy existing parameter labels and entries
            for widget in [*self.parameter_detection_entries.values(), *self.parameter_detection_labels.values(),
                        *self.parameter_detection_sliders.values(), *self.parameter_detection_buttons,
                        *self.parameter_filter_labels.values(), *self.parameter_filter_sliders.values()]:
                widget.destroy()
            self.parameter_detection_entries.clear()
            self.parameter_detection_labels.clear()
            self.parameter_detection_sliders.clear()
            self.parameter_detection_buttons.clear()
            self.parameter_filter_labels.clear()
            self.parameter_filter_sliders.clear()

            row = 3
            # Update labels with function parameters based on selected option
            for param_name, param_value in self.detection_params[selected_option].items():
                self.create_detection_menu_items(row, param_name, param_value)
                row += 2

            self.create_filter_menu_items(row)

            # Create a Text widget for multiline display
            self.contour_name_label = tk.Label(self.detection_section_menu, wraplength=200, justify=tk.LEFT)
            self.contour_name_label.grid(row=row + 10, column=0, sticky="w")
            self.contour_area_label = tk.Label(self.detection_section_menu, wraplength=200, justify=tk.LEFT)
            self.contour_area_label.grid(row=row + 11, column=0, sticky="w")
            self.contour_shortest_distance_label = tk.Label(self.detection_section_menu, wraplength=200, justify=tk.LEFT)
            self.contour_shortest_distance_label.grid(row=row + 10, column=1, sticky="w")
            self.nearest_neighbour_name_label = tk.Label(self.detection_section_menu, wraplength=200, justify=tk.LEFT)
            self.nearest_neighbour_name_label.grid(row=row + 11, column=1, sticky="w")
            self.avg_area_label = tk.Label(self.detection_section_menu, wraplength=200, justify=tk.LEFT)
            self.avg_area_label.grid(row=row + 12, column=0, columnspan=2)

            # Find Contours button
            filter_contours_button = tk.Button(self.detection_section_menu, text="Filter Contours", command=self.filter_contours_onClick)
            filter_contours_button.grid(row=row + 15, column=0, padx=5, pady=5)

        except KeyError:
            error_msg = f"Selected option '{selected_option}' not found in detection parameters."
            logger.error(error_msg)
            raise KeyError(error_msg)
        
    def update_nearest_neighbour_labe(self, text):
        self.nearest_neighbour_name_label.config(text=f"Nearest neighbour: {text}")
        
    def update_avg_area_label(self, contour_data):
        total_area = sum(contour['area'] for contour in contour_data)
        avg_area = 0
        if len(contour_data) > 0:
            avg_area = total_area / len(contour_data)
        self.avg_area_label.config(text=f"Average Area: {avg_area:.3f} nm2")

    def update_contour_labels(self, name, area, distance):
        # Update the text of each label
        self.contour_name_label.config(text=f"Name: {name}")
        self.contour_area_label.config(text=f"Area: {area:.3} nm2")
        self.contour_shortest_distance_label.config(text=f"Shortest distance: {distance:.3} nm")
        
    def create_filter_menu_items(self, row):
        for filter_type, params in self.filter_params.items():
            filter_frame = ttk.Label(self.detection_section_menu, text=filter_type + ":")
            filter_frame.grid(row=row, column=0, padx=10, pady=5, sticky="nsew")

            for param_name, param_value in params.items():
                label_text = f"{param_name.replace('_', ' ').capitalize()}: {param_value:.1f}"
                label = tk.Label(self.detection_section_menu, text=label_text)
                label.grid(row=row + 1, column=0, padx=5, pady=5)
                self.parameter_filter_labels[param_name] = label

                if param_name.startswith("min"):
                    slider = ttk.Scale(
                        self.detection_section_menu,
                        from_=0.0,
                        to=100,
                        orient="horizontal",
                        command=lambda value=param_value, param=param_name: self.filter_slider_on_change(param, value)
                    )
                elif param_name.startswith("max"):
                    slider = ttk.Scale(
                        self.detection_section_menu,
                        from_=50,
                        to=200,
                        orient="horizontal",
                        command=lambda value=param_value, param=param_name: self.filter_slider_on_change(param, value)
                    )
                else:
                    slider = ttk.Scale(
                        self.detection_section_menu,
                        from_=0.0,
                        to=1.0,
                        orient="horizontal",
                        command=lambda value=param_value, param=param_name: self.filter_slider_on_change(param, value)
                    )
                slider.set(param_value)
                slider.grid(row=row + 1, column=1, padx=5, pady=5)
                self.parameter_filter_sliders[param_name] = slider

                row += 1
            row += 1
        
        # Add checkboxes for draw contours and write labels
        draw_contours_var = tk.IntVar()
        draw_contours_checkbox = tk.Checkbutton(self.detection_section_menu, text="Draw Contours", variable=draw_contours_var, command=self.checkbox_status_changed)
        draw_contours_checkbox.grid(row=row, column=0, padx=5, pady=5, sticky="w")
        self.draw_contours_var = draw_contours_var

        write_labels_var = tk.IntVar()
        write_labels_checkbox = tk.Checkbutton(self.detection_section_menu, text="Write Labels", variable=write_labels_var, command=self.checkbox_status_changed)
        write_labels_checkbox.grid(row=row, column=1, padx=5, pady=5, sticky="w")
        self.write_labels_var = write_labels_var

        row += 1

        return row
    
    def checkbox_status_changed(self):
        self.refresh_image_after_filtering()
        
    def filter_contours_onClick(self):
        pass
        # operations_selected_index = self.operations_listbox.curselection()
        # operations_index = int(operations_selected_index[0])
        # key = "contours"
        # data = self.data_for_detection[self.original_data_index]['operations'][operations_index]
        # contours = []
        # if key in data:
        #     contours = data[key]
        # else:
        #     messagebox.showwarning("No data", "Select operation with detected edges")
        
    def get_values_from_filter_menu_items(self, params):
        for param_name, slider in self.parameter_filter_sliders.items():
            try:
                params[param_name] = float(slider.get())
            except ValueError:
                params[param_name] = slider.get()

    def create_detection_menu_items(self, row, param_name, param_value):
        """
        Create menu items based on parameter name and value.

        Parameters:
            row (int): The row index in the grid to place the menu items.
            param_name (str): The name of the parameter.
            param_value: The value of the parameter.

        Raises:
            ValueError: If param_value is invalid.

        Returns:
            None
        """
        if param_name == "sigma":
            # Create a slider for sigma parameter
            label_text = f"{param_name}: {param_value:.1f}"
            label = tk.Label(self.detection_section_menu, text=label_text, width=15)
            label.grid(row=row, column=0, padx=5, pady=1, sticky="w")
            slider = ttk.Scale(
                self.detection_section_menu, 
                from_=0.1, 
                to=5.0, 
                length=100, 
                orient="horizontal", 
                command=lambda value=param_value, param_name=param_name: self.sigma_slider_onChange(value, param_name))
            slider.set(param_value)  # Set default value
            slider.grid(row=row + 1, column=0, padx=5, pady=1, sticky="w")
            self.parameter_detection_sliders[param_name] = slider
            self.parameter_detection_labels[param_name] = label

    def get_values_from_detection_menu_items(self, params):
        """
        Retrieve values from entry fields and sliders in the detection menu.

        This method iterates over the entry fields and sliders in the detection menu,
        retrieves their current values, and adds them to the provided params dictionary.

        Args:
            params (dict): Dictionary to store parameter names and their values.

        Returns:
            None
        """
        for param_name, entry in self.parameter_detection_entries.items():
            try:
                params[param_name] = int(entry.get())
            except ValueError:
                params[param_name] = entry.get()
        
        for param_name, slider in self.parameter_detection_sliders.items():
            try:
                params[param_name] = float(slider.get())
            except ValueError:
                params[param_name] = slider.get()

    def get_image_based_on_selected_file_in_listbox(self, index, focuse_widget):
        """
        Get the appropriate image based on the selected file in the listbox.

        This method determines whether the listbox in focus is the data listbox or
        the operations listbox, and retrieves the corresponding image based on the
        selected index.

        Args:
            index (int): Index of the selected file in the data listbox.
            focuse_widget (tk.Widget): Widget currently in focus.

        Returns:
            Image: The selected image.
        """
        if focuse_widget == self.data_listbox_detection:
            img = self.data_for_detection[index]['greyscale_image']
        elif focuse_widget == self.operations_listbox:
            operations_selected_index = self.operations_listbox.curselection()
            operations_index = int(operations_selected_index[0])
            img = Image.fromarray(self.data_for_detection[self.original_data_index]['operations'][operations_index]['processed_image'])
        return img

    def handle_displaying_image_on_canvas(self, img):
        """
        Handle the display of the image on the canvas.

        This method resizes the image based on the scale factor, converts it to a Tkinter PhotoImage, and displays it on the canvas.

        Args:
            img (PIL.Image.Image): The image to be displayed on the canvas.
        """

        # Retrieve the scale factor
        scale_factor = self.scale_factor_var.get()
        # Resize the image
        img = img.resize((int(img.width * scale_factor), int(img.height * scale_factor)), Image.LANCZOS)

        # Convert the PIL image to a Tkinter PhotoImage
        photo = ImageTk.PhotoImage(img)

        # Display the image on the canvas
        self.data_canvas_detection.create_image(0, 0, anchor="nw", image=photo)

        # Save a reference to the PhotoImage to prevent garbage collection
        self.data_canvas_detection.image = photo

    def refresh_data_in_operations_listbox(self):
        """
        Refresh the operations listbox with the updated data.

        This method deletes all existing items in the operations listbox and inserts the names of the operations
        associated with the selected image.
        """
        self.operations_listbox.delete(0, tk.END)

        selected_index = self.original_data_index

        operations = [item["process_name"] for item in self.data_for_detection[selected_index]['operations']]
        self.operations_listbox.insert(tk.END, *operations)

    def choose_image_display_option_dropdownOnChange(self, selected_option):
        """
        Handle the event when an option is selected from the image display dropdown menu.

        This method retrieves the index of the selected operation from the operations listbox and then calls the 
        display_processed_image method with the appropriate parameters.

        Args:
            selected_option (str): The selected option from the dropdown menu.
        """
        operations_selected_index = self.operations_listbox.curselection()
        operations_index = int(operations_selected_index[0])
        self.display_processed_image(
            operation_index= operations_index,
            option_section= "Preprocess",
            option= selected_option
        )
    
    def choose_preprocess_options_dropdownOnChange(self, selected_option):
        """
        Handle the event when an option is selected from the preprocess options dropdown menu.

        This method updates the parameter labels and entries based on the selected preprocessing option.

        Args:
            selected_option (str): The selected preprocessing option from the dropdown menu.
        """
        self.selected_option = selected_option
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
        apply_button = tk.Button(self.detection_section_menu, text="Apply", command=self.apply_preprocessing_onClick)
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
        label = tk.Label(self.detection_section_menu, text=param_name, width=15)
        label.grid(row=row, column=0, padx=5, pady=1, sticky="w")
        entry = tk.Entry(self.detection_section_menu)
        entry.grid(row=row + 1, column=0, padx=5, pady=1, sticky="w")
        entry.insert(0, str(param_value))
        self.parameter_preprocess_entries[param_name] = entry
        self.parameter_preprocess_labels[param_name] = label

    def apply_preprocessing_onClick(self):
        """
        Apply preprocessing operation based on the selected option and parameters.
        """
        if self.selected_option is None:
            return  # No option selected
        params = {}
        index = self.original_data_index
        focuse_widget = self.root.focus_get()
        img = self.get_image_based_on_selected_file_in_listbox(index, focuse_widget)

        result_image = None
        process_name = None

        self.get_values_from_preprocess_menu_items(params)
        # Apply preprocessing based on selected option and parameters
        result_image, process_name = self.apply_preprocessing_operation(params, img)
        operation = {
            "processed_image": result_image,
            "process_name": process_name,
            "params": params
        }

        self.data_for_detection[index]['operations'].append(operation)

        # Refresh data and display processed image
        self.refresh_data_in_operations_listbox()
        operations_index = self.operations_listbox.size() - 1
        self.display_processed_image(operations_index, "Preprocess", "both")
        self.choose_display_image_option_dropdown_var.set("both")

        # Set focus and selection on operations listbox
        self.operations_listbox.focus()
        self.operations_listbox.selection_set(tk.END)

    def apply_preprocessing_operation(self, params, img):
        """
        Apply the selected preprocessing operation to the image based on the provided parameters.

        Args:
            params (dict): Dictionary containing parameter names and values for the selected preprocessing operation.
            img (PIL.Image.Image): Input image.

        Returns:
            tuple: A tuple containing the processed image and the name of the applied preprocessing operation.
        """
        if self.selected_option == "GaussianBlur":
            process_name = "GaussianBlur"
            result_image = GaussianBlur(
                img=np.array(img), 
                sigmaX=params['sigmaX'],
                sigmaY=params['sigmaY']
                )
        elif self.selected_option == "Non-local Mean Denoising":
            process_name = "Non-local Mean Denoising"
            result_image = NlMeansDenois(
                img=np.array(img),
                h=params['h'],
                searchWinwowSize=params['searchWindowSize'],
                templateWindowSize=params['templateWindowSize']
                )
        elif self.selected_option == "GaussianFilter":
            process_name = "GaussianFilter"
            result_image = GaussianFilter(
                img=np.array(img),
                sigma=params['sigma']
            )
        else:
            msg = f"Invalid preprocessing option: {self.selected_option}"
            logger.error(msg)
            raise ValueError(msg)
            
        return result_image,process_name

    def get_values_from_preprocess_menu_items(self, params):
        """
        Get parameter values from the preprocess menu entries and store them in a dictionary.

        Args:
            params (dict): Dictionary to store parameter values.

        Returns:
            None
        """
        for param_name, entry in self.parameter_preprocess_entries.items():
            try:
                params[param_name] = int(entry.get())
            except ValueError:
                params[param_name] = entry.get()
    
    def show_operations_image_listboxOnSelect(self, event):
        """
        Display the processed image corresponding to the selected operation in the operations listbox.

        Args:
            event: The event triggered by selecting an item in the operations listbox.

        Returns:
            None
        """
        try:
            operations_selected_index = self.operations_listbox.curselection()
            operations_index = int(operations_selected_index[0])

            self.display_processed_image(operations_index, "Preprocess", "both")
        except IndexError:
            pass

    def display_processed_image(self, operation_index, option_section, option):
        """
        Display the processed image based on the selected options.

        Args:
            operation_index (int): The index of the operation in the operations list.
            option_section (str): The section of options (e.g., "Preprocess", "Detection").
            option (str): The specific option selected within the section.

        Returns:
            None
        """

        # Clear previous data
        try:
            self.data_canvas_detection.delete("all")
            img = None

            img = self.get_image_bsed_on_selected_option(operation_index, option_section, option)

            self.handle_displaying_image_on_canvas(img)
        except Exception as e:
            # Handle any unexpected errors and log them
            error_msg = f"Error displaying processed image: {e}"
            logger.error(error_msg)

    def get_image_bsed_on_selected_option(self, operation_index, option_section, option):
        """
        Retrieve the image based on the selected options.

        Args:
            operation_index (int): The index of the operation in the operations list.
            option_section (str): The section of options (e.g., "Preprocess", "Detection").
            option (str): The specific option selected within the section.

        Returns:
            Image: The processed or original image based on the selected option.
        """

        img = None
        try:
            if option_section in self.image_show_options:
                options = self.image_show_options[option_section]
                if option in options:
                    # Perform operations for each option
                    if option == "processed":
                        img_data = self.data_for_detection[self.original_data_index]['operations'][operation_index]['processed_image']
                        img = Image.fromarray(img_data)
                    elif option == "original":
                        img = self.data_for_detection[self.original_data_index]['greyscale_image']
                    elif option == "both":
                        img_data = self.data_for_detection[self.original_data_index]['operations'][operation_index]['processed_image']
                        processed_img = Image.fromarray(img_data)
                        original_img = self.data_for_detection[self.original_data_index]['greyscale_image']
                        # Concatenate the images horizontally
                        img = concatenate_two_images(processed_img, original_img)
        except Exception as e:
            # Handle any unexpected errors and log them
            error_msg = f"Error retrieving image based on selected option: {e}"
            logger.error(error_msg)
        return img
    
    def display_header_info_labels(self):
        """
        Display header information labels based on the selected file.

        Retrieves the selected index from the data listbox and generates header information labels based on the file extension.
        """
        try:
            # Clear previous header
            for widget in self.header_section_frame.winfo_children():
                widget.destroy()
            # Header info labels
            header_labels = []

            selected_index = self.data_listbox_detection.curselection()
            if selected_index:
                index = int(selected_index[0])
                file_ext = self.data_for_detection[0]['file_name'][-3:]
                header_labels = self.create_data_for_header_labels_based_on_file_ext(index, file_ext)
                # Create labels and grid them
                self.create_header_labels(header_labels)
        except Exception as e:
            # Handle any unexpected errors and log them
            error_msg = f"Error displaying header information labels: {e}"
            logger.error(error_msg)

    def create_header_labels(self, header_labels):
        """
        Create and grid header labels in the header section frame.

        Distributes the given header labels into three rows and grids them in the header section frame.
        """

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

    def create_data_for_header_labels_based_on_file_ext(self, index, file_ext):
        """
        Create header labels based on the file extension and data index.

        Args:
            index (int): Index of the data.
            file_ext (str): File extension indicating the type of data.

        Returns:
            list: List of header labels.

        Raises:
            KeyError: If the header information for the given file extension is missing.
        """
        try:
            if file_ext.lower() == "s94":
                header_info = self.data_for_detection[index]['header_info']
                header_labels = [
                        f"X Points: {header_info['x_points']}", f"Y Points: {header_info['y_points']}", f"X Size: {header_info['x_size']}", f"Y Size: {header_info['y_size']}",
                        f"X Offset: {header_info['x_offset']}", f"Y Offset: {header_info['y_offset']}", f"Z Gain: {header_info['z_gain']}", f"Scan Angle: {header_info['Scan_Angle']}", f"Kp: {header_info['Kp']}", f"Tn: {header_info['Tn']}", f"Tv: {header_info['Tv']}", f"It: {header_info['It']}"
                    ]
            elif file_ext.lower() == "stp":
                header_info = self.data_for_detection[index]['header_info']
                header_labels = [
                        f"X Amplitude: {header_info['X Amplitude']}", f"Y Amplitude: {header_info['Y Amplitude']}", f"Z Amplitude: {header_info['Z Amplitude']}", f"Number of cols: {header_info['Number of columns']}",
                        f"Number of rows: {header_info['Number of rows']}", f"X Offset: {header_info['X-Offset']}", f"Y Offset: {header_info['Y-Offset']}", f"Z Gain: {header_info['Z Gain']}"
                    ]
            elif file_ext.lower() == "mpp":
                header_info = self.data_for_detection[index]['header_info']
                header_labels = [
                        f"X Amplitude: {header_info.get('Control', {}).get('X Amplitude', '')}", 
                        f"Y Amplitude: {header_info.get('Control', {}).get('Y Amplitude', '')}", 
                        f"Z Amplitude: {header_info.get('General Info', {}).get('Z Amplitude', '')}", 
                        f"Number of cols: {header_info.get('General Info', {}).get('Number of columns', '')}",
                        f"Number of rows: {header_info.get('General Info', {}).get('Number of rows', '')}", 
                        f"X Offset: {header_info.get('Control', {}).get('X Offset', '')}", 
                        f"Y Offset: {header_info.get('Control', {}).get('Y Offset', '')}", 
                        f"Z Gain: {header_info.get('Control', {}).get('Z Gain', '')}"
                    ]
                
            return header_labels
        except KeyError as e:
            error_msg = f"Header information for file extension '{file_ext}' is missing: {e}"
            logger.error(error_msg)
            raise e

    def sigma_slider_onChange(self, value, param_name):
        """
        Callback function for when the sigma slider value changes.

        Args:
            value (float): The new value of the sigma slider.
            param_name (str): The name of the parameter associated with the sigma slider.

        Raises:
            ValueError: If the provided value cannot be converted to a float.
        """
        try:
            if param_name in self.parameter_detection_labels:
                label_text = f"{param_name}: {float(value):.1f}"
                self.parameter_detection_labels[param_name].config(text=label_text)
                self.data_canvas_detection.delete("all")
                self.refresh_image_on_sigma_slider_change(value)
                self.resize_canvas_detection_scrollregion()
        except ValueError as e:
            # Handle the case where the value cannot be converted to a float
            error_msg = f"Invalid value for sigma slider: {e}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
    def filter_slider_on_change(self, param_name, value):
        if param_name in self.parameter_filter_labels:
            label_text = f"{param_name.replace('_', ' ').capitalize()}: {float(value):.1f}"
            self.parameter_filter_labels[param_name].config(text=label_text)
            self.refresh_image_after_filtering()

    def refresh_image_after_filtering(self):
        filter_params = {}
        if self.current_operation['edge_image'] is not None:
            original_img = self.data_for_detection[self.original_data_index]['greyscale_image']
            previous_processed_img = self.current_operation['processed_image']
            edge_img = self.current_operation['edge_image']
            contours = self.current_operation['contours']
            result_image = None
            self.get_values_from_filter_menu_items(filter_params)
            result_image, filtered_contours = self.process_contours(filter_params, edge_img, contours)

            contours_data = GetContourData(
                self, 
                filtered_contours= filtered_contours,
                x_size_coefficient= self.current_size_x_coefficient,
                y_size_coefficient= self.current_size_y_coefficient,
                avg_coefficient= self.current_area_coefficient
                )
            
            labeled_image = DrawLabels(
                original_img, 
                contours_data, 
                self.draw_contours_var.get(), 
                self.write_labels_var.get()
                )

            self.update_current_operation(
                previous_processed_img= previous_processed_img, 
                edge_img= edge_img, 
                contours= contours,
                contours_data= contours_data,
                contour_image= Image.fromarray(result_image),
                labeled_image=labeled_image
                )
            
            if isinstance(labeled_image, np.ndarray):
                labeled_image = Image.fromarray(labeled_image)
            img = concatenate_four_images(previous_processed_img, labeled_image, edge_img, Image.fromarray(result_image))
            self.handle_displaying_image_on_canvas(img)


    def process_contours(self, filter_params, edge_img, contours):
        filtered_contours = ContourFilter(
                contours= contours,
                circularity_low= filter_params['circularity_low'],
                circularity_high= filter_params['circularity_high'],
                min_area= filter_params['min_area'],
                max_area= filter_params['max_area']
            )
        result_image = DrawContours(
                image= edge_img,
                contours= filtered_contours
            )
        
        return result_image,filtered_contours

    def update_current_operation(self, previous_processed_img=None, edge_img=None, contours=None, contour_image=None,
                                process_name="", labeled_image=None, contours_data=None):
        current_operation = self.current_operation.copy()  # Make a copy to avoid modifying the original dictionary
        # Update specific attributes if provided
        if contours_data is not None:
            current_operation["contours_data"] = contours_data
            self.update_avg_area_label(contour_data= contours_data)
        if previous_processed_img is not None:
            current_operation["processed_image"] = previous_processed_img
        if edge_img is not None:
            current_operation["edge_image"] = edge_img
        if contours is not None:
            current_operation["contours"] = contours
        if contour_image is not None:
            current_operation["filtered_contours_img"] = contour_image
        if process_name:
            current_operation["process_name"] = process_name
        if labeled_image is not None:
            current_operation["labeled_image"] = labeled_image

        self.current_operation = current_operation
        
    def refresh_image_on_sigma_slider_change(self, sigma_value):
        """
        Refresh the image when the sigma slider value changes.

        This method updates the image displayed on the canvas when the sigma slider value changes.

        Args:
            sigma_value (float): The new value of the sigma slider.
        """
        self.handle_sigma_data_creation(sigma_value)

        self.refresh_image_after_filtering()

    def handle_sigma_data_creation(self, sigma_value):
        params = {}
        filter_params = {}
        index = self.original_data_index
        focuse_widget = self.root.focus_get()
        img = self.get_image_based_on_selected_file_in_listbox(index, focuse_widget)

        result_image = None

        self.get_values_from_detection_menu_items(params)
        self.get_values_from_filter_menu_items(filter_params)
        # Apply detection process based on selected option and parameters
        if self.selected_detection_option == "Canny":
            result_image = EdgeDetection(
                img=np.asanyarray(img), 
                sigma=sigma_value                )
        contours = ContourFinder(result_image)
        edge_img = Image.fromarray(result_image)
        result_filtered_image, _ = self.process_contours(filter_params, edge_img, contours)
        filtered_img = Image.fromarray(result_filtered_image)
        original_img = None
        preprocessed_img = None
        if focuse_widget == self.data_listbox_detection:
            original_img = img
            preprocessed_img = Image.fromarray(np.zeros_like(original_img))
        elif focuse_widget == self.operations_listbox:
            preprocessed_img = img
        
        self.update_current_operation(
            previous_processed_img= preprocessed_img,
            edge_img= edge_img,
            contour_image= filtered_img,
            contours= contours
        )

    def navigate_prev_onClick(self):
        """
        Callback function for navigating to the previous image index when the "Prev" button is clicked.
        Decrements the current value of the navigation slider by 1 if it's greater than 0.
        """
        try:
            current_value = self.navigation_slider.get()
            if current_value > 0:
                self.navigation_slider.set(current_value - 1)
        except ValueError:
            error_msg = "Invalid current value for navigation slider"
            logger.error(error_msg)
            raise ValueError(error_msg)

    def navigate_next_onClick(self):
        """
        Callback function for navigating to the next image index when the "Next" button is clicked.
        Increments the current value of the navigation slider by 1.
        """
        try:
            current_value = self.navigation_slider.get()
            self.navigation_slider.set(current_value + 1)
        except ValueError:
            error_msg = "Invalid current value for navigation slider"
            logger.error(error_msg)
            raise ValueError(error_msg)

    def update_image_from_navigation_slider_onChange(self, event):
        """
        Callback function triggered when the value of the navigation slider changes.
        Updates the displayed image based on the current value of the navigation slider.
        Also updates the selection in the listbox and refreshes the data in the operations listbox.
        
        Args:
            event: The event object representing the slider change event.
        """
        selected_index = self.data_listbox_detection.curselection()
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
            self.data_listbox_detection.selection_clear(0, tk.END)
            self.data_listbox_detection.selection_set(index - 1)
            self.data_listbox_detection.see(index - 1)

            self.original_data_index = index - 1
            self.refresh_data_in_operations_listbox()
        self.resize_canvas_detection_scrollregion()

    def update_navigation_slider_range(self):
        """
        Updates the range of the navigation slider based on the number of items in the data listbox.
        """
        num_items = len(self.data_listbox_detection.get(0, tk.END))
        self.navigation_slider.config(from_=1, to=num_items)

    def update_image_on_rescale_slider_change(self, event):
        """
        Updates the displayed image based on the selected option when the rescale slider is changed.

        Args:
            event: The event triggered by the slider change.
        """
        if self.current_operation['edge_image'] is None:
            selected_index = self.data_listbox_detection.curselection()
            if selected_index:
                index = int(selected_index[0])
                self.display_image(index)
            selected_index = self.operations_listbox.curselection()
            if selected_index:
                opertation_index = int(selected_index[0])
                selected_option = self.choose_display_image_option_dropdown_var.get()
                self.display_processed_image(opertation_index, "Preprocess", selected_option)
        else:
            preprocess_img = self.current_operation['processed_image']
            edge_img = self.current_operation['edge_image']
            labeled_image = self.current_operation['labeled_image']
            original_img = self.data_for_detection[self.original_data_index]['greyscale_image']
            filtered_img = self.current_operation['filtered_contours_img']
            img = None
            if isinstance(labeled_image, np.ndarray):
                labeled_image = Image.fromarray(labeled_image)
            if labeled_image:
                img = concatenate_four_images(preprocess_img, labeled_image, edge_img, filtered_img)
            else:
                img = concatenate_four_images(preprocess_img, original_img, edge_img, filtered_img)
            self.handle_displaying_image_on_canvas(img)
        self.resize_canvas_detection_scrollregion()

    def display_image(self, index):
        """
        Displays the image at the specified index from file listbox.

        Args:
            index (int): The index of the image to display.
        """
        # Clear previous data
        self.data_canvas_detection.delete("all")
        self.display_header_info_labels()

        # Load greyscale image
        img = self.data_for_detection[index]['greyscale_image']

        self.original_data_index = index

        self.handle_displaying_image_on_canvas(img)

    def resize_canvas_detection_scrollregion(self, *args):
        """
        Resize the scroll region of the canvas to cover the entire canvas area.

        Args:
            event: The event triggering the resize action.
        """
        # Update the scroll region to cover the entire canvas
        self.data_canvas_detection.config(scrollregion=self.data_canvas_detection.bbox("all"))

    def insert_formated_data_to_process(self):
        """
        Clear the existing data and insert formatted data for processing.

        This method retrieves data from the application, formats it, and inserts it into the detection data.
        It also updates the navigation slider range based on the number of items in the data.

        """
        self.data_for_detection.clear()
        self.data_listbox_detection.delete(0, tk.END)

        data = self.app.get_data()
        file_ext = data[0]['file_name'][-3:]
        for item in data:
            self.insert_data(file_ext, item)
        self.update_navigation_slider_range()

    def insert_data(self, file_ext, item):
        """
        Insert formatted data into the detection data list and the listbox.

        Args:
            file_ext (str): The file extension of the item.
            item (dict): The item to be inserted into the data.

        """
        if file_ext.lower() == "stp" or file_ext.lower() == "s94":
            filename_only = os.path.basename(item['file_name'])
            self.data_listbox_detection.insert(tk.END, filename_only)
            self.data_for_detection.append({
                    "file_name": item['file_name'],
                    "header_info": item['header_info'],
                    "original_data": item['data'],
                    "greyscale_image": create_greyscale_image(item['data']),
                    "operations": []
                })
        elif file_ext.lower() == "mpp":
            filename_only = os.path.basename(item['file_name'])
            for i, frame in enumerate(item['data'], start=1):
                frame_name = f"{filename_only}: frame {i}"
                self.data_listbox_detection.insert(tk.END, frame_name)
                self.data_for_detection.append({
                    "file_name": item['file_name'],
                    "frame_number": i,
                    "header_info": item['header_info'],
                    "original_data": frame,
                    "greyscale_image": create_greyscale_image(frame),
                    "operations": []
                    })

    def show_data_onDataListboxSelect(self, event):
        """
        Display selected data when an item is selected in the data listbox.

        Args:
            event: The event triggered by selecting an item in the listbox.

        """
        file_ext = self.data_for_detection[0]['file_name'][-3:]
        # Get the index of the selected filename
        selected_index = self.data_listbox_detection.curselection()
        if selected_index:
            index = int(selected_index[0])
            header_info = self.data_for_detection[index]['header_info']
            self.current_size_x_coefficient, self.current_size_y_coefficient = calculate_pixel_to_nm_coefficients(
                header_info= header_info,
                file_ext= file_ext
            )

            self.current_area_coefficient = calculate_avg_nm_per_px(
                header_info= header_info,
                file_ext= file_ext
            )

            # Update navigation slider
            self.navigation_slider.set(index + 1)
            self.display_image(index)
            self.refresh_data_in_operations_listbox()