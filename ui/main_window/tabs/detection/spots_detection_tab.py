# -*- coding: utf-8 -*-
"""
Module for spots detection in the application.

@author
rlewandkow
"""

import os, sys

sys.path.insert(1, "/".join(os.path.realpath(__file__).split("/")[0:-2]))

import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import numpy as np
import copy

from data.processing.img_process import (
    EdgeDetection, 
    concatenate_two_images,
    ContourFinder, 
    concatenate_four_images,
    GetContourData, 
    DrawLabels,
    calculate_contour_avg_area,
    process_contours_filters
)

from data.processing.file_process import (
    calculate_avg_nm_per_px, 
    calculate_pixel_to_nm_coefficients,
    get_image_sizes
)

from ui.main_window.tabs.detection.params_default_values import (
    detection_params,
    filter_params,
    preprocess_params
)

from ui.main_window.tabs.detection.detection_data import (
    data_for_detection,
    get_filename_at_index,
    get_framenumber_at_index,
    get_header_info_at_index,
    get_path_at_index,
    get_greyscale_image_at_index,
    get_preprocessed_image_data_at_index,
    get_all_operations,
    get_file_extension,
    insert_data,
    insert_formatted_data,
    insert_operation_at_index,
    clear_detection_data,
    get_s94_labels,
    get_mpp_labels,
    get_stp_labels,
    calculate_min_max_coeff_for_filters
)

from ui.main_window.tabs.detection.contours_data import (
    saved_conoturs,
    get_contours_data_at_index,
    get_contours_data,
    insert_contour
)

from ui.main_window.tabs.detection.canvas_operations import (
    get_mouse_position_in_canvas,
    get_contour_info_at_position,
    scale_factor_resize_image,
    perform_gaussian_blur,
    perform_non_local_denoising,
    perform_gaussian_filter
)

from ui.main_window.tabs.detection.save_data import (
    save_labeled_image, 
    save_avg_area_to_csv,
    save_data_to_csv
)

from ui.main_window.tabs.detection.current_operation_model import CurrentOperation

from ui.main_window.tabs.detection.preprocess_operations import create_preprocess_operation
from ui.main_window.tabs.detection.contours import create_contour_data

