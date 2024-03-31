# -*- coding: utf-8 -*-
"""
read .mpp file

@author: rlewandkow
"""
import struct
import numpy as np

def read_mpp_file(file_name):
    try:
        data_frames = []
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
            num_frames = int(header_info.get("Number of Frames", 0))

            if num_columns == 0 or num_rows == 0 or num_frames == 0:
                raise ValueError("Missing or invalid 'Number of columns' or 'Number of rows' or 'Number of Frames' in header.")

            # Read data points for each frame
            # Assuming data are continous
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

        result = {
                "file_name": file_name,
                "header_info": header_info,
                "data": data_frames
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
    file_name = "test_files/cut3_upper_part_of_stm_movie.mpp"
    f = read_mpp_file(file_name)
    if f:
        print(f['header_info'])

if __name__ == '__main__':
    main()