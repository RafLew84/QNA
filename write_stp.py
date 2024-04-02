# -*- coding: utf-8 -*-
"""
write .stp file

@author: rlewandkow
"""

import struct
import os

def write_STP_file(
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

    output_dir = os.path.join(os.path.dirname(file_name), "ISETmap")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    output_name = os.path.join(output_dir, os.path.basename(file_name) + ".STP")

    with open(output_name, "wb") as out:
        out.write("".join(header_lines).encode())

        for i in data:
            out.write(struct.pack('d', i))