# -*- coding: utf-8 -*-
"""
read .stp file

@author: rlewandkow
"""
import struct
import numpy as np

def read_STP_data(file_name):
    data = []
    header_info = {}

    try:
        with open(file_name, "rb") as file:
            # Skip header lines until the end of the header section
            while True:
                line = file.readline().decode().strip()
                if line == "[Header end]":
                    break
                elif ":" in line:
                    key, value = line.split(":", 1)
                    key = key.strip()
                    value = value.strip()
                    header_info[key] = value

            # Read data points
            while True:
                raw_data = file.read(8)  # Assuming double precision floating-point data
                if not raw_data:
                    break
                value = struct.unpack('d', raw_data)[0]
                data.append(value)

        # Construct dictionary with relevant information
        result = {
            "file_name": file_name,
            "header_info": header_info,
            "data": data
        }

        return result
    
    except FileNotFoundError:
        print(f"Error: File '{file_name}' not found.")
    except struct.error as e:
        print(f"Error reading file '{file_name}': {e}")
    except ValueError as e:
        print(f"Error reading file '{file_name}': {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
# Example usage:
file_name = "28933.stp"
f = read_STP_data(file_name)
print(f['header_info'])