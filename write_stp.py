# -*- coding: utf-8 -*-
"""
Write .stp file.

This module contains a function to write data to a .stp file.

@author: rlewandkow
"""

import struct
import os
import logging

logger = logging.getLogger(__name__)

def write_STP_file(
        output_dir_name,
        file_name, 
        x_points, 
        y_points, 
        z_amplitude, 
        image_mode, 
        x_size, 
        y_size, 
        x_offset, 
        y_offset, 
        z_gain, 
        data):
    
    """
    Write data to a .stp file.

    Args:
        output_dir_name (str): The name of the output directory.
        file_name (str): The name of the file.
        x_points (int): Number of columns.
        y_points (int): Number of rows.
        z_amplitude (float): Z amplitude.
        image_mode (int): Image mode (0 for Topo, 1 for Current).
        x_size (float): X size.
        y_size (float): Y size.
        x_offset (float): X offset.
        y_offset (float): Y offset.
        z_gain (float): Z gain.
        data (list or tuple): List or tuple of data points.

    Raises:
        ValueError: If any input parameter is invalid.
    """
    
    # Input validation
    if not all(isinstance(arg, (int, float)) for arg in [x_points, y_points, z_amplitude, x_size, y_size, x_offset, y_offset, z_gain]) \
            or not isinstance(image_mode, int) or not isinstance(data, (list, tuple)):
        msg = "write_STP_file: Invalid input. Check input parameter types."
        logger.error(msg)
        raise ValueError(msg)

    X_Calibration, Z_Calibration, Z_Scale_Offset = 100.0, 1.0, 0

    header_lines = [
        "WSxM file copyright Nanotec Electronica\nSxM Image file\nImage header Size: ",
        "\n\n[Control]\n\n  Signal Gain: {}\n  X Amplitude: {:.6f} nm\n  Y Amplitude: {:.6f} nm\n  Z Gain: 100.000 \n",
        "\n[General Info]\n\n  Acquisition channel: {}\n  Head type: STM\n  Image Data Type: double\n  Number of columns: {}\n  Number of rows: {}\n  X-Offset: {} nm\n  Y-Offset: {} nm\n  Z Amplitude: {} nm",
        "\n\n[Head Settings]\n\n  X Calibration: {:.6f} nm/V\n  Z Calibration: {:.6f} nm/V\n\n\n[Miscellaneous]\n\n  Z Scale Offset: {:.6f}\n  Relative Z value: No",
        "\n\n[Header end]\n"
    ]

    header_lines[1] = header_lines[1].format(z_gain, x_size, y_size, "Topo" if image_mode == 0 else "Current")
    header_lines[2] = header_lines[2].format("Topo" if image_mode == 0 else "Current", x_points, y_points, int(x_offset), int(y_offset), int(z_amplitude))
    header_lines[3] = header_lines[3].format(X_Calibration, Z_Calibration, Z_Scale_Offset)
    header_lines[0] += str(len(''.join(header_lines)) + 4)

    output_dir = os.path.join(os.path.dirname(file_name), output_dir_name)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    output_name = os.path.join(output_dir, os.path.basename(file_name) + ".STP")

    try:
        with open(output_name, "wb") as out:
            out.write("".join(header_lines).encode())

            for i in data:
                out.write(struct.pack('d', i))
    except (OSError, IOError) as e:
        error_msg = f"write_STP_file: Error occurred while writing the file: {e}"
        print(error_msg)
        logger.error(error_msg)
    except Exception as e:
        error_msg = f"write_STP_file: An unexpected error occurred: {e}"
        print(error_msg)
        logger.error(error_msg)