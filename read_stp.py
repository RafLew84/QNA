# -*- coding: utf-8 -*-
"""
read .stp file

@author: rlewandkow
"""
import struct
import numpy as np

import logging

logger = logging.getLogger(__name__)

def read_stp_file(file_name):
    if not isinstance(file_name, str):
        msg = "read_stp_file: Invalid input. filename must be strings."
        logger.error(msg)
        raise ValueError(msg)
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
                msg = "read_stp_file: Missing or invalid 'Number of columns' or 'Number of rows' in header."
                logger.error(msg)
                raise ValueError(msg)

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
        error_msg = f"read_stp_file: File '{file_name}' not found."
        logger.error(error_msg)
        print(error_msg)
    except struct.error as e:
        error_msg = f"read_stp_file: Error unpacking struct '{file_name}': {e}"
        logger.error(error_msg)
        print(error_msg)
    except ValueError as e:
        error_msg = f"read_stp_file: Error reading file '{file_name}': {e}"
        logger.error(error_msg)
        print(error_msg)
    except Exception as e:
        error_msg = f"read_stp_file: An unexpected error occurred: {e}"
        logger.error(error_msg)
        print(error_msg)

def main():
    file_name = "test_files/t/ISETmap/28933_I-ISET.stp"
    f = read_stp_file(file_name)
    if f:
        print("Pop")
        print(sum(sum(f['data'])))

if __name__ == '__main__':
    main()