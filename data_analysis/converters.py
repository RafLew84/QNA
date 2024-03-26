# -*- coding: utf-8 -*-
"""
convertes between filetypes

@author
"""

from data_writer.write_bmp import save_bmp_from_s94
from data_reader.read_s94 import read_s94_file

def convert_s94_to_bmp(filename):
    try:
        if filename.lower().endswith('.s94'):
            print(f"Start converting {filename}")
            output_name, x_points, y_points, Swapped, image_mode, Image_Number, x_size, y_size, x_offset, y_offset, Scan_Speed, Bias_Voltage, z_gain, Section, Kp, Tn, Tv, It, Scan_Angle, z_Flag, tab = read_s94_file(filename)
            save_bmp_from_s94(output_name, tab)
            print(f"Done converting {filename}")
        else:
            print(f"Error: '{filename}' is not a .s94 file.")
    except Exception as e:
        print(f"An error occurred during conversion of '{filename}': {e}")

def main():
    convert_s94_to_bmp("29205.S94")

if __name__ == '__main__':
    main()