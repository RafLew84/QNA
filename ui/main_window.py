# -*- coding: utf-8 -*-
"""


@author
"""

import os
import tkinter as tk
from tkinter import filedialog, messagebox

import data_analysis.converters

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

def show_main_window():
    root = tk.Tk()
    root.title("File Converter")

    # Entry field for file/folder path
    global path_entry  # declare path_entry as global variable
    path_entry = tk.Entry(root, width=50)
    path_entry.grid(row=0, column=0, padx=5, pady=5)

    # Checkbox to toggle file/folder mode
    global folder_var  # declare folder_var as global variable
    folder_var = tk.BooleanVar()
    folder_var.set(False)
    folder_checkbox = tk.Checkbutton(root, text="Convert folder", variable=folder_var)
    folder_checkbox.grid(row=1, column=0, columnspan=2, padx=5, pady=5)

    # Button to browse for file/folder
    browse_button = tk.Button(root, text="Browse", command=browse_path)
    browse_button.grid(row=0, column=1, padx=5, pady=5)

    # Listbox to display .s94 files
    global file_listbox  # declare file_listbox as global variable
    file_listbox = tk.Listbox(root, width=50, height=10)
    file_listbox.grid(row=3, column=0, columnspan=2, padx=5, pady=5)

    root.mainloop()

def main():
    show_main_window()

if __name__ == '__main__':
    main()