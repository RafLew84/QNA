# -*- coding: utf-8 -*-
"""
Module for spots detection in the application.

@author
rlewandkow
"""

import os, sys

sys.path.insert(1, "/".join(os.path.realpath(__file__).split("/")[0:-2]))

from data.processing.data_process import (
    create_greyscale_image
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
                "greyscale_image": create_greyscale_image(item['data']),
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
                "greyscale_image": create_greyscale_image(frame),
                "operations": []
                })
    return data_name

def insert_operation_at_index(index, operation):
    data_for_detection[index]['operations'].append(operation)

def clear_detection_data():
    data_for_detection.clear()