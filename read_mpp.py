# -*- coding: utf-8 -*-
"""
read .mpp file

@author: rlewandkow
"""
import numpy as np
import struct
import re

def read_mpp_file(file_name):
    """
    Read data from an MPP file
    """
    try:
        header_info = {}
        data_frames = []
        header_length = None

        # Read header information
        with open(file_name, "rb") as file:
            current_section = None
            while True:
                line = file.readline().decode().strip()
                if line == "[Header end]":
                    break
                elif line.startswith("Image header size: "):
                    header_length = int(re.search(r'\d+', line).group())
                elif line.startswith("[") and line.endswith("]"):
                    current_section = line[1:-1]
                    header_info[current_section] = {}
                elif ":" in line and current_section:
                    key, value = line.split(":", 1)
                    key = key.strip()
                    value = value.strip()
                    header_info[current_section][key] = value

            # Extract dimensions from header
            num_columns = int(header_info.get("General Info", {}).get("Number of columns", 0))
            num_rows = int(header_info.get("General Info", {}).get("Number of rows", 0))
            num_frames = int(header_info.get("General Info", {}).get("Number of Frames", 0))

            if num_columns == 0 or num_rows == 0 or num_frames == 0:
                raise ValueError("Invalid dimensions in header.")

            for _ in range(num_frames):
                frame_data = []
                for _ in range(num_columns * num_rows):
                    raw_data = file.read(8)  # Assuming double precision floating-point data
                    if not raw_data:
                        break
                    value = struct.unpack('d', raw_data)[0]
                    frame_data.append(value)
                data_frames.append(frame_data)

        return {
            "file_name": file_name,
            "header_info": header_info,
            "data": data_frames,
            "header_length": header_length
        }
    
    except FileNotFoundError:
        raise FileNotFoundError(f"File '{file_name}' not found.")
    except ValueError as ve:
        raise ValueError(f"Error reading file '{file_name}': {ve}")
    except Exception as e:
        raise RuntimeError(f"An unexpected error occurred: {e}")

def main():
    file_name = "test_files/cut3_upper_part_of_stm_movie.mpp"
    try:
        result = read_mpp_file(file_name)
        print(result['header_length'])
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    main()