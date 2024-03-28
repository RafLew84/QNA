# -*- coding: utf-8 -*-
"""


@author
"""

import os
import tkinter as tk
from tkinter import filedialog, messagebox

from read_s94 import read_s94_file

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("File Converter")

        # Entry field for folder path
        self.path_entry = tk.Entry(root, width=50)
        self.path_entry.grid(row=0, column=0, columnspan=3, padx=5, pady=5)

        # Button to browse for folder
        self.browse_button = tk.Button(root, text="Browse", command=self.browse_path)
        self.browse_button.grid(row=0, column=3, padx=5, pady=5)

        # File type selection
        self.file_type_label = tk.Label(root, text="Select File Type:")
        self.file_type_label.grid(row=1, column=0, padx=5, pady=5)

        self.file_type_var = tk.StringVar()
        self.file_type_var.set(".s94")  # Set .s94 as default
        self.file_type_dropdown = tk.OptionMenu(root, self.file_type_var, ".s94", ".mpp", ".stp", command=self.refresh_listbox)
        self.file_type_dropdown.grid(row=1, column=1, padx=5, pady=5)

        # Load button
        self.load_button = tk.Button(root, text="Load", command=self.load_files, state=tk.DISABLED)
        self.load_button.grid(row=1, column=2, padx=5, pady=5)

        # Scrollbar for listbox
        self.scrollbar = tk.Scrollbar(root, orient=tk.VERTICAL)
        self.scrollbar.grid(row=2, column=4, sticky=tk.N+tk.S, padx=(0, 5), pady=5)

        # Listbox to display files
        self.file_listbox = tk.Listbox(root, width=50, height=10, yscrollcommand=self.scrollbar.set, selectmode=tk.NONE, activestyle='none')
        self.file_listbox.grid(row=2, column=0, columnspan=4, padx=5, pady=5)
        self.scrollbar.config(command=self.file_listbox.yview)

    def browse_path(self):
        folder_path = filedialog.askdirectory(title="Select a folder")
        if folder_path:
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, folder_path)
            self.refresh_listbox()

    def refresh_listbox(self, *args):
        folder_path = self.path_entry.get()
        file_type = self.file_type_var.get().lower()  # Convert file type to lowercase
        self.file_listbox.delete(0, tk.END)
        files = [file for file in os.listdir(folder_path) if file.lower().endswith(file_type)]
        for file in files:
            self.file_listbox.insert(tk.END, file)
        self.check_file_type()

    def check_file_type(self):
        selected_type = self.file_type_var.get().lower()  # Convert selected type to lowercase
        if selected_type == ".mpp":
            self.load_button.config(state=tk.DISABLED)
        else:
            self.load_button.config(state=tk.NORMAL)

    def load_files(self):
        folder_path = self.path_entry.get()
        file_type = self.file_type_var.get().lower()  # Convert file type to lowercase
        files = [file for file in os.listdir(folder_path) if file.lower().endswith(file_type)]
        
        for file in files:
            file_path = os.path.join(folder_path, file)
            try:
                data = read_file(file_path, file_type)
                # Perform further operations with 'data'
                self.file_listbox.itemconfig(files.index(file), {'bg': 'green'})
            except Exception as e:
                self.file_listbox.itemconfig(files.index(file), {'bg': 'red'})
                print(f"Error loading file '{file}': {e}")

def read_file(file_path, file_type):
    if file_type == ".s94":
        return read_s94_file(file_path)
    elif file_type == ".stp":
        # return read_stp_file(file_path)
        pass
    elif file_type == ".mpp":
        # Different functionality for .mpp files
        pass

def main():
    root = tk.Tk()
    app = App(root)
    root.mainloop()

if __name__ == "__main__":
    main()