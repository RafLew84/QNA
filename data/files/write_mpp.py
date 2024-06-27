# -*- coding: utf-8 -*-
"""
write .mpp file 

for some reason WSxM reads data in the wrong order

@author
"""

import os, sys

sys.path.insert(1, "/".join(os.path.realpath(__file__).split("/")[0:-2]))

import struct
import os

from read_mpp import read_mpp_file

def write_mpp_file(file_name, header_info, data_frames, header_length):
    """
    Write data to an MPP file.

    Args:
        file_name (str): The path to the MPP file.
        header_info (dict): Header information dictionary.
        data_frames (list): List of data frames.

    Raises:
        ValueError: If the header information is incomplete or invalid.
    """

    try:
        # Create directory
        output_dir = os.path.join(os.path.dirname(file_name), "ISETmap")
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        output_name = os.path.join(output_dir, os.path.basename(file_name) + ".MPP")

        # num_columns = int(header_info.get("General Info", {}).get("Number of columns", 0))
        # num_rows = int(header_info.get("General Info", {}).get("Number of rows", 0))
        # num_frames = int(header_info.get("General Info", {}).get("Number of Frames", 0))

        # Write header information
        with open(output_name, "wb") as file:
            file.write(f"WSxM file copyright UAM\nMovie Image file\nImage header size: {header_length}\n\n".encode())
            for section, content in header_info.items():
                file.write(f"[{section}]\n\n".encode())
                for key, value in content.items():
                    file.write(f"    {key}: {value}\n".encode())
                file.write("\n".encode())
            file.write("[Header end]\n".encode())

            # reversed_frames = []
            # for i, frame in enumerate(data_frames):
            #     half_col = int(num_columns / 2)
            #     first_half = []
            #     second_half = []
            #     for j, data in enumerate(frame):
            #         if j < half_col:
            #             first_half.append(data)
            #         else:
            #             second_half.append(data)
            #     reversed_frames += second_half
            #     reversed_frames += first_half

            # Write data
            for frame in data_frames:
                for i in frame:
                    file.write(struct.pack('d', i))
            
            # for data in reversed_frames:
            #     file.write(struct.pack('d', data))
            
            

    except Exception as e:
        raise RuntimeError(f"An unexpected error occurred: {e}")


def main():
    file_name = "test_files/cut_2_raw_low_part_of_stm_movie.mpp"
    try:
        result = read_mpp_file(file_name)
        write_mpp_file(file_name, result["header_info"], result["data"], result["header_length"])
    except Exception as e:
        print(f"Error: {e}")


if __name__ == '__main__':
    main()