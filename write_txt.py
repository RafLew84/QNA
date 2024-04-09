# -*- coding: utf-8 -*-
"""
write .txt file

@author: rlewandkow
"""
import os

def write_txt_file(filename, l0):
    output_dir = os.path.join(os.path.dirname(filename), "l0")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    #directory = os.path.dirname(filename)
    filename_only = os.path.basename(filename)
    l0_filename = os.path.join(output_dir, f"l0_{filename_only}.txt")
    with open(l0_filename, 'a') as l0_file:
        l0_file.write(f'l0 for {filename_only}: {l0}\n')