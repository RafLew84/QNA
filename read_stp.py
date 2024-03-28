# -*- coding: utf-8 -*-
"""
read .stp file

@author: rlewandkow
"""
import struct
import numpy as np

def read_STP_data(file_name):
    try:
        data = []
        header_info = {}

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
                
            num_columns = int(header_info.get("Number of columns", 0))
            num_rows = int(header_info.get("Number of rows", 0))

            if num_columns == 0 or num_rows == 0:
                raise ValueError("Missing or invalid 'Number of columns' or 'Number of rows' in header.")

            # Read data points
            while True:
                raw_data = file.read(8)  # Assuming double precision floating-point data
                if not raw_data:
                    break
                value = struct.unpack('d', raw_data)[0]
                data.append(value)
        
            data_array = np.array(data).reshape((num_rows, num_columns))

        # Construct dictionary with relevant information
        result = {
            "file_name": file_name,
            "header_info": header_info,
            "data": data_array
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

def main():
    file_name = "28933.stp"
    f = read_STP_data(file_name)
    if f:
        print(f['data'])

if __name__ == '__main__':
    main()