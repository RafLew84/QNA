# -*- coding: utf-8 -*-
"""
Module for processing in the application.

@author
rlewandkow
"""

import os, sys

sys.path.insert(1, "/".join(os.path.realpath(__file__).split("/")[0:-2]))

import tkinter as tk
import numpy as np
from tkinter import ttk
from PIL import Image, ImageTk

from ui.main_window.tabs.measurement.measurement_data import (
    data_for_measurement,
    insert_data,
    clear_measurement_data,
    insert_formatted_data
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

import logging

logger = logging.getLogger(__name__)

class MeasurementTab:
    """Class representing the tab for spots detection in the application."""

    def __init__(self, notebook, app):

        self.measurement_tab = ttk.Frame(notebook)
        notebook.add(self.measurement_tab, text="Measurement")
        self.app = app
        self.root = app.root

        self.selected_process_option = None

        # self.load_params()

        self.create_measurement_tab()

        self.measured_data = []

        # {
        #     'names': [],
        #     'images': []
        # }

        self.current_data_index = 0

    def create_measurement_tab(self):
        self.configure_tab()
        self.create_data_ui()
        self.create_canvas_ui()
        self.create_scaling_ui()
        self.create_navigation_ui()

        # Display header information labels
        self.header_section_frame = ttk.Frame(self.measurement_tab, padding="5")
        self.header_section_frame.grid(row=0, column=4, padx=5, pady=2, sticky="nsew")

        # Header section name label
        self.header_section_name_label = tk.Label(self.header_section_frame, text="Header Info:")
        self.header_section_name_label.grid(row=0, column=2, padx=5, pady=2, sticky="e")

        # Display Proccess Options
        self.process_section_menu = ttk.Frame(self.measurement_tab, padding="3")
        self.process_section_menu.grid(row=0, column=5,rowspan=2, columnspan=2, padx=5, pady=2, sticky="nsew")

        self.display_header_info_labels()
        self.display_detection_section_menu()
    
    def configure_tab(self):
        # Set row and column weights
        self.measurement_tab.grid_rowconfigure(1, weight=1)
        self.measurement_tab.grid_columnconfigure(4, weight=1)
    
    def create_data_ui(self):
        # Button to load data
        self.load_data_button = tk.Button(
            self.measurement_tab, 
            text="Load Data", 
            command=self.load_data_onClick
            )
        self.load_data_button.grid(row=0, column=0, padx=5, pady=5)
        
        # Create listbox to display filenames
        self.data_listbox_processing = tk.Listbox(
            self.measurement_tab, 
            width=20, 
            height=10, 
            selectmode=tk.SINGLE
            )
        self.data_listbox_processing.grid(row=1, column=0, rowspan=2, padx=5, pady=5, sticky="nsew")
        self.listbox_scrollbar_processing = tk.Scrollbar(
            self.measurement_tab, 
            orient=tk.VERTICAL, 
            command=self.data_listbox_processing.yview
            )
        self.listbox_scrollbar_processing.grid(row=1, column=1, rowspan=2, sticky="ns")
        self.data_listbox_processing.config(yscrollcommand=self.listbox_scrollbar_processing.set)
        self.data_listbox_processing.bind("<<ListboxSelect>>", self.show_data_onDataListboxSelect)

        # Create listbox to display selected items for measurement
        self.data_listbox_measurement = tk.Listbox(
            self.measurement_tab, 
            width=20, 
            height=10, 
            selectmode=tk.SINGLE
            )
        self.data_listbox_measurement.grid(row=1, column=2, rowspan=2, padx=5, pady=5, sticky="nsew")

        self.remove_button = tk.Button(self.measurement_tab, text="Remove", command=self.remove_from_measurement_onClick)
        self.remove_button.grid(row=3, column=2, padx=5, pady=5)

        self.listbox_scrollbar_measurement = tk.Scrollbar(
            self.measurement_tab, 
            orient=tk.VERTICAL, 
            command=self.data_listbox_measurement.yview
            )
        self.listbox_scrollbar_measurement.grid(row=1, column=3, rowspan=2, sticky="ns")
        self.data_listbox_measurement.config(yscrollcommand=self.listbox_scrollbar_measurement.set)
        self.data_listbox_measurement.bind("<<ListboxSelect>>", self.show_data_onMeasurementListboxSelect)
    
    def remove_from_measurement_onClick(self):
        focuse_widget = self.root.focus_get()
        if focuse_widget == self.data_listbox_measurement:
            data_selected_index = self.data_listbox_measurement.curselection()
            remove_index = int(data_selected_index[0])
            del self.measured_data[remove_index]
            self.data_listbox_measurement.delete(remove_index)
    
    def load_data_onClick(self):
        try:
            # self.data_for_detection = self.app.get_data()
            self.insert_formated_data_to_process()
        except Exception as e:
            error_msg = f"Error loading data for spots detection: {e}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
    def insert_formated_data_to_process(self):
        clear_measurement_data()
        self.data_listbox_processing.delete(0, tk.END)
        self.data_listbox_measurement.delete(0, tk.END)
        self.measured_data.clear()

        data = self.app.get_data()
        if 'operations' in data[0]:
            file_ext = data[0]['file_name'][-3:]
            data_name = insert_formatted_data(file_ext, data)
            self.data_listbox_processing.insert(tk.END, *data_name)
            self.data_listbox_measurement.insert(tk.END, *data_name)
        else:
            file_ext = data[0]['file_name'][-3:]
            names = []
            for item in data:
                data_name = insert_data(file_ext, item)
                names.append(data_name)
            names = [item for sublist in names for item in sublist]
            self.data_listbox_processing.insert(tk.END, *names)
            self.data_listbox_measurement.insert(tk.END, *names)

        for name, item in zip(names, data_for_measurement):
            self.measured_data.append({
                'name': name,
                'image': item['greyscale_image']
            })
        # print(len(self.measured_data))
            # self.measured_data['images'].append(item['greyscale_image'])
        self.update_navigation_slider_range()
    
    def show_data_onDataListboxSelect(self, event):
        # Get the index of the selected filename
        selected_index = self.data_listbox_processing.curselection()
        if selected_index:
            index = int(selected_index[0])
            self.current_data_index = index
            # Update navigation slider
            self.navigation_slider.set(index + 1)
            self.display_image(index)
            self.refresh_data_in_operations_listbox()

    def show_data_onMeasurementListboxSelect(self, event):
        selected_index = self.data_listbox_measurement.curselection()
        if selected_index:
            index = int(selected_index[0])
            self.display_image_for_measurement(index)

    def refresh_data_in_operations_listbox(self):
        self.operations_listbox.delete(0, tk.END)
        index = self.current_data_index      
        operations = get_all_operations(data_for_measurement, index)
        self.operations_listbox.insert(tk.END, *operations)

    def display_image(self, index):
        # Clear previous data
        self.data_canvas_processing.delete("all")
        self.display_header_info_labels()

        # Load greyscale image
        img = get_greyscale_image_at_index(data_for_measurement, index)
        self.handle_displaying_image_on_canvas(img)

        self.display_header_info_labels()

    def display_image_for_measurement(self, index):
        self.data_canvas_processing.delete("all")
        img = self.measured_data[index]['image']
        # img = self.measured_data['images'][index]

        self.handle_displaying_image_on_canvas(img)

    def handle_displaying_image_on_canvas(self, img):
        # Retrieve the scale factor
        scale_factor = self.scale_factor_var.get()
        # Resize the image
        img = scale_factor_resize_image(img, scale_factor)

        # Convert the PIL image to a Tkinter PhotoImage
        photo = ImageTk.PhotoImage(img)

        # Display the image on the canvas
        self.data_canvas_processing.create_image(0, 0, anchor="nw", image=photo)

        # Save a reference to the PhotoImage to prevent garbage collection
        self.data_canvas_processing.image = photo

    def update_navigation_slider_range(self):
        num_items = len(self.data_listbox_processing.get(0, tk.END))
        self.navigation_slider.config(from_=1, to=num_items)

    def create_navigation_ui(self):
        # Slider for navigation
        self.navigation_slider = tk.Scale(
            self.measurement_tab, 
            from_=1, 
            to=1, 
            orient=tk.HORIZONTAL, 
            command=self.update_image_from_navigation_slider_onChange
            )
        self.navigation_slider.grid(row=4, column=3, columnspan=2, padx=5, pady=5, sticky="ew")

        # Navigation buttons
        self.prev_button = tk.Button(self.measurement_tab, text="Prev", command=self.navigate_prev_onClick)
        self.prev_button.grid(row=4, column=2, padx=5, pady=5)
        self.next_button = tk.Button(self.measurement_tab, text="Next", command=self.navigate_next_onClick)
        self.next_button.grid(row=4, column=5, padx=5, pady=5)
    
    def create_scaling_ui(self):
        # Scale factor label and slider
        self.scale_factor_label = tk.Label(self.measurement_tab, text="Scale Factor:")
        self.scale_factor_label.grid(row=3, column=3, padx=5, pady=5, sticky="e")
        self.scale_factor_var = tk.DoubleVar()
        self.scale_factor_var.set(1.0)  # Default scale factor
        self.scale_factor_slider = tk.Scale(
            self.measurement_tab, 
            from_=0.1, 
            to=10.0, 
            resolution=0.1, 
            orient=tk.HORIZONTAL, 
            variable=self.scale_factor_var, 
            length=200
            )
        self.scale_factor_slider.grid(row=3, column=4, padx=5, pady=5, sticky="ew")
        
        # Bind event for slider changes
        self.scale_factor_slider.bind("<ButtonRelease-1>", self.update_image_on_rescale_slider_change)
    
    def create_canvas_ui(self):
        self.data_canvas_processing = tk.Canvas(self.measurement_tab, bg="white")
        self.data_canvas_processing.grid(row=1, column=4, padx=5, pady=5, sticky="nsew")
        self.vertical_scrollbar_processing = tk.Scrollbar(
            self.measurement_tab, 
            orient=tk.VERTICAL, 
            command=self.data_canvas_processing.yview
            )
        self.vertical_scrollbar_processing.grid(row=1, column=5, sticky="ns")
        self.data_canvas_processing.configure(yscrollcommand=self.vertical_scrollbar_processing.set)
        self.horizontal_scrollbar_processing = tk.Scrollbar(
            self.measurement_tab, 
            orient=tk.HORIZONTAL, 
            command=self.data_canvas_processing.xview
            )
        self.horizontal_scrollbar_processing.grid(row=2, column=4, sticky="ew")
        self.data_canvas_processing.configure(xscrollcommand=self.horizontal_scrollbar_processing.set)
        
        # Bind event for canvas resizing
        self.data_canvas_processing.bind("<Configure>", self.resize_canvas_detection_scrollregion)
    
    def update_image_from_navigation_slider_onChange(self, event):
        selected_index = self.data_listbox_processing.curselection()
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
            self.data_listbox_processing.selection_clear(0, tk.END)
            self.data_listbox_processing.selection_set(index - 1)
            self.data_listbox_processing.see(index - 1)

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
        selected_index = self.data_listbox_processing.curselection()
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
            self.data_canvas_processing.delete("all")
            img = None
            index = self.current_data_index
            img_data = get_preprocessed_image_data_at_index(data_for_measurement, index, operation_index)
            processed_img = Image.fromarray(img_data)
            original_img = get_greyscale_image_at_index(data_for_measurement, index)
            # Concatenate the images horizontally
            img = concatenate_two_images(processed_img, original_img)
            self.handle_displaying_image_on_canvas(img)
        except Exception as e:
            # Handle any unexpected errors and log them
            error_msg = f"Error displaying processed image: {e}"
            logger.error(error_msg)

    def resize_canvas_detection_scrollregion(self, event=None):
        self.data_canvas_processing.config(scrollregion=self.data_canvas_processing.bbox("all"))

    def display_header_info_labels(self):
        try:
            # Clear previous header
            for widget in self.header_section_frame.winfo_children():
                widget.destroy()
            # Header info labels
            header_labels = []

            selected_index = self.data_listbox_processing.curselection()
            if selected_index:
                index = int(selected_index[0])
                file_ext = get_file_extension(data_for_measurement)
                header_labels = self.create_data_for_header_labels_based_on_file_ext(index, file_ext)
                # Create labels and grid them
                self.create_header_labels(header_labels)
        except Exception as e:
            # Handle any unexpected errors and log them
            error_msg = f"Error displaying header information labels: {e}"
            logger.error(error_msg)

    def display_detection_section_menu(self):
        try:
            # self.display_process_options_menu()

            self.replace_button = tk.Button(self.process_section_menu, text="Replace", command=self.replace_button_onClick)
            self.replace_button.grid(row=0, column=0, padx=5, pady=5)

            # Listbox to show all operations
            self.operations_listbox = tk.Listbox(self.process_section_menu)
            self.operations_listbox.grid(row=0, column=1,rowspan=5, padx=5, pady=5, sticky="nsew")

            self.operations_listbox.bind("<<ListboxSelect>>", self.show_operations_image_listboxOnSelect)

            # Add scrollbar to the listbox
            self.operations_scrollbar = tk.Scrollbar(self.process_section_menu, orient="vertical", command=self.operations_listbox.yview)
            self.operations_scrollbar.grid(row=0, column=2, rowspan=5, padx=5, pady=5, sticky="ns")
            self.operations_listbox.config(yscrollcommand=self.operations_scrollbar.set)
        except Exception as e:
            error_msg = f"Error occurred while creating the detection section menu: {e}"
            logger.error(error_msg)
            raise ValueError(error_msg)
    
    def replace_button_onClick(self):
        focuse_widget = self.root.focus_get()
        if focuse_widget == self.operations_listbox:
            operations_selected_index = self.operations_listbox.curselection()
            operations_index = int(operations_selected_index[0])
            self.measured_data[self.current_data_index]['image'] = Image.fromarray(get_preprocessed_image_data_at_index(data_for_measurement, self.current_data_index, operations_index))
        
    def get_image_based_on_selected_file_in_listbox(self, index, focuse_widget):
        img = None
        if focuse_widget == self.data_listbox_processing:
            img = get_greyscale_image_at_index(data_for_measurement, index)
        elif focuse_widget == self.operations_listbox:
            operations_selected_index = self.operations_listbox.curselection()
            operations_index = int(operations_selected_index[0])
            img = Image.fromarray(get_preprocessed_image_data_at_index(data_for_measurement, index, operations_index))
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
        header_info = get_header_info_at_index(data_for_measurement, index)
        filename = get_filename_at_index(data_for_measurement, index)
        stp_labels = get_stp_labels(header_info, filename)
        return stp_labels
    
    def get_header_labels_from_s94_file(self, index):
        header_info = get_header_info_at_index(data_for_measurement, index)
        filename = get_filename_at_index(data_for_measurement, index)
        s94_labels = get_s94_labels(header_info, filename)
        return s94_labels

    def get_header_labels_from_mpp_file(self, index):
        header_info = get_header_info_at_index(data_for_measurement, index)
        filename = get_filename_at_index(data_for_measurement, index)
        framenumber = get_framenumber_at_index(data_for_measurement, index)
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
