# -*- coding: utf-8 -*-
"""
write .bmp file in greyscale

@author
"""

import os
import tkinter as tk
from tkinter import filedialog, messagebox

def browse_path():
    if folder_var.get():
        folder_path = filedialog.askdirectory(title="Select a folder")
    else:
        folder_path = filedialog.askopenfilename(title="Select a file", filetypes=(("S94 files", "*.s94"), ("All files", "*.*")))
    if folder_path:
        path_entry.delete(0, tk.END)
        path_entry.insert(0, folder_path)
        if folder_var.get():
            display_s94_files(folder_path)

def display_s94_files(folder_path):
    file_listbox.delete(0, tk.END)
    s94_files = [file for file in os.listdir(folder_path) if file.lower().endswith('.s94')]
    for file in s94_files:
        file_listbox.insert(tk.END, file)

root = tk.Tk()
root.title("File Converter")

# Entry field for file/folder path
path_entry = tk.Entry(root, width=50)
path_entry.grid(row=0, column=0, padx=5, pady=5)

# Button to browse for file/folder
browse_button = tk.Button(root, text="Browse", command=browse_path)
browse_button.grid(row=0, column=1, padx=5, pady=5)

# Checkbox to toggle file/folder mode
folder_var = tk.BooleanVar()
folder_var.set(False)
folder_checkbox = tk.Checkbutton(root, text="Convert folder", variable=folder_var)
folder_checkbox.grid(row=1, column=0, columnspan=2, padx=5, pady=5)

# # Button to convert file(s)
# convert_button = tk.Button(root, text="Convert", command=None)
# convert_button.grid(row=2, column=0, columnspan=2, padx=5, pady=5)

# Listbox to display .s94 files
file_listbox = tk.Listbox(root, width=50, height=10)
file_listbox.grid(row=3, column=0, columnspan=2, padx=5, pady=5)

root.mainloop()