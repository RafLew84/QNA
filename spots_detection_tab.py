# -*- coding: utf-8 -*-
"""


@author
"""

import os

import tkinter as tk
from tkinter import ttk

from PIL import Image, ImageTk

import numpy as np

from data_proccess import create_greyscale_image

from img_process import NlMeansDenois, GaussianBlur, GaussianFilter, EdgeDetection

import logging

logger = logging.getLogger(__name__)

class SpotsDetectionTab:
    def __init__(self, notebook, app):
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

        self.detection_params = {
            "Canny": {"sigma": 1., "low_threshold": None, "high_threshold": None}
        }

        self.selected_option = None

        self.create_spots_detection_tab()
    
    def load_data_onClick(self):
        self.data = self.app.get_data()
        self.insert_data_to_detection()

    def create_spots_detection_tab(self):
        # Data for analisys
        self.data_index = None

        # Button to load data
        self.load_data_button = tk.Button(self.spots_detection_tab, text="Load Data", command=self.load_data_onClick)
        self.load_data_button.grid(row=0, column=0, padx=5, pady=5)
        
        # Create listbox to display filenames
        self.data_listbox_detection = tk.Listbox(self.spots_detection_tab, width=20, height=10, selectmode=tk.SINGLE)
        self.data_listbox_detection.grid(row=1, column=0, rowspan=2, padx=5, pady=5, sticky="nsew")

        # Add scrollbar for the listbox
        self.listbox_scrollbar_detection = tk.Scrollbar(self.spots_detection_tab, orient=tk.VERTICAL, command=self.data_listbox_detection.yview)
        self.listbox_scrollbar_detection.grid(row=1, column=1, rowspan=2, sticky="ns")
        self.data_listbox_detection.config(yscrollcommand=self.listbox_scrollbar_detection.set)

        self.data_listbox_detection.bind("<<ListboxSelect>>", self.show_data_for_detection)

        # Add a canvas to display the data
        self.data_canvas_detection = tk.Canvas(self.spots_detection_tab, bg="white")
        self.data_canvas_detection.grid(row=1, column=2, padx=5, pady=5, sticky="nsew")

        # Create vertical scrollbar for the canvas
        self.vertical_scrollbar_detection = tk.Scrollbar(self.spots_detection_tab, orient=tk.VERTICAL, command=self.data_canvas_detection.yview)
        self.vertical_scrollbar_detection.grid(row=1, column=3, sticky="ns")
        self.data_canvas_detection.configure(yscrollcommand=self.vertical_scrollbar_detection.set)

        # Create horizontal scrollbar for the canvas
        self.horizontal_scrollbar_detection = tk.Scrollbar(self.spots_detection_tab, orient=tk.HORIZONTAL, command=self.data_canvas_detection.xview)
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
        self.scale_factor_slider = tk.Scale(self.spots_detection_tab, from_=0.1, to=10.0, resolution=0.1, orient=tk.HORIZONTAL, variable=self.scale_factor_var, length=200)
        self.scale_factor_slider.grid(row=3, column=2, padx=5, pady=5, sticky="ew")

        # Slider for navigation
        self.navigation_slider = tk.Scale(self.spots_detection_tab, from_=1, to=1, orient=tk.HORIZONTAL, command=self.update_image_from_navigation_slider)
        self.navigation_slider.grid(row=4, column=1, columnspan=3, padx=5, pady=5, sticky="ew")

        # Navigation buttons
        self.prev_button = tk.Button(self.spots_detection_tab, text="Prev", command=self.navigate_prev)
        self.prev_button.grid(row=4, column=0, padx=5, pady=5)

        self.next_button = tk.Button(self.spots_detection_tab, text="Next", command=self.navigate_next)
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

        # Display Preproccess Options
        self.detection_section_menu = ttk.Frame(self.spots_detection_tab, padding="3")
        self.detection_section_menu.grid(row=0, column=4,rowspan=2, columnspan=2, padx=5, pady=2, sticky="nsew")

        self.display_header_info_labels()
        self.display_detection_section_menu()

    def display_preprocess_options_menu(self):
        # Preprocess Dropdown menu options
        preprocessing_options = ["GaussianBlur", "GaussianFilter", "Non-local Mean Denoising"]

        self.image_show_options = {
            "Preprocess": ["processed", "both", "original"]
        }

        # Create and place dropdown menu
        dropdown_var = tk.StringVar()
        dropdown_var.set("")  # Set default option
        dropdown = tk.OptionMenu(self.detection_section_menu, dropdown_var, *preprocessing_options, command=self.update_preprocess_options)
        dropdown.config(width=10)
        dropdown.grid(row=1, column=0, padx=5, pady=1, sticky="n")

        # Create and place second dropdown menu
        self.image_option_dropdown_var = tk.StringVar()
        self.image_option_dropdown_var.set("")  # Set default option
        self.image_dropdown = tk.OptionMenu(self.detection_section_menu, self.image_option_dropdown_var, *self.image_show_options["Preprocess"], command=self.update_image)
        self.image_dropdown.config(width=10)
        self.image_dropdown.grid(row=2, column=0, padx=5, pady=1, sticky="n")

        # Labels for function parameters
        self.parameter_preprocess_entries = {}
        self.parameter_preprocess_labels = {}
        self.parameter_detection_buttons = []

    def display_detection_options_menu(self):
        detection_options = ["Canny"]

        # Create and place dropdown menu for detection options
        detection_dropdown_var = tk.StringVar()
        detection_dropdown_var.set("")  # Set default option
        detection_dropdown = tk.OptionMenu(self.detection_section_menu, detection_dropdown_var, *detection_options, command=self.update_detection_options_labels)
        detection_dropdown.config(width=10)
        detection_dropdown.grid(row=1, column=0, padx=5, pady=1, sticky="n")

        # Labels for function parameters
        self.parameter_detection_entries = {}
        self.parameter_detection_labels = {}
        self.parameter_detection_sliders = {}
        self.parameter_detection_buttons = []


    def display_detection_section_menu(self):
        display_options = ["Preprocess", "Detection"]

        # Create and place dropdown menu for detection options
        self.detection_menu_dropdown_var = tk.StringVar()
        self.detection_menu_dropdown_var.set("Preprocess")  # Set default option
        self.detection_menu_dropdown = tk.OptionMenu(self.detection_section_menu, self.detection_menu_dropdown_var, *display_options, command=self.update_detection_menu)
        self.detection_menu_dropdown.config(width=10)
        self.detection_menu_dropdown.grid(row=0, column=0, padx=5, pady=1, sticky="n")

        self.display_preprocess_options_menu()

        # Listbox to show all operations
        self.operations_listbox = tk.Listbox(self.detection_section_menu)
        self.operations_listbox.grid(row=0, column=1,rowspan=20, padx=5, pady=5, sticky="nsew")

        self.operations_listbox.bind("<<ListboxSelect>>", self.show_data_for_preprocess)

        # Add scrollbar to the listbox
        self.scrollbar = tk.Scrollbar(self.detection_section_menu, orient="vertical", command=self.operations_listbox.yview)
        self.scrollbar.grid(row=0, column=2, rowspan=20, padx=5, pady=5, sticky="ns")
        self.operations_listbox.config(yscrollcommand=self.scrollbar.set)

    def update_detection_menu(self, selected_option):
        for widget in self.detection_section_menu.winfo_children():
            if not widget in (self.operations_listbox, self.scrollbar, self.detection_menu_dropdown):
                widget.destroy()
        
        if selected_option == "Preprocess":
            self.display_preprocess_options_menu()
        elif selected_option == "Detection":
            self.display_detection_options_menu()

    def update_detection_options_labels(self, selected_option):
        self.selected_detection_option = selected_option
        # Destroy existing parameter labels and entries
        for entry in self.parameter_detection_entries.values():
            entry.destroy()
        for label in self.parameter_detection_labels.values():
            label.destroy()
        for slider in self.parameter_detection_sliders.values():
            slider.destroy()
        for button in self.parameter_detection_buttons:
            button.destroy()
        self.parameter_detection_entries.clear()
        self.parameter_detection_labels.clear()
        self.parameter_detection_sliders.clear()
        self.parameter_detection_buttons.clear()
        row = 3
        # # Update labels with function parameters based on selected option
        for param_name, param_value in self.detection_params[selected_option].items():
            if param_name == "sigma":
                # Create a slider for sigma parameter
                label_text = f"{param_name}: {param_value:.1f}"
                label = tk.Label(self.detection_section_menu, text=label_text, width=15)
                label.grid(row=row, column=0, padx=5, pady=1, sticky="w")
                slider = ttk.Scale(self.detection_section_menu, from_=0.1, to=5.0, length=100, orient="horizontal", command=lambda value=param_value, param_name=param_name: self.sigma_slider_change(value, param_name))
                slider.set(param_value)  # Set default value
                slider.grid(row=row + 1, column=0, padx=5, pady=1, sticky="w")
                self.parameter_detection_sliders[param_name] = slider
                self.parameter_detection_labels[param_name] = label
            else:
                # Create entry for other parameters
                label = tk.Label(self.detection_section_menu, text=param_name, width=15)
                label.grid(row=row, column=0, padx=5, pady=1, sticky="w")
                entry = tk.Entry(self.detection_section_menu)
                entry.grid(row=row + 1, column=0, padx=5, pady=1, sticky="w")
                entry.insert(0, str(param_value))
                self.parameter_detection_entries[param_name] = entry
                self.parameter_detection_labels[param_name] = label
            row += 2
        # Apply button for detection
        find_edges_button = tk.Button(self.detection_section_menu, text="Find Edges", command=self.apply_detection)
        find_edges_button.grid(row=row, column=0, padx=5, pady=5)
        self.parameter_detection_buttons.append(find_edges_button)

    def update_image_detection(self, selected_option):
        operations_selected_index = self.operations_listbox.curselection()
        operations_index = int(operations_selected_index[0])
        self.display_edged_image(
            operation_index= operations_index,
            option_section= "Preprocess",
            option= selected_option
        )
    
    def apply_detection(self):
        if self.selected_detection_option is None:
            return  # No option selected
        params = {}
        index = self.data_index
        focuse_widget = self.root.focus_get()
        if focuse_widget == self.data_listbox_detection:
            img = self.data_for_detection[index]['greyscale_image']
        elif focuse_widget == self.operations_listbox:
            operations_selected_index = self.operations_listbox.curselection()
            operations_index = int(operations_selected_index[0])
            img = Image.fromarray(self.data_for_detection[self.data_index]['operations'][operations_index]['processed_image'])


        result_image = None
        process_name = None

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
        # Apply detection process based on selected option and parameters
        if self.selected_detection_option == "Canny":
            process_name = "Canny"
            result_image = EdgeDetection(
                img=np.asanyarray(img), 
                sigma=params['sigma'],
                low_threshold=None if params['low_threshold'] == 'None' else params['low_threshold'],
                high_threshold=None if params['high_threshold'] == 'None' else params['high_threshold']
                )
        operation = {
            "processed_image": result_image,
            "process_name": process_name,
            "params": params,
            "contours": None,
            "labeled_image": None
        }
        self.data_for_detection[index]['operations'].append(operation)
        self.refresh_data_to_detection()
        operations_index = self.operations_listbox.size() - 1
        self.display_edged_image(operations_index, "Preprocess", "both")
        self.image_option_dropdown_var.set(self.image_show_options["Preprocess"][1])

        self.operations_listbox.focus()
        self.operations_listbox.selection_set(tk.END)

    def refresh_image_on_sigma_slider_change(self, sigma_value):
        params = {}
        index = self.data_index
        focuse_widget = self.root.focus_get()
        if focuse_widget == self.data_listbox_detection:
            img = self.data_for_detection[index]['greyscale_image']
        elif focuse_widget == self.operations_listbox:
            operations_selected_index = self.operations_listbox.curselection()
            operations_index = int(operations_selected_index[0])
            img = Image.fromarray(self.data_for_detection[self.data_index]['operations'][operations_index]['processed_image'])

        result_image = None

        for param_name, entry in self.parameter_detection_entries.items():
            try:
                params[param_name] = int(entry.get())
            except ValueError:
                params[param_name] = entry.get()
        # Apply detection process based on selected option and parameters
        if self.selected_detection_option == "Canny":
            result_image = EdgeDetection(
                img=np.asanyarray(img), 
                sigma=sigma_value,
                low_threshold=None if params['low_threshold'] == 'None' else params['low_threshold'],
                high_threshold=None if params['high_threshold'] == 'None' else params['high_threshold']
                )
        processed_img = Image.fromarray(result_image)
        original_img = img

        img = Image.new('RGB', (processed_img.width + original_img.width + 10, max(processed_img.height, original_img.height)))
        img.paste(processed_img, (0, 0))
        img.paste(original_img, (processed_img.width + 10, 0))

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

    def display_edged_image(self, operation_index, option_section, option):
        # Clear previous data
        self.data_canvas_detection.delete("all")
        img = None

        if option_section in self.image_show_options:
            options = self.image_show_options[option_section]
            if option in options:
                # Perform operations for each option
                if option == "processed":
                    img_data = self.data_for_detection[self.data_index]['operations'][operation_index]['processed_image']
                    img = Image.fromarray(img_data)
                elif option == "original":
                    img = self.data_for_detection[self.data_index]['greyscale_image']
                elif option == "both":
                    img_data = self.data_for_detection[self.data_index]['operations'][operation_index]['processed_image']
                    processed_img = Image.fromarray(img_data)
                    original_img = self.data_for_detection[self.data_index]['greyscale_image']

                    # Concatenate the images horizontally
                    img = Image.new('RGB', (processed_img.width + original_img.width + 10, max(processed_img.height, original_img.height)))
                    img.paste(processed_img, (0, 0))
                    img.paste(original_img, (processed_img.width + 10, 0))


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

    def refresh_data_to_detection(self):
        self.operations_listbox.delete(0, tk.END)

        selected_index = self.data_index

        for item in self.data_for_detection[selected_index]['operations']:
                name = item["process_name"]
                self.operations_listbox.insert(tk.END, name)


    def update_image(self, selected_option):
        operations_selected_index = self.operations_listbox.curselection()
        operations_index = int(operations_selected_index[0])
        self.display_processed_image(
            operation_index= operations_index,
            option_section= "Preprocess",
            option= selected_option
        )

    def update_image_dropdown_options(self, options):
        self.image_option_dropdown_var.set(options[0])
        self.image_dropdown['menu'].delete(0, 'end')
        for option in options:
            self.image_dropdown['menu'].add_command(label=option, command=tk._setit(self.image_option_dropdown_var, option))
    
    def update_preprocess_options(self, selected_option):
        self.selected_option = selected_option
        # Destroy existing parameter labels and entries
        for entry in self.parameter_preprocess_entries.values():
            entry.destroy()
        for label in self.parameter_preprocess_labels.values():
            label.destroy()
        for button in self.parameter_detection_buttons:
            button.destroy()
        self.parameter_preprocess_entries.clear()
        self.parameter_preprocess_labels.clear()
        self.parameter_detection_buttons.clear()
        # # Update labels with function parameters based on selected option
        row = 3
        for param_name, param_value in self.preprocess_params[selected_option].items():
            label = tk.Label(self.detection_section_menu, text=param_name, width=15)
            label.grid(row=row, column=0, padx=5, pady=1, sticky="w")
            entry = tk.Entry(self.detection_section_menu)
            entry.grid(row=row + 1, column=0, padx=5, pady=1, sticky="w")
            entry.insert(0, str(param_value))
            self.parameter_preprocess_entries[param_name] = entry
            self.parameter_preprocess_labels[param_name] = label
            row += 2
        # Apply button
        apply_button = tk.Button(self.detection_section_menu, text="Apply", command=self.apply_preprocessing)
        apply_button.grid(row=row, column=0, padx=5, pady=5)
        self.parameter_detection_buttons.append(apply_button)

    def apply_preprocessing(self):
        if self.selected_option is None:
            return  # No option selected
        params = {}
        index = self.data_index
        focuse_widget = self.root.focus_get()
        if focuse_widget == self.data_listbox_detection:
            img = self.data_for_detection[index]['greyscale_image']
        elif focuse_widget == self.operations_listbox:
            operations_selected_index = self.operations_listbox.curselection()
            operations_index = int(operations_selected_index[0])
            img = Image.fromarray(self.data_for_detection[self.data_index]['operations'][operations_index]['processed_image'])


        result_image = None
        process_name = None

        for param_name, entry in self.parameter_preprocess_entries.items():
            try:
                params[param_name] = int(entry.get())
            except ValueError:
                params[param_name] = entry.get()
        # Apply preprocessing based on selected option and parameters
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
        operation = {
            "processed_image": result_image,
            "process_name": process_name,
            "params": params
        }
        self.data_for_detection[index]['operations'].append(operation)
        self.refresh_data_to_preprocess()
        operations_index = self.operations_listbox.size() - 1
        self.display_processed_image(operations_index, "Preprocess", "both")
        self.image_option_dropdown_var.set(self.image_show_options["Preprocess"][1])

        self.operations_listbox.focus()
        self.operations_listbox.selection_set(tk.END)
    
    def refresh_data_to_preprocess(self):
        self.operations_listbox.delete(0, tk.END)

        selected_index = self.data_index

        for item in self.data_for_detection[selected_index]['operations']:
                name = item["process_name"]
                self.operations_listbox.insert(tk.END, name)
    
    def show_data_for_preprocess(self, event):

        operations_selected_index = self.operations_listbox.curselection()
        operations_index = int(operations_selected_index[0])

        self.display_processed_image(operations_index, "Preprocess", "both")


    def display_processed_image(self, operation_index, option_section, option):
        # Clear previous data
        self.data_canvas_detection.delete("all")
        img = None

        if option_section in self.image_show_options:
            options = self.image_show_options[option_section]
            if option in options:
                # Perform operations for each option
                if option == "processed":
                    img_data = self.data_for_detection[self.data_index]['operations'][operation_index]['processed_image']
                    img = Image.fromarray(img_data)
                elif option == "original":
                    img = self.data_for_detection[self.data_index]['greyscale_image']
                elif option == "both":
                    img_data = self.data_for_detection[self.data_index]['operations'][operation_index]['processed_image']
                    processed_img = Image.fromarray(img_data)
                    original_img = self.data_for_detection[self.data_index]['greyscale_image']

                    # Concatenate the images horizontally
                    img = Image.new('RGB', (processed_img.width + original_img.width + 10, max(processed_img.height, original_img.height)))
                    img.paste(processed_img, (0, 0))
                    img.paste(original_img, (processed_img.width + 10, 0))


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
    
    def display_header_info_labels(self):
        # Clear previous header
        for widget in self.header_section_frame.winfo_children():
            widget.destroy()
        # Header info labels
        header_labels = []

        selected_index = self.data_listbox_detection.curselection()
        if selected_index:
            index = int(selected_index[0])
            file_ext = self.data_for_detection[0]['file_name'][-3:]
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
            # Create labels and grid them
            num_labels_per_row = (len(header_labels) + 2) // 3  # Distribute labels into three rows
            for i, label_text in enumerate(header_labels):
                row = i // num_labels_per_row
                column = i % num_labels_per_row
                label = tk.Label(self.header_section_frame, text=label_text)
                label.grid(row=row, column=column, padx=5, pady=2, sticky="e")

    def sigma_slider_change(self, value, param_name):
        if param_name in self.parameter_detection_labels:
            label_text = f"{param_name}: {float(value):.1f}"
            self.parameter_detection_labels[param_name].config(text=label_text)
            self.data_canvas_detection.delete("all")
            self.refresh_image_on_sigma_slider_change(value)

    def navigate_prev(self):
        current_value = self.navigation_slider.get()
        if current_value > 0:
            self.navigation_slider.set(current_value - 1)

    def navigate_next(self):
        current_value = self.navigation_slider.get()
        self.navigation_slider.set(current_value + 1)

    def update_image_from_navigation_slider(self, event):
        selected_index = self.data_listbox_detection.curselection()
        if selected_index:
            index = int(self.navigation_slider.get())
            self.display_image_detection(index - 1)

            # Update listbox selection
            self.data_listbox_detection.selection_clear(0, tk.END)
            self.data_listbox_detection.selection_set(index - 1)
            self.data_listbox_detection.see(index - 1)

            self.data_index = index - 1
            #if not self.data_for_detection[index - 1]['operations']:
            self.refresh_data_to_preprocess()
            self.resize_canvas_detection_scrollregion(event)
        self.resize_canvas_detection_scrollregion(event)

    def update_navigation_slider_range(self):
        num_items = len(self.data_listbox_detection.get(0, tk.END))
        self.navigation_slider.config(from_=1, to=num_items)

    def update_image_on_rescale_slider_change(self, event):
        selected_index = self.data_listbox_detection.curselection()
        if selected_index:
            index = int(selected_index[0])
            self.display_image_detection(index)
        selected_index = self.operations_listbox.curselection()
        if selected_index:
            opertation_index = int(selected_index[0])
            selected_option = self.image_option_dropdown_var.get()
            self.display_processed_image(opertation_index, "Preprocess", selected_option)
        self.resize_canvas_detection_scrollregion(event)

    def display_image_detection(self, index):
        # Clear previous data
        self.data_canvas_detection.delete("all")
        self.display_header_info_labels()

        # Load greyscale image
        img = self.data_for_detection[index]['greyscale_image']

        self.data_index = index

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

    def resize_canvas_detection_scrollregion(self, event):
        # Update the scroll region to cover the entire canvas
        self.data_canvas_detection.config(scrollregion=self.data_canvas_detection.bbox("all"))

    def insert_data_to_detection(self):
        self.data_for_detection.clear()
        self.data_listbox_detection.delete(0, tk.END)

        file_ext = self.data[0]['file_name'][-3:]
        for item in self.data:
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
        self.update_navigation_slider_range()

    def show_data_for_detection(self, event):
        file_ext = self.data[0]['file_name'][-3:]
        # Get the index of the selected filename
        selected_index = self.data_listbox_detection.curselection()
        if selected_index:
            index = int(selected_index[0])
            # Update navigation slider
            self.navigation_slider.set(index + 1)
            self.display_image_detection(index)
            self.refresh_data_to_preprocess()