import os, sys

sys.path.insert(1, "/".join(os.path.realpath(__file__).split("/")[0:-2]))

# -*- coding: utf-8 -*-
"""
Read .mpp file.

This module contains a function to read data from a .mpp file.

@author: rlewandkow
"""
import numpy as np
import struct
import re
import logging

logger = logging.getLogger(__name__)

def read_mpp_file(file_name):
    """
    Read data from a .mpp file.

    Args:
        file_name (str): The path to the .mpp file.

    Returns:
        dict: A dictionary containing the file name, header information, data array, and header length.
    """
    if not isinstance(file_name, str):
        msg = "read_mpp_file: Invalid input. filename must be strings."
        logger.error(msg)
        raise ValueError(msg)
    
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
                msg = "read_mpp_file: Invalid dimensions in header."
                logger.error(msg)
                raise ValueError(msg)

            for _ in range(num_frames):
                frame_data = []
                for _ in range(num_columns * num_rows):
                    raw_data = file.read(8)  # Assuming double precision floating-point data
                    if not raw_data:
                        break
                    value = struct.unpack('d', raw_data)[0]
                    frame_data.append(value)
                data_array = np.array(frame_data).reshape((num_rows, num_columns))
                data_frames.append(data_array)

        return {
            "file_name": file_name,
            "header_info": header_info,
            "data": data_frames,
            "header_length": header_length
        }
    
    except FileNotFoundError as e:
        logger.error(f"File '{file_name}' not found: {e}")
        raise FileNotFoundError(f"File '{file_name}' not found.")
    except ValueError as ve:
        logger.error(f"Error reading file '{file_name}': {ve}")
        raise ValueError(f"Error reading file '{file_name}': {ve}")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        raise Exception(f"An unexpected error occurred: {e}")

def main():
    file_name = "test_files/cut3_upper_part_of_stm_movie.mpp"
    try:
        result = read_mpp_file(file_name)
        print(result['header_length'])
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    main()