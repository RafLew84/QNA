# -*- coding: utf-8 -*-
"""
Module for spots detection in the application.

@author
rlewandkow
"""

import os, sys

sys.path.insert(1, "/".join(os.path.realpath(__file__).split("/")[0:-2]))

from data.processing.data_process import (
    convert_data_to_greyscale_image
)

data_for_preprocessing = []

def get_file_extension():
    file_ext = data_for_preprocessing[0]['file_name'][-3:]
    return file_ext

def get_filename_at_index(index):
    path = data_for_preprocessing[index]['file_name']
    filename = os.path.basename(path)
    return filename

def get_header_info_at_index(index):
    header_info = data_for_preprocessing[index]['header_info']
    return header_info

def get_s94_labels(header_info, filename):
    return [
        f"Filename: {filename}",
        f"X Amplitude: {header_info.get('x_size', '')}",
        f"Y Amplitude: {header_info.get('y_size', '')}",
        f"Number of cols: {header_info.get('x_points', '')}",
        f"Number of rows: {header_info.get('y_points', '')}",
        f"X Offset: {header_info.get('x_offset', '')}",
        f"Y Offset: {header_info.get('y_offset', '')}",
        f"Z Gain: {header_info.get('z_gain', '')}"
    ]

def get_mpp_labels(header_info, filename, framenumber):
    return [
        f"Filename: {filename}",
        f"Frame: {framenumber}",
        f'X Amplitude: {header_info.get("Control", {}).get("X Amplitude", "")}',
        f'Y Amplitude: {header_info.get("Control", {}).get("Y Amplitude", "")}',
        f'Number of cols: {header_info.get("General Info", {}).get("Number of columns", "")}',
        f'Number of rows: {header_info.get("General Info", {}).get("Number of rows", "")}',
        f'X Offset: {header_info.get("Control", {}).get("X Offset", "")}',
        f'Y Offset: {header_info.get("Control", {}).get("Y Offset", "")}',
        f'Z Gain: {header_info.get("Control", {}).get("Z Gain", "")}'
    ]

def get_stp_labels(header_info, filename):
    return [
        f"Filename: {filename}",
        f"X Amplitude: {header_info.get('X Amplitude', '')}",
        f"Y Amplitude: {header_info.get('Y Amplitude', '')}",
        f"Z Amplitude: {header_info.get('Z Amplitude', '')}",
        f"Number of cols: {header_info.get('Number of columns', '')}",
        f"Number of rows: {header_info.get('Number of rows', '')}",
        f"X Offset: {header_info.get('X Offset', '')}",
        f"Y Offset: {header_info.get('Y Offset', '')}",
        f"Z Gain: {header_info.get('Z Gain', '')}"
    ]

def get_framenumber_at_index(index):
    framenumber = ""
    if 'frame_number' in data_for_preprocessing[index]:
        framenumber = str(data_for_preprocessing[index]['frame_number'])
    return framenumber