from ui.main_window.tabs.detection.iou_window import IntersectionOverUnionWindow

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
        """

        self.spots_detection_tab = ttk.Frame(notebook)
        notebook.add(self.spots_detection_tab, text="Detection")
        self.app = app
        self.root = app.root

        self.load_params()
        self.init_attributes()

        self.current_operation = CurrentOperation()

        self.selected_preprocess_option = None

        self.create_spots_detection_tab()

    def init_attributes(self):
        """
        Initialize attributes for the SpotsDetectionTab instance.

        Attributes:
            current_size_x_coefficient (float): Coefficient for the current size in the x dimension.
            current_size_y_coefficient (float): Coefficient for the current size in the y dimension.
            current_area_coefficient (float): Coefficient for the current area size.
            min_size_scale (float): Minimum size scale for minimum size slider.
            max_size_min_scale (float): Minimum scale for the maximum size slider.
            max_size_max_scale (float): Maximum scale for the maximum size slider.
        """
        self.current_size_x_coefficient = 0
        self.current_size_y_coefficient = 0
        self.current_area_coefficient = 0

        self.min_size_scale = 0
        self.max_size_min_scale = 0
        self.max_size_max_scale = 0
    
    def create_spots_detection_tab(self):
        """
        Create the GUI components for the spots detection tab.

        This method initializes and lays out the widgets for the spots detection tab.

        Raises:
            ValueError: If there is an issue creating the GUI components.
        """
        try:
            # Data for analisys

            self.configure_tab()

            self.create_data_ui()
            self.create_canvas_ui()
            self.create_scaling_ui()
            self.create_navigation_ui()
            self.create_contours_edit_ui()

            # Display header information labels
            self.header_section_frame = ttk.Frame(self.spots_detection_tab, padding="5")
            self.header_section_frame.grid(row=0, column=2, padx=5, pady=2, sticky="nsew")

            # Header section name label
            self.header_section_name_label = tk.Label(self.header_section_frame, text="Header Info:")
            self.header_section_name_label.grid(row=0, column=0, padx=5, pady=2, sticky="e")

            # Display Proccess Options
            self.detection_section_menu = ttk.Frame(self.spots_detection_tab, padding="3")
            self.detection_section_menu.grid(row=0, column=5,rowspan=2, columnspan=2, padx=5, pady=2, sticky="nsew")

            self.display_header_info_labels()
            self.display_detection_section_menu()
        except Exception as e:
            error_msg = f"Error creating spots detection tab: {e}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
    
    def configure_tab(self):
        """
        Configure the grid layout for the spots detection tab.

        This method sets the row and column weights to ensure proper resizing of the UI elements.
        """
        # Set row and column weights
        self.spots_detection_tab.grid_rowconfigure(1, weight=1)
        self.spots_detection_tab.grid_columnconfigure(2, weight=1)
    
    def create_data_ui(self):
        """
        Create the user interface for displaying and interacting with data.

        This method sets up buttons, listboxes, and scrollbars for loading and displaying data.
        """
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

    def create_contours_edit_ui(self):
        """
        Create the user interface for editing contours.

        This method sets up the contours section with listboxes and buttons
        for displaying and interacting with contour data.
        """
        self.contours_section = ttk.Frame(self.spots_detection_tab, padding="3")
        self.contours_section.grid(row=1, column=4,rowspan=2, padx=5, pady=2, sticky="nsew")
        
        self.contours_listbox = tk.Listbox(self.contours_section)
        self.contours_listbox.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

        self.contours_listbox.bind("<<ListboxSelect>>", self.show_contours_listboxOnSelect)

        self.delete_contour_button = tk.Button(self.contours_section, text="Delete", command=self.delete_contour_button_onClick)
        self.delete_contour_button.grid(row=1, column=0, padx=5, pady=5)

        self.contour_data_listbox = tk.Listbox(self.contours_section, selectmode=tk.MULTIPLE)
        self.contour_data_listbox.grid(row=2, column=0, padx=5, pady=5, sticky="nsew")

        self.contour_data_listbox.bind("<<ListboxSelect>>", self.select_contours_data_listboxOnSelect)
        self.contour_data_listbox.bind("<Double-Button-1>", self.show_contours_onDoubleClick)

        self.cross_contour_button = tk.Button(self.contours_section, text="IoU", command=self.iou_button_onClick)
        self.cross_contour_button.grid(row=3, column=0, padx=5, pady=5)

    
    def create_navigation_ui(self):
        """
        Create the user interface for navigation.

        This method sets up the navigation slider and buttons for navigating through images.
        """
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
        
    def create_scaling_ui(self):
        """
        Create the user interface for scaling.

        This method sets up a label, slider, and event binding for scaling operations.
        """
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
        
        # Bind event for slider changes
        self.scale_factor_slider.bind("<ButtonRelease-1>", self.update_image_on_rescale_slider_change)
        
    def create_canvas_ui(self):
        """
        Create the user interface for the canvas.

        This method sets up a canvas with scrollbars and event bindings for displaying data.
        """
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
        
        # Bind event for canvas resizing
        self.data_canvas_detection.bind("<Configure>", self.resize_canvas_detection_scrollregion)

    def load_params(self):
        """
        Load parameters for detection, filtering, and preprocessing.

        Attributes:
            preprocess_params (dict): Parameters for image preprocessing methods.
            detection_params (dict): Parameters for spot detection methods.
            filter_params (dict): Parameters for filtering methods.
        """
        self.preprocess_params = preprocess_params
        self.detection_params = detection_params
        self.filter_params = filter_params
    
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
        
    def refresh_edit_contours_listbox_data(self):
        """
        Refresh the data displayed in the contours listbox.

        This method clears the existing data in the listbox and inserts updated contour data.
        """
        self.contours_listbox.delete(0, tk.END)
        if self.current_operation:
            for contour_data in self.current_operation.contours_data:
                name = contour_data['name']
                area = contour_data['area']
                nearest = contour_data['nearest_neighbour']
                distance = contour_data['distance_to_nearest_neighbour']
                self.contours_listbox.insert(tk.END, f"{name} | {area:.3f} | {nearest} | {distance:.2f}")

    def on_canvas_hover(self, event):
        """
        Handle mouse hover events on the canvas.

        Retrieves mouse position relative to the canvas, adjusts for scale factor,
        and updates UI elements based on the detected contour under the cursor.

        Args:
            event (tk.Event): The mouse event.

        """
        x, y = get_mouse_position_in_canvas(
            scale_factor=self.scale_factor_var.get(),
            x_canvas=self.data_canvas_detection.canvasx(event.x),
            y_canvas=self.data_canvas_detection.canvasy(event.y),
            event=event
        )

        # Check if the mouse is over a contour
        item = get_contour_info_at_position(
            current_operation=self.current_operation,
            x=x,
            y=y
        )
        if item:
            # Update contour labels with data from the item
            self.update_contour_labels(
                name=item['name'],
                area=item['area'],
                distance=item['distance_to_nearest_neighbour']
            )

            self.update_nearest_neighbour_label(item['nearest_neighbour'])
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

            # Save Contours buttons
            save_contours_button = tk.Button(self.detection_section_menu, text="Save to files", command=self.save_contours_onClick)
            save_contours_button.grid(row=row + 13, column=0, padx=5, pady=5)

            save_contours_to_operations_button = tk.Button(self.detection_section_menu, text="Save to operations", command=self.save_contours_to_memory_onClick)
            save_contours_to_operations_button.grid(row=row + 13, column=1, padx=5, pady=5)

        except KeyError:
            error_msg = f"Selected option '{selected_option}' not found in detection parameters."
            logger.error(error_msg)
            raise KeyError(error_msg)
        
    def show_contours_listboxOnSelect(self, event):
        """
        Handle selection events in the contours listbox.

        This method retrieves the index of the selected contour from the listbox,
        refreshes the image after filtering, and updates the UI accordingly.

        Args:
            event (tk.Event): The selection event from the listbox.
        """
        contour_index = self.contours_listbox.curselection()
        index = int(contour_index[0])
        self.refresh_image_after_filtering(index, True)

    def select_contours_data_listboxOnSelect(self, event):
        """
        Handle selection events in the contour data listbox.

        This method retrieves the index of the selected data from the listbox,
        updates the current operation and coefficients, refreshes the image after filtering,
        and updates the UI accordingly.

        Args:
            event (tk.Event): The selection event from the listbox.
        """
        data_index = self.contour_data_listbox.curselection()
        index = int(data_index[0])
        data = get_contours_data_at_index(index)
        self.current_operation = data['operation']
        self.current_operation.raw_data_index = data['original_data_index']
        self.current_size_x_coefficient = data['x_coeff']
        self.current_size_y_coefficient = data['y_coeff']
        self.current_area_coefficient = data['area_coeff']
        self.refresh_image_after_filtering(manual_edit=True)
        self.refresh_edit_contours_listbox_data()
        self.update_avg_area_label(self.current_operation.contours_data)

    def show_contours_onDoubleClick(self, event):
        pass

    def iou_button_onClick(self):
        """
        Handle click event for IoU button.

        This method creates an IntersectionOverUnionWindow instance,
        retrieves selected indices from contour data listbox,
        retrieves selected items based on indices, and opens a new window
        displaying IoU information for selected items.

        """
        iou_window = IntersectionOverUnionWindow(self.app)
        selected_indices = self.contour_data_listbox.curselection()
        selected_items = [self.contour_data_listbox.get(i) for i in selected_indices]
        iou_window.open_new_window(selected_items)
        
    def update_nearest_neighbour_label(self, text):
        """
        Update the nearest neighbour label with the provided text.

        Args:
            text (str): The text to display in the nearest neighbour label.
        """
        self.nearest_neighbour_name_label.config(text=f"Nearest neighbour: {text}")
        
    def update_avg_area_label(self, contour_data):
        """
        Update the average area label with the calculated average area based on contour data.

        Args:
            contour_data (list): List of contour data dictionaries.

        """
        avg_area = calculate_contour_avg_area(contour_data)
        self.avg_area_label.config(text=f"Average Area: {avg_area:.3f} nm2")

    def update_contour_labels(self, name, area, distance):
        """
        Update the contour labels with the provided data.

        Args:
            name (str): The name of the contour.
            area (float): The area of the contour.
            distance (float): The shortest distance associated with the contour.
        """
        # Update the text of each label
        self.contour_name_label.config(text=f"Name: {name}")
        self.contour_area_label.config(text=f"Area: {area:.3} nm2")
        self.contour_shortest_distance_label.config(text=f"Shortest distance: {distance:.3} nm")
        
    def create_filter_menu_items(self, row):
        """
        Create filter menu items based on filter parameters.

        Args:
            row (int): The starting row index for placing menu items.

        Returns:
            int: The updated row index after placing menu items.
        """
        for filter_type, params in self.filter_params.items():
            filter_frame = ttk.Label(self.detection_section_menu, text=filter_type + ":")
            filter_frame.grid(row=row, column=0, padx=10, pady=5, sticky="nsew")

            for param_name, param_value in params.items():
                label_text = f"{param_name.replace('_', ' ').capitalize()}: {param_value:.1f}"
                label = tk.Label(self.detection_section_menu, text=label_text)
                label.grid(row=row + 1, column=0, padx=5, pady=5)
                self.parameter_filter_labels[param_name] = label

                self.add_slider_to_menu(row, param_name, param_value)

                row += 1
            row += 1
        
        # Add checkboxes for draw contours and write labels
        self.add_chackboxes_to_menu(row)

        row += 2

        return row

    def add_chackboxes_to_menu(self, row):
        """
        Add checkboxes for draw contours, write labels, and label contour color to the menu.

        Args:
            row (int): The row index to place the checkboxes.
        """
        draw_contours_var = tk.IntVar()
        draw_contours_checkbox = tk.Checkbutton(
            self.detection_section_menu, text="Draw Contours", 
            variable=draw_contours_var, 
            command=self.checkbox_status_changed
            )
        draw_contours_checkbox.grid(row=row, column=0, padx=5, pady=5, sticky="w")
        self.draw_contours_var = draw_contours_var

        write_labels_var = tk.IntVar()
        write_labels_checkbox = tk.Checkbutton(
            self.detection_section_menu, 
            text="Write Labels", 
            variable=write_labels_var, 
            command=self.checkbox_status_changed
            )
        write_labels_checkbox.grid(row=row, column=1, padx=5, pady=5, sticky="w")
        self.write_labels_var = write_labels_var

        label_contour_color_var = tk.IntVar()
        label_contour_color_checkbox = tk.Checkbutton(
            self.detection_section_menu, 
            text="Labels Color", 
            variable=label_contour_color_var, 
            command=self.checkbox_status_changed
            )
        label_contour_color_checkbox.grid(row=row + 1, column=0, padx=5, pady=5, sticky="w")
        self.label_contour_color_var = label_contour_color_var

    def add_slider_to_menu(self, row, param_name, param_value):
        """
        Add a slider to the menu for adjusting filter parameters.

        Args:
            row (int): The row index to place the slider.
            param_name (str): The name of the parameter.
            param_value (float): The initial value of the parameter.
        """
        if param_name.startswith("min"):
            slider = ttk.Scale(
                        self.detection_section_menu,
                        from_=0.0,
                        to=self.min_size_scale,
                        orient="horizontal",
                        command=lambda value=param_value, param=param_name: self.filter_slider_on_change(param, value)
                    )
        elif param_name.startswith("max"):
            slider = ttk.Scale(
                        self.detection_section_menu,
                        from_=self.max_size_min_scale,
                        to=self.max_size_max_scale,
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
    
    def checkbox_status_changed(self):
        """
        Handle changes in checkbox status.

        Checks if the focus is on the contour data listbox and triggers
        image refreshing with manual edit if so, otherwise triggers image refreshing.
        """
        focuse_widget = self.root.focus_get()
        if focuse_widget == self.contour_data_listbox:
            self.refresh_image_after_filtering(manual_edit=True)
        else:
            self.refresh_image_after_filtering()

    def delete_contour_button_onClick(self):
        """
        Handle the click event of the delete contour button.

        Deletes the selected contour from the current operation's contour data,
        refreshes the contours listbox data, refreshes the image after filtering,
        and updates the average area label.
        """
        focuse_widget = self.root.focus_get()
        if focuse_widget == self.contours_listbox:
            contour_index = self.contours_listbox.curselection()
            index = int(contour_index[0])
            self.current_operation.contours_data.pop(index)
            self.refresh_edit_contours_listbox_data()
            self.refresh_image_after_filtering(manual_edit=True)
            self.update_avg_area_label(self.current_operation.contours_data)
            

    def save_contours_to_memory_onClick(self):
        """
        Handle the click event of the save contours to memory button.

        Saves the current operation's contour data to memory, inserts it into the
        saved contours list, and refreshes the saved contours listbox data.
        """
        index = self.current_operation.raw_data_index
        filename = get_filename_at_index(index)
        framenumber = get_framenumber_at_index(index)

        data_to_save = create_contour_data(
            filename= filename,
            framenumber= framenumber,
            operation= copy.deepcopy(self.current_operation),
            contours_num= len(self.current_operation.contours_data),
            originally_processed_image= self.current_operation.image_to_process,
            original_data_index= self.current_operation.raw_data_index,
            x_coeff= self.current_size_x_coefficient,
            y_coeff= self.current_size_y_coefficient,
            area_coeff= self.current_area_coefficient
        )

        insert_contour(data_to_save)
        self.refresh_saved_contours_listbox_data()

    def refresh_saved_contours_listbox_data(self):
        """
        Refresh the data in the saved contours listbox.

        Retrieves contours data from memory, updates the saved contours listbox
        with filenames, frame numbers, and number of contours.
        """
        self.contour_data_listbox.delete(0, tk.END)
        contours = get_contours_data()
        if contours:
            for contour_data in contours:
                name = contour_data['filename']
                frame = contour_data['frame']
                number_of_contours = str(contour_data['contours_num'])
                if frame == "":
                    self.contour_data_listbox.insert(tk.END, f"{name} | {number_of_contours}")
                else:
                    self.contour_data_listbox.insert(tk.END, f"{name} | {frame} | {number_of_contours}")


    def save_to_files(self):
        """
        Save labeled image and contour data to files.

        Saves the labeled image to a PNG file and the contour data to a CSV file.
        Also calculates and saves the average area of contours to a CSV file.
        """
        labeled_image = self.current_operation.labeled_image
        if isinstance(labeled_image, np.ndarray):
            labeled_image = Image.fromarray(labeled_image)
        output_dir, name = self.save_img(labeled_image)

        contours_data = self.current_operation.contours_data

        # Define the CSV filename
        csv_filename = name + ".csv"  # Use the same 'name' as the PNG file
        
        save_data_to_csv(output_dir, contours_data, csv_filename)

        avg_area = calculate_contour_avg_area(contours_data)

        save_avg_area_to_csv(output_dir, csv_filename, avg_area)

    def save_img(self, labeled_image):
        """
        Save labeled image to disk.

        Args:
            labeled_image (PIL.Image.Image or np.ndarray): Labeled image to save.

        Returns:
            tuple: Tuple containing output directory and filename.
        """
        index = self.current_operation.raw_data_index
        path = get_path_at_index(index)
        filename = get_filename_at_index(index)
        framenumber = get_framenumber_at_index(index)

        return save_labeled_image(labeled_image, path, filename, framenumber)
        
    def save_contours_onClick(self):
        self.save_to_files()
        
    def get_values_from_filter_menu_items(self, params):
        """
        Retrieve values from filter menu sliders and update the params dictionary.

        Args:
            params (dict): Dictionary to update with parameter values.

        Notes:
            If a slider value cannot be converted to float, it is added as a string to params.
        """
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
        img = None
        if focuse_widget == self.data_listbox_detection:
            img = get_greyscale_image_at_index(index)
            self.current_operation.image_to_process = img
        elif focuse_widget == self.operations_listbox:
            operations_selected_index = self.operations_listbox.curselection()
            operations_index = int(operations_selected_index[0])
            img = Image.fromarray(get_preprocessed_image_data_at_index(self.current_operation.raw_data_index, operations_index))
            self.current_operation.image_to_process = img
        elif focuse_widget == self.contours_listbox:
            img = self.current_operation.image_to_process
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
        img = scale_factor_resize_image(img, scale_factor)

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

        selected_index = self.current_operation.raw_data_index

        operations = get_all_operations(selected_index)
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
        if self.selected_preprocess_option is None:
            return  # No option selected
        params = {}
        index = self.current_operation.raw_data_index
        focuse_widget = self.root.focus_get()
        img = self.get_image_based_on_selected_file_in_listbox(index, focuse_widget)

        result_image = None
        process_name = None

        self.get_values_from_preprocess_menu_items(params)
        # Apply preprocessing based on selected option and parameters
        result_image, process_name = self.apply_preprocessing_operation(params, img)
        operation = create_preprocess_operation(result_image, process_name, params)

        insert_operation_at_index(index, operation)

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
        preprocess_operations = {
            "GaussianBlur": perform_gaussian_blur,
            "Non-local Mean Denoising": perform_non_local_denoising,
            "GaussianFilter": perform_gaussian_filter,
        }

        if self.selected_preprocess_option in preprocess_operations:
            process_function = preprocess_operations[self.selected_preprocess_option]
            process_name, result_image = process_function(params, img)
        else:
            msg = f"Invalid preprocessing option: {self.selected_preprocess_option}"
            logger.error(msg)
            raise ValueError(msg)
            
        return result_image, process_name

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
                        img_data = get_preprocessed_image_data_at_index(self.current_operation.raw_data_index, operation_index)
                        img = Image.fromarray(img_data)
                    elif option == "original":
                        img = get_greyscale_image_at_index(self.current_operation.raw_data_index)
                    elif option == "both":
                        img_data = get_preprocessed_image_data_at_index(self.current_operation.raw_data_index, operation_index)
                        processed_img = Image.fromarray(img_data)
                        original_img = get_greyscale_image_at_index(self.current_operation.raw_data_index)
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
                file_ext = get_file_extension()
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
        Create header labels data based on the file extension.

        Args:
            index (int): Index of the data.
            file_ext (str): File extension.

        Returns:
            dict: Header labels data.

        Raises:
            KeyError: If header labels function for the specified file extension is missing.
            Exception: For any other unexpected errors.
        """
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
        """
        Callback function for when a filter slider changes its value.

        Args:
            param_name (str): Name of the parameter associated with the slider.
            value (float): New value of the slider.

        Notes:
            - Updates the label text for the parameter filter label associated with `param_name`.
            - Calls `refresh_image_after_filtering()` to update the displayed image after filtering.
            - Calls `refresh_edit_contours_listbox_data()` to update the contours list box data.
        """
        if param_name in self.parameter_filter_labels:
            label_text = f"{param_name.replace('_', ' ').capitalize()}: {float(value):.1f}"
            self.parameter_filter_labels[param_name].config(text=label_text)
            self.refresh_image_after_filtering()
            self.refresh_edit_contours_listbox_data()

    def refresh_image_after_filtering(self, hilghlight_index=None, manual_edit=False):
        """
        Refreshes the image display after applying filters or manual edits.

        Args:
            highlight_index (int or None): Index of the contour to highlight after filtering.
            manual_edit (bool): Flag indicating if the refresh was triggered by a manual edit.

        Notes:
            - Calls either `refresh_image_after_manual_change()` or `refresh_image_after_param_filtering()`
              based on the value of `manual_edit`.
            - Provides the option to highlight a specific contour identified by `highlight_index`.
        """
        if manual_edit:
            self.refresh_image_after_manual_change(hilghlight_index)
        else:
            self.refresh_image_after_param_filtering(hilghlight_index)

    def refresh_image_after_param_filtering(self, hilghlight_index):
        """
        Refreshes the image after applying parameterized filters to contours.

        Args:
            highlight_index (int or None): Index of the contour to highlight.

        Notes:
            - Retrieves filter parameters from the UI.
            - Processes contours using the retrieved parameters.
            - Draws labels and updates the displayed image based on filtered contours.
            - Updates attributes in the current operation object.
            - Concatenates multiple images and displays the result on a canvas.
        """
        filter_params = {}
        if self.current_operation.edge_image is not None:
            original_img = get_greyscale_image_at_index(self.current_operation.raw_data_index)
            previous_processed_img = self.current_operation.processed_image
            edge_img = self.current_operation.edge_image
            contours = self.current_operation.contours
            result_image = None
            self.get_values_from_filter_menu_items(filter_params)
            result_image, filtered_contours = process_contours_filters(filter_params, edge_img, contours, self.current_area_coefficient)

            contours_data = GetContourData( 
                    filtered_contours= filtered_contours,
                    x_size_coefficient= self.current_size_x_coefficient,
                    y_size_coefficient= self.current_size_y_coefficient,
                    avg_coefficient= self.current_area_coefficient
                    )
                
            if hilghlight_index:
                labeled_image = DrawLabels(
                        original_img, 
                        contours_data,
                        self.draw_contours_var.get(), 
                        self.write_labels_var.get(),
                        self.label_contour_color_var.get(),
                        hilghlight_index
                        )
            else:
                labeled_image = DrawLabels(
                        original_img, 
                        contours_data, 
                        self.draw_contours_var.get(), 
                        self.write_labels_var.get(),
                        self.label_contour_color_var.get()
                        )
                
            self.current_operation.processed_image = previous_processed_img
            self.current_operation.edge_image = edge_img
            self.current_operation.contours = contours
            self.current_operation.contours_data = contours_data
            self.current_operation.filtered_contours_img = Image.fromarray(result_image)
            self.current_operation.labeled_image = labeled_image
                
            if isinstance(labeled_image, np.ndarray):
                labeled_image = Image.fromarray(labeled_image)
            img = concatenate_four_images(previous_processed_img, labeled_image, edge_img, Image.fromarray(result_image))
            self.handle_displaying_image_on_canvas(img)

    def refresh_image_after_manual_change(self, hilghlight_index):
        """
        Refreshes the image after a manual change to contours.

        Args:
            highlight_index (int or None): Index of the contour to highlight.

        Notes:
            - Retrieves necessary attributes from the current operation object.
            - Constructs new contours data based on filtered contours.
            - Draws labels on the original image based on user settings and highlights a contour if specified.
            - Updates attributes in the current operation object with the processed data.
            - Concatenates multiple images and displays the result on a canvas.
        """
        original_img = get_greyscale_image_at_index(self.current_operation.raw_data_index)
        previous_processed_img = self.current_operation.processed_image
        edge_img = self.current_operation.edge_image
        labeled_image = self.current_operation.labeled_image
        contours_data = self.current_operation.contours_data
        filtered_mage = self.current_operation.filtered_contours_img
        filtered_contours = [data['contour'] for data in contours_data]

        new_contours_data = GetContourData( 
            filtered_contours= filtered_contours,
            x_size_coefficient= self.current_size_x_coefficient,
            y_size_coefficient= self.current_size_y_coefficient,
            avg_coefficient= self.current_area_coefficient
            )

        if hilghlight_index:
            labeled_image = DrawLabels(
                    original_img, 
                    new_contours_data,
                    self.draw_contours_var.get(), 
                    self.write_labels_var.get(),
                    self.label_contour_color_var.get(),
                    hilghlight_index
                    )
        else:
            labeled_image = DrawLabels(
                    original_img, 
                    new_contours_data, 
                    self.draw_contours_var.get(), 
                    self.write_labels_var.get(),
                    self.label_contour_color_var.get()
                    )
        
        self.current_operation.labeled_image = labeled_image
        self.current_operation.contours_data = new_contours_data
        # self.update_current_operation(labeled_image=labeled_image, contours_data=new_contours_data)
        if isinstance(labeled_image, np.ndarray):
            labeled_image = Image.fromarray(labeled_image)
        img = concatenate_four_images(previous_processed_img, labeled_image, edge_img, filtered_mage)
        self.handle_displaying_image_on_canvas(img)
        
    def refresh_image_on_sigma_slider_change(self, sigma_value):
        """
        Refresh the image when the sigma slider value changes.

        This method updates the image displayed on the canvas when the sigma slider value changes.

        Args:
            sigma_value (float): The new value of the sigma slider.
        """
        self.handle_sigma_data_creation(sigma_value)

        self.refresh_image_after_filtering()

        self.refresh_edit_contours_listbox_data()

    def handle_sigma_data_creation(self, sigma_value):
        """
        Handles the creation of sigma data for image processing.

        Args:
            sigma_value (float): The sigma value for edge detection.

        Notes:
            - Retrieves necessary parameters and filter settings.
            - Retrieves the image based on the selected file in the listbox.
            - Performs edge detection using Canny method with the given sigma value.
            - Finds contours in the resulting edge image.
            - Applies filters to contours based on specified filter parameters.
            - Updates attributes in the current operation object with processed data.
        """
        params = {}
        filter_params = {}
        index = self.current_operation.raw_data_index
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
        result_filtered_image, _ = process_contours_filters(filter_params, edge_img, contours, self.current_area_coefficient)
        filtered_img = Image.fromarray(result_filtered_image)
        original_img = None
        preprocessed_img = None
        if focuse_widget == self.data_listbox_detection:
            original_img = img
            preprocessed_img = Image.fromarray(np.zeros_like(original_img))
        elif focuse_widget == self.operations_listbox:
            preprocessed_img = img

        self.current_operation.processed_image = preprocessed_img
        self.current_operation.edge_image = edge_img
        self.current_operation.filtered_contours_img = filtered_img
        self.current_operation.contours = contours

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

            self.current_operation.raw_data_index = index - 1
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
        if self.current_operation.edge_image is None:
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
            preprocess_img = self.current_operation.processed_image
            edge_img = self.current_operation.edge_image
            labeled_image = self.current_operation.labeled_image
            original_img = get_greyscale_image_at_index(self.current_operation.raw_data_index)
            filtered_img = self.current_operation.filtered_contours_img
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
        img = get_greyscale_image_at_index(index)

        self.current_operation.raw_data_index = index

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
        clear_detection_data()
        self.data_listbox_detection.delete(0, tk.END)

        data = self.app.get_data()
        # print(data)
        if 'operations' in data[0]:
            file_ext = data[0]['file_name'][-3:]
            data_name = insert_formatted_data(file_ext, data)
            self.data_listbox_detection.insert(tk.END, *data_name)
        else:
            file_ext = data[0]['file_name'][-3:]
            for item in data:
                data_name = insert_data(file_ext, item)
                self.data_listbox_detection.insert(tk.END, *data_name)
        self.update_navigation_slider_range()

    def show_data_onDataListboxSelect(self, event):
        """
        Display selected data when an item is selected in the data listbox.

        Args:
            event: The event triggered by selecting an item in the listbox.

        """
        file_ext = get_file_extension()
        # Get the index of the selected filename
        selected_index = self.data_listbox_detection.curselection()
        if selected_index:
            index = int(selected_index[0])
            header_info = get_header_info_at_index(index)
            self.current_size_x_coefficient, self.current_size_y_coefficient = calculate_pixel_to_nm_coefficients(
                header_info= header_info,
                file_ext= file_ext
            )

            self.current_area_coefficient = calculate_avg_nm_per_px(
                header_info= header_info,
                file_ext= file_ext
            )

            # calculate scales for min and max areas
            _, _, x, y = get_image_sizes(header_info, file_ext)
            self.calculate_scales_for_minmax_area_filters(x, y)

            # Update navigation slider
            self.navigation_slider.set(index + 1)
            self.display_image(index)
            self.refresh_data_in_operations_listbox()

    def calculate_scales_for_minmax_area_filters(self, x, y):
        """
        Calculates scales for minimum and maximum area filters based on given parameters.

        Args:
            x (float): Width or size parameter.
            y (float): Height or size parameter.
        """
        min_pixels, max_pixels = calculate_min_max_coeff_for_filters(x, y)
        self.min_size_scale = min_pixels * self.current_area_coefficient
        self.max_size_min_scale = self.min_size_scale
        self.max_size_max_scale = max_pixels * self.current_area_coefficient