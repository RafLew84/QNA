# -*- coding: utf-8 -*-
"""
Functions for file proccessing

@author
"""

import os
import re
import numpy as np

from write_stp import write_STP_file
from write_txt import write_txt_file
from data_proccess import calculate_I_ISET_square, calculate_l0

def create_dir_for_mpp_frames(data_set, frame_num):
    path = data_set['file_name']

    filename = os.path.basename(path)

    output_dir = os.path.join(os.path.dirname(path), f"{filename} frames")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    frame_filename = os.path.join(output_dir, f"frame_{frame_num}")
    return frame_filename

def extract_data_from_mpp_header_for_stp_file(header_info):
    extracted_data = {}

    extracted_data["z_amplitude"] = re.search(r'[\d.]+', header_info.get("General Info", {}).get("Z Amplitude", "")).group()
    extracted_data["x_size"] = re.search(r'[\d.]+', header_info.get("Control", {}).get("X Amplitude", "")).group()
    extracted_data["y_size"] = re.search(r'[\d.]+', header_info.get("Control", {}).get("Y Amplitude", "")).group()
    extracted_data["x_offset"] = re.search(r'[\d.]+', header_info.get("Control", {}).get("X Offset", "")).group()
    extracted_data["y_offset"] = re.search(r'[\d.]+', header_info.get("Control", {}).get("Y Offset", "")).group()
    extracted_data["z_gain"] = re.search(r'[\d.]+', header_info.get("Control", {}).get("Z Gain", "")).group()

    return extracted_data

def calculate_z_amplitude_from_S94_file(z_gain, data):
    height_array = [[5.5 * pow(4, z_gain - 1) * d / 65536 for d in row] for row in data]
    max_z, min_z = max(map(max, height_array)), min(map(min, height_array))
    return max_z - min_z

def proccess_stp_files_I_ISET_map(data, ISET):
    for data_set in data:
        mapISET = calculate_I_ISET_square(data= data_set['data'], ISET= ISET)

        header_info = data_set['header_info']

        write_STP_file(
            file_name= data_set['file_name'][:-4]+"_I-ISET",
            x_points= int(header_info['Number of columns']),
            y_points= int(header_info['Number of rows']),
            z_amplitude= float(header_info['Z Amplitude'][:-3]),
            image_mode= 1,
            x_size= float(header_info['X Amplitude'][:-3]),
            y_size= float(header_info['Y Amplitude'][:-3]),
            x_offset= float(header_info['X-Offset'][:-3]),
            y_offset= float(header_info['Y-Offset'][:-3]),
            z_gain= float(header_info['Z Gain']),
            data= [i for row in mapISET for i in row]
        )

def proccess_s94_files_I_ISET_map(data, ISET):
    for data_set in data:
        mapISET = calculate_I_ISET_square(data= data_set['data'], ISET= ISET)

        header_info = data_set['header_info']

        z_amplitude = calculate_z_amplitude_from_S94_file(
            z_gain= header_info['z_gain'],
            data= data_set['data']
        )

        write_STP_file(
            file_name= data_set['file_name'][:-4]+"_I-ISET",
            x_points= header_info['x_points'],
            y_points= header_info['y_points'],
            z_amplitude= z_amplitude,
            image_mode= 1,
            x_size= header_info['x_size'],
            y_size= header_info['y_size'],
            x_offset= header_info['x_offset'],
            y_offset= header_info['y_offset'],
            z_gain= header_info['z_gain'],
            data= [i for row in mapISET for i in row]
        )

def proccess_mpp_files_I_ISET_map(data, ISET):
    for data_set in data:

        header_info = data_set['header_info']
        num_columns = int(header_info.get("General Info", {}).get("Number of columns", 0))
        num_rows = int(header_info.get("General Info", {}).get("Number of rows", 0))
        
        for i, frame in enumerate(data_set['data'], start=1):
            data_array = np.array(frame).reshape((num_rows, num_columns))
            mapISET = calculate_I_ISET_square(data= data_array, ISET= ISET)

            frame_filename = create_dir_for_mpp_frames(data_set= data_set, frame_num= i)

            extracted_header_info = extract_data_from_mpp_header_for_stp_file(header_info)

            write_STP_file(
                file_name= frame_filename,
                x_points= num_columns,
                y_points= num_rows,
                z_amplitude= float(extracted_header_info['z_amplitude']),
                image_mode= 1,
                x_size= float(extracted_header_info['x_size']),
                y_size= float(extracted_header_info['y_size']),
                x_offset= float(extracted_header_info['x_offset']),
                y_offset= float(extracted_header_info['y_offset']),
                z_gain= int(extracted_header_info['z_gain']),
                data= [i for row in mapISET for i in row]
            )

def proccess_stp_and_s94_files_l0(data, ISET):
    for data_set in data:
        mapISET = calculate_I_ISET_square(data_set['data'], ISET)
        l0 = calculate_l0(data_set['data'], mapISET.flatten())
        write_txt_file(data_set['file_name'], l0)

def proccess_mpp_files_l0(data, ISET):
    for data_set in data:
        header_info = data_set['header_info']
        num_columns = int(header_info.get("General Info", {}).get("Number of columns", 0))
        num_rows = int(header_info.get("General Info", {}).get("Number of rows", 0))
        for i, frame in enumerate(data_set['data'], start=1):
            data_array = np.array(frame).reshape((num_rows, num_columns))

            mapISET = calculate_I_ISET_square(data= data_array, ISET= ISET)
            l0 = calculate_l0(data_array, mapISET.flatten())
            write_txt_file(data_set['file_name'], l0, f"frame {i}")

def proccess_stp_and_s94_files_l0_from_I_ISET_map(data):
    for data_set in data:
        l0 = calculate_l0(data_set['data'])
        write_txt_file(data_set['file_name'], l0)

def proccess_mpp_files_l0_from_I_ISET_map(data):
    for data_set in data:
        header_info = data_set['header_info']
        num_columns = int(header_info.get("General Info", {}).get("Number of columns", 0))
        num_rows = int(header_info.get("General Info", {}).get("Number of rows", 0))
        for i, frame in enumerate(data_set['data'], start=1):
            data_array = np.array(frame).reshape((num_rows, num_columns))

            l0 = calculate_l0(data_array)
            write_txt_file(data_set['file_name'], l0, f"frame {i}")
