# -*- coding: utf-8 -*-
"""
Module for shared data between tabs.

@author
rlewandkow
"""

import os, sys

sys.path.insert(1, "/".join(os.path.realpath(__file__).split("/")[0:-2]))

from data.processing.data_process import (
    convert_data_to_greyscale_image
)

def get_file_extension(data):
    file_ext = data[0]['file_name'][-3:]
    return file_ext

def get_filename_at_index(data, index):
    path = data[index]['file_name']
    filename = os.path.basename(path)
    return filename

def get_header_info_at_index(data, index):
    header_info = data[index]['header_info']
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

def get_framenumber_at_index(data, index):
    framenumber = ""
    if 'frame_number' in data[index]:
        framenumber = str(data[index]['frame_number'])
    return framenumber

def get_greyscale_image_at_index(data, index):
    img = data[index]['greyscale_image']
    return img

def get_all_operations(data, index):
    operations = [item["process_name"] for item in data[index]['operations']]
    return operations

def get_preprocessed_image_data_at_index(data, img_index, operation_index):
    img = data[img_index]['operations'][operation_index]['processed_image']
    return img

def insert_operation_at_index(data, index, operation):
    data[index]['operations'].append(operation)

