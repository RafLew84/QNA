# -*- coding: utf-8 -*-
"""


@author
"""

import os
from PIL import Image, ImageTk

import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, messagebox, Scrollbar, Text

from read_s94 import read_s94_file
from read_stp import read_stp_file
from read_mpp import read_mpp_file

from file_proccess import proccess_stp_files_I_ISET_map, proccess_s94_files_I_ISET_map
from file_proccess import proccess_mpp_files_I_ISET_map, proccess_stp_and_s94_files_l0
from file_proccess import proccess_mpp_files_l0, proccess_mpp_files_l0_from_I_ISET_map
from file_proccess import proccess_stp_and_s94_files_l0_from_I_ISET_map

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
        # Create listbox to display filenames
        self.data_listbox_detection = tk.Listbox(self.spots_detection_tab, width=20, height=10, selectmode=tk.SINGLE)
        self.data_listbox_detection.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

        # Add scrollbar for the listbox
        self.listbox_scrollbar_detection = tk.Scrollbar(self.spots_detection_tab, orient=tk.VERTICAL, command=self.data_listbox_detection.yview)
        self.listbox_scrollbar_detection.grid(row=0, column=1, sticky="ns")
        self.data_listbox_detection.config(yscrollcommand=self.listbox_scrollbar_detection.set)

        self.data_listbox_detection.bind("<<ListboxSelect>>", self.show_data_for_detection)

        # Add a canvas to display the data
        self.data_canvas_detection = tk.Canvas(self.spots_detection_tab, bg="white")
        self.data_canvas_detection.grid(row=0, column=2, padx=5, pady=5, sticky="nsew")

        # Create vertical scrollbar for the canvas
        self.vertical_scrollbar_detection = tk.Scrollbar(self.spots_detection_tab, orient=tk.VERTICAL, command=self.data_canvas_detection.yview)
        self.vertical_scrollbar_detection.grid(row=0, column=3, sticky="ns")
        self.data_canvas_detection.configure(yscrollcommand=self.vertical_scrollbar_detection.set)

        # Create horizontal scrollbar for the canvas
        self.horizontal_scrollbar_detection = tk.Scrollbar(self.spots_detection_tab, orient=tk.HORIZONTAL, command=self.data_canvas_detection.xview)
        self.horizontal_scrollbar_detection.grid(row=1, column=2, sticky="ew")
        self.data_canvas_detection.configure(xscrollcommand=self.horizontal_scrollbar_detection.set)

        # Set row and column weights
        self.spots_detection_tab.grid_rowconfigure(0, weight=1)
        self.spots_detection_tab.grid_columnconfigure(2, weight=1)

        # Scale factor label and slider
        self.scale_factor_label = tk.Label(self.spots_detection_tab, text="Scale Factor:")
        self.scale_factor_label.grid(row=2, column=1, padx=5, pady=5, sticky="e")

        self.scale_factor_var = tk.DoubleVar()
        self.scale_factor_var.set(1.0)  # Default scale factor
        self.scale_factor_slider = tk.Scale(self.spots_detection_tab, from_=1.0, to=5.0, resolution=0.1, orient=tk.HORIZONTAL, variable=self.scale_factor_var, length=200)
        self.scale_factor_slider.grid(row=2, column=2, padx=5, pady=5, sticky="ew")

        # Bind event for canvas resizing
        self.data_canvas_detection.bind("<Configure>", self.resize_canvas_detection_scrollregion)

        # Bind event for slider changes
        self.scale_factor_slider.bind("<ButtonRelease-1>", self.update_image_on_slider_change)


    def update_image_on_slider_change(self, event):
        selected_index = self.data_listbox_detection.curselection()
        if selected_index:
            index = int(selected_index[0])
            file_ext = self.data[0]['file_name'][-3:]
            if file_ext.lower() == "stp" or file_ext.lower() == "s94":
                selected_data = self.data[index]
                self.display_image_detection(selected_data)
            elif file_ext.lower() == "mpp":
                selected_name = self.data_listbox_detection.get(index)
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
                self.display_image_detection(selected_data, True)

    def display_image_detection(self, data, mpp=False):
        # Clear previous data
        self.data_canvas_detection.delete("all")
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
        self.data_listbox_detection.delete(0, tk.END)

        file_ext = self.data[0]['file_name'][-3:]
        for item in self.data:
            if file_ext.lower() == "stp" or file_ext.lower() == "s94":
                filename_only = os.path.basename(item['file_name'])
                self.data_listbox_detection.insert(tk.END, filename_only)
            elif file_ext.lower() == "mpp":
                filename_only = os.path.basename(item['file_name'])
                for i, frame in enumerate(item['data'], start=1):
                    frame_name = f"{filename_only}: frame {i}"
                    self.data_listbox_detection.insert(tk.END, frame_name)

    def show_data_for_detection(self, event):
        file_ext = self.data[0]['file_name'][-3:]
        # Get the index of the selected filename
        selected_index = self.data_listbox_detection.curselection()
        if selected_index:
            index = int(selected_index[0])
            # Get the corresponding data
            if file_ext.lower() == "stp" or file_ext.lower() == "s94":
                selected_data = self.data[index]
                self.display_image_detection(selected_data)
            elif file_ext.lower() == "mpp":
                selected_name = self.data_listbox_detection.get(index)
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
                self.display_image_detection(selected_data, True)
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