# -*- coding: utf-8 -*-
"""


@author
"""

import os
from PIL import Image, ImageTk
import numpy as np

import tkinter as tk
import tkinter.font as tkFont

from tkinter import ttk
from tkinter import filedialog, messagebox, Scrollbar, Text

from read_s94 import read_s94_file
from read_stp import read_stp_file
from read_mpp import read_mpp_file

from file_proccess import proccess_stp_files_I_ISET_map, proccess_s94_files_I_ISET_map
from file_proccess import proccess_mpp_files_I_ISET_map, proccess_stp_and_s94_files_l0
from file_proccess import proccess_mpp_files_l0, proccess_mpp_files_l0_from_I_ISET_map
from file_proccess import proccess_stp_and_s94_files_l0_from_I_ISET_map, convert_s94_files_to_stp

from data_proccess import create_greyscale_image

from img_proccess import NlMeansDenois, GaussianBlur, GaussianFilter, EdgeDetection

import logging

logger = logging.getLogger(__name__)

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("QNA Software")

        self.data = []
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

        # Create a notebook (tabbed interface)
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Create the first tab: Load Data
        self.load_data_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.load_data_tab, text="Load Data")
        self.create_load_data_tab()

        # Create the second tab: Noise Analisys
        self.noise_analisys_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.noise_analisys_tab, text="Noise Analisys")
        self.create_noise_analisys_tab()

        # # Create the third tab: Detection
        self.spots_detection_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.spots_detection_tab, text="Detection")
        self.create_spots_detection_tab()

        # Configure grid row and column weights for rescaling
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # Configure grid row and column weights for Load Data tab
        self.load_data_tab.grid_rowconfigure(5, weight=1)
        self.load_data_tab.grid_columnconfigure(0, weight=1)
        self.load_data_tab.grid_columnconfigure(6, weight=1)
    ##########################################################################################################
    #### Spots Detection Tab
    ##########################################################################################################
    def create_spots_detection_tab(self):
        # Data for analisys
        self.data_for_detection = []
        self.data_index = None
        
        # Create listbox to display filenames
        self.data_listbox_detection = tk.Listbox(self.spots_detection_tab, width=20, height=10, selectmode=tk.SINGLE)
        self.data_listbox_detection.grid(row=0, column=0, rowspan=2, padx=5, pady=5, sticky="nsew")

        # Add scrollbar for the listbox
        self.listbox_scrollbar_detection = tk.Scrollbar(self.spots_detection_tab, orient=tk.VERTICAL, command=self.data_listbox_detection.yview)
        self.listbox_scrollbar_detection.grid(row=0, column=1, rowspan=2, sticky="ns")
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
        self.detection_section_frame = ttk.Frame(self.spots_detection_tab, padding="3")
        self.detection_section_frame.grid(row=0, column=4,rowspan=2, columnspan=2, padx=5, pady=2, sticky="nsew")

        self.display_header_info_labels()
        self.display_detection_frame()

    def display_detection_frame(self):
        # Clear existing widgets in the preprocessing frame
        for widget in self.detection_section_frame.winfo_children():
            widget.destroy()
        
        # Preproccess section name label
        preproccess_section_name_label = tk.Label(self.detection_section_frame, text="Preproccess:")
        preproccess_section_name_label.grid(row=0, column=0, padx=1, pady=2, sticky="n")

        # Preprocess Dropdown menu options
        preprocessing_options = ["GaussianBlur", "Non-local Mean Denoising", "GaussianFilter"]
        detection_options = ["Canny"]

        # Show Picture Options
        self.picture_options = {
            "Preprocess": ["processed", "both", "original"]
        }

        # Create and place dropdown menu
        dropdown_var = tk.StringVar()
        dropdown_var.set(preprocessing_options[0])  # Set default option
        dropdown = tk.OptionMenu(self.detection_section_frame, dropdown_var, *preprocessing_options, command=self.update_labels)
        dropdown.config(width=10)
        dropdown.grid(row=1, column=0, padx=5, pady=1, sticky="n")

        # Create and place second dropdown menu
        self.image_option_dropdown_var = tk.StringVar()
        self.image_option_dropdown_var.set("")  # Set default option
        self.image_dropdown = tk.OptionMenu(self.detection_section_frame, self.image_option_dropdown_var, *self.picture_options["Preprocess"], command=self.update_image)
        self.image_dropdown.config(width=10)
        self.image_dropdown.grid(row=2, column=0, padx=5, pady=1, sticky="n")

        # Labels for function parameters
        self.parameter_preprocess_entries = {}
        self.parameter_preprocess_labels = {}
        row = 3
        for param_name in self.preprocess_params[preprocessing_options[0]].keys():
            label = tk.Label(self.detection_section_frame, text=param_name, width=15)
            label.grid(row=row, column=0, padx=5, pady=1, sticky="w")
            self.parameter_preprocess_labels[param_name] = label
            entry = tk.Entry(self.detection_section_frame)
            entry.grid(row=row + 1, column=0, padx=5, pady=1, sticky="w")
            entry.insert(0, str(self.preprocess_params[preprocessing_options[0]][param_name]))
            self.parameter_preprocess_entries[param_name] = entry
            row += 2

        # # Apply button
        self.apply_button = tk.Button(self.detection_section_frame, text="Apply", command=self.apply_preprocessing)
        self.apply_button.grid(row=row, column=0, padx=5, pady=5)

        # Listbox to show all operations
        self.operations_listbox = tk.Listbox(self.detection_section_frame)
        self.operations_listbox.grid(row=0, column=1,rowspan=20, padx=5, pady=5, sticky="nsew")

        self.operations_listbox.bind("<<ListboxSelect>>", self.show_data_for_preprocess)

        # Add scrollbar to the listbox
        self.scrollbar = tk.Scrollbar(self.detection_section_frame, orient="vertical", command=self.operations_listbox.yview)
        self.scrollbar.grid(row=0, column=2, rowspan=20, padx=5, pady=5, sticky="ns")
        self.operations_listbox.config(yscrollcommand=self.scrollbar.set)

        row = row + 1

        # Analysis section name label
        analisys_section_name_label = tk.Label(self.detection_section_frame, text="Detection:")
        analisys_section_name_label.grid(row=row, column=0, padx=1, pady=2, sticky="n")

        row = row + 1

        # Create and place dropdown menu for detection options
        detection_dropdown_var = tk.StringVar()
        detection_dropdown_var.set(detection_options[0])  # Set default option
        detection_dropdown = tk.OptionMenu(self.detection_section_frame, detection_dropdown_var, *detection_options, command=self.update_detection_options_labels)
        detection_dropdown.config(width=10)
        detection_dropdown.grid(row=row, column=0, padx=5, pady=1, sticky="n")

        row = row + 1

        # Create and place dropdown menu for display options
        self.image_option_dropdown_for_detection_var = tk.StringVar()
        self.image_option_dropdown_for_detection_var.set("")  # Set default option
        self.image_dropdown_for_detection = tk.OptionMenu(self.detection_section_frame, self.image_option_dropdown_for_detection_var, *self.picture_options["Preprocess"], command=self.update_image_detection)
        self.image_dropdown_for_detection.config(width=10)
        self.image_dropdown_for_detection.grid(row=row, column=0, padx=5, pady=1, sticky="n")

        row = row + 1
        # Labels for function parameters
        self.parameter_detection_entries = {}
        self.parameter_detection_labels = {}
        self.parameter_detection_sliders = {}
        for param_name, param_value in self.detection_params[detection_options[0]].items():
            if param_name == "sigma":
                # Create a slider for sigma parameter
                label_text = f"{param_name}: {param_value:.1f}"
                label = tk.Label(self.detection_section_frame, text=label_text, width=15)
                label.grid(row=row, column=0, padx=5, pady=1, sticky="w")
                slider = ttk.Scale(self.detection_section_frame, from_=0.1, to=5.0, length=100, orient="horizontal", command=lambda value=param_value, param_name=param_name: self.sigma_slider_change(value, param_name))
                slider.set(param_value)  # Set default value
                slider.grid(row=row + 1, column=0, padx=5, pady=1, sticky="w")
                self.parameter_detection_sliders[param_name] = slider
                self.parameter_detection_labels[param_name] = label
            else:
                # Create entry for other parameters
                label = tk.Label(self.detection_section_frame, text=param_name, width=15)
                label.grid(row=row, column=0, padx=5, pady=1, sticky="w")
                entry = tk.Entry(self.detection_section_frame)
                entry.grid(row=row + 1, column=0, padx=5, pady=1, sticky="w")
                entry.insert(0, str(param_value))
                self.parameter_detection_entries[param_name] = entry
                self.parameter_detection_labels[param_name] = label
            row += 2

        # Apply button for detection
        self.find_edges_button = tk.Button(self.detection_section_frame, text="Find Edges", command=self.apply_detection)
        self.find_edges_button.grid(row=row, column=0, padx=5, pady=5)

    def update_detection_options_labels(self, selected_option):
        self.selected_detection_option = selected_option
        # Destroy existing parameter labels and entries
        for entry in self.parameter_detection_entries.values():
            entry.destroy()
        for label in self.parameter_detection_labels.values():
            label.destroy()
        self.parameter_detection_entries.clear()
        self.parameter_detection_labels.clear()
        row = 11
        # # Update labels with function parameters based on selected option
        for param_name, param_value in self.detection_params[selected_option].items():
            if param_name == "sigma":
                # Create a slider for sigma parameter
                label_text = f"{param_name}: {param_value:.1f}"
                label = tk.Label(self.detection_section_frame, text=label_text, width=15)
                label.grid(row=row, column=0, padx=5, pady=1, sticky="w")
                slider = ttk.Scale(self.detection_section_frame, from_=0.1, to=5.0, length=100, orient="horizontal", command=lambda value=param_value, param_name=param_name: self.sigma_slider_change(value, param_name))
                slider.set(param_value)  # Set default value
                slider.grid(row=row + 1, column=0, padx=5, pady=1, sticky="w")
                self.parameter_detection_sliders[param_name] = slider
                self.parameter_detection_labels[param_name] = label
            else:
                # Create entry for other parameters
                label = tk.Label(self.detection_section_frame, text=param_name, width=15)
                label.grid(row=row, column=0, padx=5, pady=1, sticky="w")
                entry = tk.Entry(self.detection_section_frame)
                entry.grid(row=row + 1, column=0, padx=5, pady=1, sticky="w")
                entry.insert(0, str(param_value))
                self.parameter_detection_entries[param_name] = entry
                self.parameter_detection_labels[param_name] = label
            row += 2
        self.find_edges_button.grid_remove()
        self.find_edges_button.grid(row=row, column=0, padx=5, pady=5)

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
        self.image_option_dropdown_var.set(self.picture_options["Preprocess"][1])

        self.operations_listbox.focus()
        self.operations_listbox.selection_set(tk.END)

    def refresh_image_on_sigma_slider_change(self, sigma_value):
        # if self.selected_detection_option is None:
        #     return  # No option selected
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
            # process_name = "Canny"
            result_image = EdgeDetection(
                img=np.asanyarray(img), 
                sigma=sigma_value,
                low_threshold=None if params['low_threshold'] == 'None' else params['low_threshold'],
                high_threshold=None if params['high_threshold'] == 'None' else params['high_threshold']
                )
        # operation = {
        #     "processed_image": result_image,
        #     "process_name": process_name,
        #     "params": params,
        #     "contours": None,
        #     "labeled_image": None
        # }
        # self.data_for_detection[index]['operations'].append(operation)
        # self.refresh_data_to_detection()
        # operations_index = self.operations_listbox.size() - 1
        # self.display_edged_image(operations_index, "Preprocess", "both")
        # self.image_option_dropdown_var.set(self.picture_options["Preprocess"][1])
            
        # img_data = self.data_for_detection[self.data_index]['operations'][operation_index]['processed_image']
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

        # self.operations_listbox.focus()
        # self.operations_listbox.selection_set(tk.END)

    def display_edged_image(self, operation_index, option_section, option):
        # Clear previous data
        self.data_canvas_detection.delete("all")
        img = None

        if option_section in self.picture_options:
            options = self.picture_options[option_section]
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
    
    def update_labels(self, selected_option):
        self.selected_option = selected_option
        # Destroy existing parameter labels and entries
        for entry in self.parameter_preprocess_entries.values():
            entry.destroy()
        for label in self.parameter_preprocess_labels.values():
            label.destroy()
        self.parameter_preprocess_entries.clear()
        self.parameter_preprocess_labels.clear()
        # # Update labels with function parameters based on selected option
        row = 3
        for param_name, param_value in self.preprocess_params[selected_option].items():
            label = tk.Label(self.detection_section_frame, text=param_name, width=15)
            label.grid(row=row, column=0, padx=5, pady=1, sticky="w")
            entry = tk.Entry(self.detection_section_frame)
            entry.grid(row=row + 1, column=0, padx=5, pady=1, sticky="w")
            entry.insert(0, str(param_value))
            self.parameter_preprocess_entries[param_name] = entry
            self.parameter_preprocess_labels[param_name] = label
            row += 2
        self.apply_button.grid_remove()
        self.apply_button.grid(row=row, column=0, padx=5, pady=5)

    def apply_preprocessing(self):
        if self.selected_option is None:
            return  # No option selected
        params = {}
        # selected_index = self.data_listbox_detection.curselection()
        # index = None
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
        self.image_option_dropdown_var.set(self.picture_options["Preprocess"][1])

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

        if option_section in self.picture_options:
            options = self.picture_options[option_section]
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
    ##########################################################################################################
    #### Noise Analisys Tab
    ##########################################################################################################
    def create_noise_analisys_tab(self):
        # Create listbox to display filenames
        self.data_listbox_analisys = tk.Listbox(self.noise_analisys_tab, width=20, height=10, selectmode=tk.SINGLE)
        self.data_listbox_analisys.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        self.data_listbox_analisys.bind("<<ListboxSelect>>", self.show_data_for_analisys)

        # Add a scrollbar for the listbox
        listbox_scrollbar = tk.Scrollbar(self.noise_analisys_tab, orient=tk.VERTICAL)
        listbox_scrollbar.grid(row=0, column=1, sticky="ns")
        self.data_listbox_analisys.config(yscrollcommand=listbox_scrollbar.set)
        listbox_scrollbar.config(command=self.data_listbox_analisys.yview)

        # Add a canvas to display the data
        self.data_canvas = tk.Canvas(self.noise_analisys_tab, bg="white")
        self.data_canvas.grid(row=0, column=2, padx=5, pady=5, sticky="nsew")

        # Add vertical scrollbar
        v_scrollbar = tk.Scrollbar(self.noise_analisys_tab, orient=tk.VERTICAL, command=self.data_canvas.yview)
        v_scrollbar.grid(row=0, column=3, sticky="ns")
        self.data_canvas.configure(yscrollcommand=v_scrollbar.set)

        # Add horizontal scrollbar
        h_scrollbar = tk.Scrollbar(self.noise_analisys_tab, orient=tk.HORIZONTAL, command=self.data_canvas.xview)
        h_scrollbar.grid(row=1, column=2, sticky="ew")
        self.data_canvas.configure(xscrollcommand=h_scrollbar.set)

        # Configure row and column weights for rescaling
        self.noise_analisys_tab.grid_rowconfigure(0, weight=1)
        self.noise_analisys_tab.grid_columnconfigure(0, weight=1)
        self.noise_analisys_tab.grid_columnconfigure(2, weight=1)

        # Bind the function to handle resizing events
        self.noise_analisys_tab.bind("<Configure>", self.resize_canvas_scrollregion)

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
    ##########################################################################################################
    #### Load Data Tab
    ##########################################################################################################
    def create_load_data_tab(self):
        # Entry field for folder path
        self.path_entry = tk.Entry(self.load_data_tab, width=50)
        self.path_entry.grid(row=0, column=0, columnspan=4, padx=5, pady=5, sticky="ew")

        # Button to browse for folder
        self.browse_button = tk.Button(self.load_data_tab, text="Browse", command=self.browse_path)
        self.browse_button.grid(row=0, column=4, padx=5, pady=5)

        # File type selection
        self.file_type_label = tk.Label(self.load_data_tab, text="Select File Type:")
        self.file_type_label.grid(row=1, column=0, padx=5, pady=5)

        self.file_type_var = tk.StringVar()
        self.file_type_var.set(".s94")  # Set .s94 as default
        self.file_type_dropdown = tk.OptionMenu(self.load_data_tab, self.file_type_var, ".s94", ".mpp", ".stp", command=self.refresh_listbox)
        self.file_type_dropdown.config(width=10)  # Set the width of the dropdown
        self.file_type_dropdown.grid(row=1, column=1, columnspan=2, padx=5, pady=5)

        # Load buttons
        self.load_all_button = tk.Button(self.load_data_tab, text="Load All", command=self.load_all_files)
        self.load_all_button.grid(row=1, column=3, padx=5, pady=5)

        self.load_selected_button = tk.Button(self.load_data_tab, text="Load Selected", command=self.load_selected_files)
        self.load_selected_button.grid(row=1, column=4, padx=5, pady=5)

        # Proccess data labels
        self.iset_label = tk.Label(self.load_data_tab, text="ISET:")
        self.iset_label.grid(row=1, column=5, padx=5, pady=5, sticky="s")

        self.iset_entry = tk.Entry(self.load_data_tab, width=10)
        self.iset_entry.grid(row=1, column=6, padx=5, pady=5, sticky="ew")

        # Proccess data buttons
        self.calculate_I_ISET_button = tk.Button(self.load_data_tab, text="Calculate (I - ISET)^2", command=self.calculate_I_ISET)
        self.calculate_I_ISET_button.grid(row=1, column=7, columnspan=2, padx=5, pady=5)

        self.calculate_raw_l0_button = tk.Button(self.load_data_tab, text="Calculate l0 from raw data", command=self.calculate_raw_l0)
        self.calculate_raw_l0_button.grid(row=2, column=5,columnspan=2, padx=5, pady=5)

        self.calculate_I_ISET_l0_button = tk.Button(self.load_data_tab, text="Calculate l0 from (I - ISET)^2 map" , command=self.calculate_I_ISET_l0)
        self.calculate_I_ISET_l0_button.grid(row=2, column=7,columnspan=2, padx=5, pady=5, sticky="ew")

        # Covert button
        self.convert_s94_stp_button = tk.Button(self.load_data_tab, text="Convert", command=self.convert_s94_stp)
        self.convert_s94_stp_button.grid(row=2, column=0, padx=5, pady=5)

        # Scrollbar for listbox
        self.scrollbar = tk.Scrollbar(self.load_data_tab, orient=tk.VERTICAL)
        self.scrollbar.grid(row=5, column=4, sticky=tk.N+tk.S, padx=(0, 5), pady=5)

        # Listbox to display files
        self.file_listbox = tk.Listbox(self.load_data_tab, width=50, height=10, yscrollcommand=self.scrollbar.set, selectmode=tk.MULTIPLE, activestyle='none')
        self.file_listbox.grid(row=5, column=0, columnspan=4, padx=5, pady=5, sticky="nsew")
        self.scrollbar.config(command=self.file_listbox.yview)

        # Loaded files text box with scrollbar
        self.loaded_files_text = Text(self.load_data_tab, width=50, height=10)
        self.loaded_files_text.grid(row=5, column=5, columnspan=4, padx=5, pady=5, sticky="nsew")
        self.loaded_files_scrollbar = Scrollbar(self.load_data_tab, orient=tk.VERTICAL, command=self.loaded_files_text.yview)
        self.loaded_files_text.config(yscrollcommand=self.loaded_files_scrollbar.set)
        self.loaded_files_scrollbar.grid(row=5, column=9, sticky=tk.N+tk.S, padx=(0, 5), pady=5)

    def browse_path(self):
        try:
            folder_path = filedialog.askdirectory(title="Select a folder")
            if folder_path:
                self.path_entry.delete(0, tk.END)
                self.path_entry.insert(0, folder_path)
                self.refresh_listbox()
        except Exception as e:
            error_msg = "browse_path: An error occurred while browsing for a folder:", str(e)
            logger.error(error_msg)
            messagebox.showerror(error_msg)

    def refresh_listbox(self, *args):
        folder_path = self.path_entry.get()
        file_type = self.file_type_var.get().lower()  # Convert file type to lowercase
        self.file_listbox.delete(0, tk.END)
        files = [file for file in os.listdir(folder_path) if file.lower().endswith(file_type)]
        for file in files:
            self.file_listbox.insert(tk.END, file)

    def convert_s94_stp(self):
        try:
            folder_path = self.path_entry.get()
            if not os.path.isdir(folder_path):
                error_msg = "load_all_files: Invalid folder path"
                logger.error(error_msg)
                raise ValueError(error_msg)
            files = []
            file_type = self.file_type_var.get().lower()  # Convert file type to lowercase
            if file_type == ".s94":
                files = [file for file in os.listdir(folder_path) if file.lower().endswith(file_type)]
                for file in files:
                    file_path = os.path.join(folder_path, file)
                    #self.data.append(read_file(file_path, file_type))
                    f = read_file(file_path, file_type)
                    convert_s94_files_to_stp(f)
            else:
                messagebox.showinfo("Wrong file type", "Use only with s94 files")
            messagebox.showinfo("Done", "Proccessing s94 files complete.")
            
        except Exception as e:
            error_msg = "Error", f"convert: An error occurred while refreshing the listbox: {str(e)}"
            logger.error(error_msg)
            messagebox.showerror(error_msg)

    def load_all_files(self):
        try:
            # Clear loaded files before loading new ones
            self.loaded_files_text.delete('1.0', tk.END)
            self.data.clear()
            
            folder_path = self.path_entry.get()
            if not os.path.isdir(folder_path):
                error_msg = "load_all_files: Invalid folder path"
                logger.error(error_msg)
                raise ValueError(error_msg)
            
            file_type = self.file_type_var.get().lower()  # Convert file type to lowercase
            files = [file for file in os.listdir(folder_path) if file.lower().endswith(file_type)]

            loaded_files = self.load_files(files, folder_path, file_type)

            self.loaded_files_text.insert(tk.END, "\n".join(loaded_files))
            self.insert_data_to_analisys()
            self.insert_data_to_detection()
            
        except Exception as e:
            error_msg = "Error", f"load_all_files: An error occurred while refreshing the listbox: {str(e)}"
            logger.error(error_msg)
            messagebox.showerror(error_msg)
            

    def load_selected_files(self):
        try:
            # Clear loaded files before loading new ones
            self.loaded_files_text.delete('1.0', tk.END)
            self.data.clear()
            
            selected_indices = self.file_listbox.curselection()
            if not selected_indices:
                messagebox.showerror("Error", "No files selected.")
                return

            folder_path = self.path_entry.get()
            if not os.path.isdir(folder_path):
                    error_msg = "load_all_files: Invalid folder path"
                    logger.error(error_msg)
                    raise ValueError(error_msg)
            
            file_type = self.file_type_var.get().lower()  # Convert file type to lowercase
            selected_files = [self.file_listbox.get(idx) for idx in selected_indices]

            loaded_files = self.load_files(selected_files, folder_path, file_type)

            self.loaded_files_text.insert(tk.END, "\n".join(loaded_files))
            self.insert_data_to_analisys()
            self.insert_data_to_detection()
        except Exception as e:
            error_msg = "load_selected_files: Error", f"An error occurred while loading selected files: {str(e)}"
            logger.error(error_msg)
            messagebox.showerror(error_msg)
            
    
    def load_files(self, files, folder_path, file_type):
        loaded_files = []
        for file in files:
            file_path = os.path.join(folder_path, file)
            try:
                self.data.append(read_file(file_path, file_type))
                loaded_files.append(file)
            except Exception as e:
                error_msg = f"load_files: Error loading file '{file}': {e}"
                logger.error(error_msg)
                print(error_msg)
        return loaded_files

    def calculate_I_ISET(self):
        try:
            # Extract extension
            file_ext = self.data[0]['file_name'][-3:]
        except IndexError:
            messagebox.showerror("Error", "No files selected")
            return
        try:
            ISET = float(self.iset_entry.get())  # Read the value of ISET from the iset_entry widget
        except ValueError:
            messagebox.showerror("Error", "Invalid value for ISET.")
            return
        if file_ext.lower() == "stp":
            proccess_stp_files_I_ISET_map(self.data, ISET)
            messagebox.showinfo("Done", "Processing STP files complete.")
        elif file_ext.lower() == "s94":
            proccess_s94_files_I_ISET_map(self.data, ISET)
            messagebox.showinfo("Done", "Processing S94 files complete.")
        elif file_ext.lower() == "mpp":
            proccess_mpp_files_I_ISET_map(self.data, ISET)
            messagebox.showinfo("Done", "Processing MPP files complete.")
    
    def calculate_raw_l0(self):
        try:
            # Extract extension
            file_ext = self.data[0]['file_name'][-3:]
        except IndexError:
            messagebox.showerror("Error", "No files selected")
            return
        try:
            ISET = float(self.iset_entry.get())  # Read the value of ISET from the iset_entry widget
        except ValueError:
            messagebox.showerror("Error", "Invalid value for ISET.")
            return
        if file_ext.lower() == "stp":
            proccess_stp_and_s94_files_l0(self.data, ISET)
            messagebox.showinfo("Done", "Processing STP files complete.")
        elif file_ext.lower() == "s94":
            proccess_stp_and_s94_files_l0(self.data, ISET)
            messagebox.showinfo("Done", "Processing S94 files complete.")
        elif file_ext.lower() == "mpp":
            proccess_mpp_files_l0(self.data, ISET)
            messagebox.showinfo("Done", "Processing MPP files complete.")

    def calculate_I_ISET_l0(self):
        try:
            # Extract extension
            file_ext = self.data[0]['file_name'][-3:]
        except IndexError:
            messagebox.showerror("Error", "No files selected")
            return
        if file_ext.lower() == "stp":
            proccess_stp_and_s94_files_l0_from_I_ISET_map(self.data)
            messagebox.showinfo("Done", "Processing STP files complete.")
        elif file_ext.lower() == "s94":
            proccess_stp_and_s94_files_l0_from_I_ISET_map(self.data)
            messagebox.showinfo("Done", "Processing S94 files complete.")
        elif file_ext.lower() == "mpp":
            proccess_mpp_files_l0_from_I_ISET_map(self.data)
            messagebox.showinfo("Done", "Processing MPP files complete.")

def read_file(file_path, file_type):
    if file_type == ".s94":
        return read_s94_file(file_path)
    elif file_type == ".stp":
        return read_stp_file(file_path)
    elif file_type == ".mpp":
        return read_mpp_file(file_path)

def main():
    root = tk.Tk()
    app = App(root)
    root.mainloop()

if __name__ == "__main__":
    main()