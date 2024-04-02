# -*- coding: utf-8 -*-
"""
read .s94 file

@author: rlewandkow
"""

""" .s94 metadata
/*
s94MetaDataDisplay: display metadata of .s94 STM image files.
(c) 2013 Gerald Gmachmeir    V0.74

s94 file:                   	c:\Test\Gerald\19708.S94
Image size [pixel]:         	256*256	Pixel
x/y scan direction swapped: 	0	(0: no swap;  1: swap of x/y scan direction)
ImageMode:                  	0	(0: topological image [nm];  1: current image [nA])
ImageNumber original:       	19708	(number of the originally recorded image)
Image size [nm]:            	  81.817 *  81.817	nm^2
OffsetX, OffsetY:           	   0.000 ,   0.000	nm^2  (x/y offset of image center)
ScanSpeed:                  	2496.865	nm/s (fast scanning direction)
Digital Bias Voltage:       	 200.000	mV
zGain:                      	3	(Gain of z-feedback circuit: 1/2/3) [5.5/22/88 nm]
Section:                    	2	(Gain of x/y scan ramp amplifiers: 1/2/3)
Scan Angle:                 	80	deg (Rotation with respect to physical x/y scan direction: 0-359 deg)

Image data:
Possible z-range:  -44.000 ... 43.979 nm  (-32768 ...32752 RAW)    (88 nm)
Actual image:       -3.459 ...  7.025 nm  ( -2576 ... 5232 RAW)
   zMax - zMin:                10.484 nm            ( 7808 RAW)    (11.9% F.S.)
   zMean:                       0.777 nm  (  2.26*256 =   578.9 RAW)
   zStdDev                      1.220 nm  (  3.55*256 =   908.7 RAW)
12 bit image:
 1 LSB (12 bit) = delta z Min = 0.0215 nm
   z-range used contains: 489 levels     8.9 bits effective

*/
"""

import struct
import numpy as np

#  Image modes
s94_image_mode = {
    "S94_TOPOGRAPHY": 0,
    "S94_CURRENT": 1,
}

# Define the format string used to read binary data from the file.
format_string = "<hhhhiffffffhhffffhh"

# The size (in bytes) of the binary data structure
number_of_bytes = struct.calcsize(format_string)

def read_s94_file(file_name):
    try:
        with open(file_name, 'rb') as file:
            # Unpack binary data using the specified format
            data = file.read(number_of_bytes)
            if len(data) != number_of_bytes:
                raise ValueError("Incomplete data read")

            x_points, y_points, Swapped, image_mode, Image_Number, x_size, y_size, x_offset, y_offset, Scan_Speed, \
                Bias_Voltage, z_gain, Section, Kp, Tn, Tv, It, Scan_Angle, z_Flag = struct.unpack(format_string, data)

            # Read image data into a NumPy array
            image_data = np.fromfile(file, dtype=np.int16, count=x_points * y_points).reshape((x_points, y_points))

            current_data = (20 * image_data) / 65536

        # Construct header information dictionary
        header_info = {
            "x_points": x_points,
            "y_points": y_points,
            "Swapped": Swapped,
            "image_mode": image_mode,
            "Image_Number": Image_Number,
            "x_size": x_size,
            "y_size": y_size,
            "x_offset": x_offset,
            "y_offset": y_offset,
            "Scan_Speed": Scan_Speed,
            "Bias_Voltage": Bias_Voltage,
            "z_gain": z_gain,
            "Section": Section,
            "Kp": Kp,
            "Tn": Tn,
            "Tv": Tv,
            "It": It,
            "Scan_Angle": Scan_Angle,
            "z_Flag": z_Flag,
        }

        # Construct dictionary with relevant information
        result = {
            "file_name": file_name,
            "header_info": header_info,
            "data": current_data
        }

        # Return dictionary
        return result

    except FileNotFoundError:
        print(f"Error: File '{file_name}' not found.")
    except struct.error as e:
        print(f"Error reading file '{file_name}': {e}")
    except ValueError as e:
        print(f"Error reading file '{file_name}': {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def calculate_z_amplitude(z_gain, data):
    height_array = [[5.5 * pow(4, z_gain - 1) * d / 65536 for d in row] for row in data]
    max_z, min_z = max(map(max, height_array)), min(map(min, height_array))
    return max_z - min_z

# # Function to read data from an S94 file and return relevant information
# def read_s94_file(file_name):
#     try:
#         with open(file_name, 'rb') as file:
#             # Unpack binary data using the specified format
#             data = file.read(number_of_bytes)
#             if len(data) != number_of_bytes:
#                 raise ValueError("Incomplete data read")

#             x_points, y_points, Swapped, image_mode, Image_Number, x_size, y_size, x_offset, y_offset, Scan_Speed, \
#                 Bias_Voltage, z_gain, Section, Kp, Tn, Tv, It, Scan_Angle, z_Flag = struct.unpack(format_string, data)

#             # Read image data into a NumPy array
#             image_data = np.fromfile(file, dtype=np.int16, count=x_points * y_points).reshape((x_points, y_points))

#         # Return relevant information along with the image data
#         return (file_name, x_points, y_points, Swapped, image_mode, Image_Number, x_size, y_size, x_offset, y_offset,
#                 Scan_Speed, Bias_Voltage, z_gain, Section, Kp, Tn, Tv, It, Scan_Angle, z_Flag, image_data)

#     except FileNotFoundError:
#         print(f"Error: File '{file_name}' not found.")
#     except struct.error as e:
#         print(f"Error reading file '{file_name}': {e}")
#     except ValueError as e:
#         print(f"Error reading file '{file_name}': {e}")
#     except Exception as e:
#         print(f"An unexpected error occurred: {e}")
        
def main():
    file_name = "test_files/28933.S94"
    f = read_s94_file(file_name)
    if f:
        print(f['data'])

if __name__ == '__main__':
    main()