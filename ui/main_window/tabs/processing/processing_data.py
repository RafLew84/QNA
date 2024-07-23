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

data_for_processing = []

def clear_processing_data():
    data_for_processing.clear()

def insert_data(file_ext, item):
    data_name = []
    if file_ext.lower() == "stp" or file_ext.lower() == "s94":
        filename_only = os.path.basename(item['file_name'])
        data_name.append(filename_only)
        data_for_processing.append({
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
            data_for_processing.append({
                "file_name": item['file_name'],
                "frame_number": i,
                "header_info": item['header_info'],
                "original_data": frame,
                "greyscale_image": convert_data_to_greyscale_image(frame),
                "operations": []
                })
    return data_name 

def insert_formatted_data(file_ext, data):
    data_name = []
    if file_ext.lower() == "stp" or file_ext.lower() == "s94":
        for item in data:
            filename_only = os.path.basename(item['file_name'])
            data_for_processing.append(item)
            data_name.append(filename_only)
    elif file_ext.lower() == "mpp":
        for item in data:
            filename_only = os.path.basename(item['file_name'])
            data_for_processing.append(item)
            i = item['frame_number']
            frame_name = f"{filename_only}: frame {i}"
            data_name.append(frame_name)
    return data_name