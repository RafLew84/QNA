# -*- coding: utf-8 -*-
"""


@author
"""

import os
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

        # Create the second tab: Proccess Data
        self.tab2 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab2, text="Proccess Data")

        # Create the third tab: Detection
        self.tab3 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab3, text="Detection")

        # Configure grid row and column weights for rescaling
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # Configure grid row and column weights for Load Data tab
        self.load_data_tab.grid_rowconfigure(5, weight=1)
        self.load_data_tab.grid_columnconfigure(0, weight=1)
        self.load_data_tab.grid_columnconfigure(6, weight=1)

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