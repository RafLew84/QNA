# -*- coding: utf-8 -*-
"""


@author
"""

import os
import tkinter as tk
from tkinter import filedialog, messagebox

import converters

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("File Converter")

        # Entry field for folder path
        self.path_entry = tk.Entry(root, width=50)
        self.path_entry.grid(row=0, column=0, padx=5, pady=5)

        # Button to browse for folder
        self.browse_button = tk.Button(root, text="Browse", command=self.browse_path)
        self.browse_button.grid(row=0, column=1, padx=5, pady=5)

        # File type selection
        self.file_type_label = tk.Label(root, text="Select File Type:")
        self.file_type_label.grid(row=1, column=0, columnspan=2, padx=5, pady=5)

        self.file_type_var = tk.StringVar()
        self.file_type_var.set(".s94")  # Set .s94 as default
        self.file_type_dropdown = tk.OptionMenu(root, self.file_type_var, ".s94", ".mpp", ".stp")
        self.file_type_dropdown.grid(row=2, column=0, columnspan=2, padx=5, pady=5)

        # Listbox to display files
        self.file_listbox = tk.Listbox(root, width=50, height=10)
        self.file_listbox.grid(row=3, column=0, columnspan=2, padx=5, pady=5)

    def browse_path(self):
        folder_path = filedialog.askdirectory(title="Select a folder")
        if folder_path:
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, folder_path)
            self.display_files(folder_path)

    def display_files(self, folder_path):
        self.file_listbox.delete(0, tk.END)
        file_type = self.file_type_var.get()
        files = [file for file in os.listdir(folder_path) if file.lower().endswith(file_type)]
        for file in files:
            self.file_listbox.insert(tk.END, file)

def main():
    root = tk.Tk()
    app = App(root)
    root.mainloop()

if __name__ == "__main__":
    main()