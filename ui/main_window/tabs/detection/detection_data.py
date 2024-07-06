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

data_for_detection = []

def get_filename_at_index(index):
    path = data_for_detection[index]['file_name']
    filename = os.path.basename(path)
    return filename

def get_path_at_index(index):
    path = data_for_detection[index]['file_name']
    return path

def get_framenumber_at_index(index):
    framenumber = ""
    if 'frame_number' in data_for_detection[index]:
        framenumber = str(data_for_detection[index]['frame_number'])
    return framenumber

def get_header_info_at_index(index):
    header_info = data_for_detection[index]['header_info']
    return header_info

def get_greyscale_image_at_index(index):
    img = data_for_detection[index]['greyscale_image']
    return img

def get_preprocessed_image_data_at_index(img_index, operation_index):
    img = data_for_detection[img_index]['operations'][operation_index]['processed_image']
    return img

def get_all_operations(index):
    operations = [item["process_name"] for item in data_for_detection[index]['operations']]
    return operations

def get_file_extension():
    file_ext = data_for_detection[0]['file_name'][-3:]
    return file_ext

def insert_data(file_ext, item):
    data_name = []
    if file_ext.lower() == "stp" or file_ext.lower() == "s94":
        filename_only = os.path.basename(item['file_name'])
        data_name.append(filename_only)
        data_for_detection.append({
                "file_name": item['file_name'],
                "header_info": item['header_info'],
                "original_data": item['data'],
                "greyscale_image": convert_data_to_greyscale_image(item['data']),
                "operations": []
            })
    elif file_ext.lower() == "mpp":
        filename_only = os.path.basename(item['file_name'])
        for i, frame in enumerate(item['data'], start=1):
            frame_name = f"{filename_only}: frame {i}"
            data_name.append(frame_name)
            data_for_detection.append({
                "file_name": item['file_name'],
                "frame_number": i,
                "header_info": item['header_info'],
                "original_data": frame,
                "greyscale_image": convert_data_to_greyscale_image(frame),
                "operations": []
                })
    return data_name

def insert_operation_at_index(index, operation):
    data_for_detection[index]['operations'].append(operation)

def clear_detection_data():
    data_for_detection.clear()

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

def calculate_min_max_coeff_for_filters(x, y):
    min_size_coeff = 0.02
    max_size_coeff = 0.1
    min_pixels = (x * min_size_coeff) * ( min_size_coeff * y)
    max_pixels = (x * max_size_coeff) * ( max_size_coeff * y)
    return min_pixels,max_pixels