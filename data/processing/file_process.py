# -*- coding: utf-8 -*-
"""
Functions for file proccessing

@author
"""

import os, sys

sys.path.insert(1, "/".join(os.path.realpath(__file__).split("/")[0:-2]))

import re
import numpy as np

from data.files.write_stp import write_STP_file
from data.files.write_txt import write_txt_file
from data.processing.data_process import calculate_I_ISET_square, calculate_l0
from data.files.read_s94 import S94_IMAGE_MODE

import logging

logger = logging.getLogger(__name__)

def create_dir_for_mpp_frames(data_set, frame_num):
    """
    Create a directory for storing frames of MPP data.

    Args:
        data_set (dict): Dictionary containing information about the data set.
        frame_num (int): Number of the frame.

    Returns:
        str: Path to the directory for the specified frame.
    """
    # Input validation
    if not isinstance(data_set, dict) or not isinstance(frame_num, int):
        error_msg = "create_dir_for_mpp_frames: Invalid input types. data_set should be a dictionary and frame_num should be an integer."
        logger.error(error_msg)
        raise TypeError(error_msg)

    if 'file_name' not in data_set or not isinstance(data_set['file_name'], str):
        error_msg = "create_dir_for_mpp_frames: Invalid data_set format. 'file_name' key should be present and should be a string."
        logger.error(error_msg)
        raise ValueError(error_msg)

    path = data_set['file_name']
    filename = os.path.basename(path)

    output_dir = os.path.join(os.path.dirname(path), f"{filename} frames")
    try:
        os.makedirs(output_dir, exist_ok=True)
    except OSError as e:
        error_msg = f"create_dir_for_mpp_frames: Failed to create directory: {output_dir}. Error: {e}"
        logger.error(error_msg)
        raise OSError(error_msg)

    frame_filename = os.path.join(output_dir, f"frame_{frame_num}")
    return frame_filename

def calculate_pixel_to_nm_coefficients(header_info, file_ext):
    if not isinstance(header_info, dict):
        error_msg = "calculate_pixel_to_nm_coefficient: Header information must be provided as a dictionary."
        logger.error(error_msg)
        raise TypeError(error_msg)
    
    x_nm = None
    y_nm = None

    x_px = None
    y_px = None
    
    try:
        x_nm, y_nm, x_px, y_px = get_image_sizes(header_info, file_ext)
        
        nm_per_pixel_x = x_nm / x_px
        nm_per_pixel_y = y_nm / y_px
            
        return nm_per_pixel_x, nm_per_pixel_y
    except KeyError as e:
        error_msg = f"Header information for file extension '{file_ext}' is missing: {e}"
        logger.error(error_msg)
        raise e
    
def calculate_pixels_from_nm(nm, coeff):
    pixels = nm / coeff
    return int(pixels)


def get_image_sizes(header_info, file_ext):
    if file_ext.lower() == "s94":
        x_nm = header_info['x_size']
        y_nm = header_info['y_size']

        x_px = header_info['x_points']
        y_px = header_info['y_points']

    elif file_ext.lower() == "stp":
        x_nm = extract_number_from_string(header_info['X Amplitude'])
        y_nm = extract_number_from_string(header_info['Y Amplitude'])

        x_px = float(header_info['Number of columns'])
        y_px = float(header_info['Number of rows'])

    elif file_ext.lower() == "mpp":
        x_nm = extract_number_from_string(header_info.get('Control', {}).get('X Amplitude', ''))
        y_nm = extract_number_from_string(header_info.get('Control', {}).get('Y Amplitude', ''))

        x_px = float(header_info.get('General Info', {}).get('Number of columns', ''))
        y_px = float(header_info.get('General Info', {}).get('Number of rows', ''))
    return x_nm,y_nm,x_px,y_px
    
def calculate_avg_nm_per_px(header_info, file_ext):
    #x_nm, y_nm, x_px, y_px = get_image_sizes(header_info, file_ext)
    x_coeff, y_coeff = calculate_pixel_to_nm_coefficients(header_info, file_ext)
    avg_nm_per_pixel = x_coeff * y_coeff

    return avg_nm_per_pixel

def extract_number_from_string(string):
    # Use regular expression to match numerical part
    match = re.search(r'(\d+\.?\d*)', string)
    if match:
        return float(match.group())  # Convert matched string to float
    else:
        return None  # Return None if no match found

def extract_data_from_mpp_header_for_stp_file(header_info):
    """
    Extract relevant data from header information obtained from an MPP file for writing to an STP file.

    Args:
        header_info (dict): Header information dictionary obtained from the MPP file.

    Returns:
        dict: Extracted data including (with unit) 'z_amplitude', 'x_size', 'y_size', 'x_offset', 'y_offset', 'z_gain'.
    """
    if not isinstance(header_info, dict):
        error_msg = "extract_data_from_mpp_header_for_stp_file: Header information must be provided as a dictionary."
        logger.error(error_msg)
        raise TypeError(error_msg)
    
    pattern = re.compile(r'[\d.]+')

    extracted_data = {}

    try:
        # Extract data from header_info using regex patterns
        extracted_data["z_amplitude"] = pattern.search(header_info.get("General Info", {}).get("Z Amplitude", "")).group()
        extracted_data["x_size"] = pattern.search(header_info.get("Control", {}).get("X Amplitude", "")).group()
        extracted_data["y_size"] = pattern.search(header_info.get("Control", {}).get("Y Amplitude", "")).group()
        extracted_data["x_offset"] = pattern.search(header_info.get("Control", {}).get("X Offset", "")).group()
        extracted_data["y_offset"] = pattern.search(header_info.get("Control", {}).get("Y Offset", "")).group()
        extracted_data["z_gain"] = pattern.search(header_info.get("Control", {}).get("Z Gain", "")).group()
    except AttributeError:
        error_msg = "extract_data_from_mpp_header_for_stp_file: Failed to extract data from header information."
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    return extracted_data

def calculate_z_amplitude_from_S94_file(z_gain, data):
    """
    Calculate the z-amplitude from data obtained from an S94 file using a given z-gain.

    Args:
        z_gain (int or float): Z-gain value.
        data (np.ndarray): Data obtained from the S94 file.

    Returns:
        float: Calculated z-amplitude.
    """
    if not isinstance(z_gain, (int, float)):
        error_msg = "calculate_z_amplitude_from_S94_file: z_gain must be a numeric value."
        logger.error(error_msg)
        raise TypeError(error_msg)
    if not isinstance(data, np.ndarray):
        error_msg = "Invalid data format. data must be a NumPy array."
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    if isinstance(data, np.ndarray):
        if data.ndim != 2:
            error_msg = "calculate_z_amplitude_from_S94_file: Invalid data format. NumPy ndarray must be 2D."
            logger.error(error_msg)
            raise ValueError(error_msg)
    else:
        if not data or not all(isinstance(row, list) for row in data):
            error_msg = "calculate_z_amplitude_from_S94_file: Invalid data format. data must be a non-empty 2D list or a NumPy ndarray."
            logger.error(error_msg)
            raise ValueError(error_msg)
    
    height_array = 5.5 * pow(4, z_gain - 1) * data / 65536
    max_z, min_z = np.max(height_array), np.min(height_array)
    return max_z - min_z

def process_stp_files_I_ISET_map(data, ISET):
    """
    Process STP files to generate I-ISET maps.

    Args:
        data (list of dict): List of dictionaries, where each dictionary contains 'data', 'header_info', and 'file_name' keys.
        ISET (int or float): Value of ISET.

    Raises:
        ValueError: If data is not provided as a list or if any dictionary in the list is missing required keys.
        ValueError: If ISET is not a numeric value.
    """

    if not isinstance(data, list):
        error_msg = "proccess_stp_files_I_ISET_map: Input data must be provided as a list."
        logger.error(error_msg)
        raise ValueError(error_msg)
    if not all(isinstance(d, dict) and 'data' in d and 'header_info' in d and 'file_name' in d for d in data):
        error_msg = "proccess_stp_files_I_ISET_map: Each element of the input data list must be a dictionary with 'data', 'header_info', and 'file_name' keys."
        logger.error(error_msg)
        raise ValueError(error_msg)
    if not isinstance(ISET, (int, float)):
        error_msg = "proccess_stp_files_I_ISET_map: ISET must be a numeric value."
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    for data_set in data:
        try:
            mapISET = calculate_I_ISET_square(data= data_set['data'], ISET= ISET)

            header_info = data_set['header_info']

            write_STP_file(
                output_dir_name="I-ISETmap",
                file_name= data_set['file_name'][:-4]+"_I-ISET",
                x_points= int(header_info['Number of columns']),
                y_points= int(header_info['Number of rows']),
                z_amplitude= float(header_info['Z Amplitude'][:-3]),
                image_mode= S94_IMAGE_MODE["S94_CURRENT"],
                x_size= float(header_info['X Amplitude'][:-3]),
                y_size= float(header_info['Y Amplitude'][:-3]),
                x_offset= float(header_info['X-Offset'][:-3]),
                y_offset= float(header_info['Y-Offset'][:-3]),
                z_gain= float(header_info['Z Gain']),
                data= [i for row in mapISET for i in row]
            )
        except Exception as e:
            error_msg = f"proccess_stp_files_I_ISET_map: Error processing data set: {data_set['file_name']}. Error: {e}"
            logger.error(error_msg)
            print(error_msg)

def convert_s94_files_to_stp(file):
    """
    Convert S94 file data to STP file format.

    Args:
        file (dict): Dictionary containing 'data', 'header_info', and 'file_name' keys.

    Raises:
        ValueError: If the input file is not provided as a dictionary or is missing required keys.
    """
    if not isinstance(file, dict) and 'data' in file and 'header_info' in file and 'file_name' in file:
        error_msg = "convert_s94_files_to_stp: Element must be a dictionary with 'data', 'header_info', and 'file_name' keys."
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    header_info = file['header_info']
    
    write_STP_file(
        output_dir_name="STP_files",
        file_name=file['file_name'][:-4],
        x_points= header_info['x_points'],
        y_points= header_info['y_points'],
        z_amplitude= calculate_z_amplitude_from_S94_file(header_info['z_gain'], file['data']),
        image_mode= header_info['image_mode'],
        x_size= header_info['x_size'],
        y_size= header_info['y_size'],
        x_offset= header_info['x_offset'],
        y_offset= header_info['y_offset'],
        z_gain= header_info['z_gain'],
        data= [i for row in file['data'] for i in row]
    )

def process_s94_files_I_ISET_map(data, ISET):
    """
    Process a list of S94 files to calculate I_ISET square and generate corresponding I-ISET maps.

    Args:
        data (list): A list of dictionaries, each containing 'data', 'header_info', and 'file_name' keys.
        ISET (int, float): The ISET value used for calculating the I_ISET square.

    Raises:
        ValueError: If input data is not provided as a list, or if ISET is not a numeric value.
    """
    if not isinstance(data, list):
        error_msg = "proccess_s94_files_I_ISET_map: Input data must be provided as a list."
        logger.error(error_msg)
        raise ValueError(error_msg)
    if not all(isinstance(d, dict) and 'data' in d and 'header_info' in d and 'file_name' in d for d in data):
        error_msg = "proccess_s94_files_I_ISET_map: Each element of the input data list must be a dictionary with 'data', 'header_info', and 'file_name' keys."
        logger.error(error_msg)
        raise ValueError(error_msg)
    if not isinstance(ISET, (int, float)):
        error_msg = "proccess_s94_files_I_ISET_map: ISET must be a numeric value."
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    for data_set in data:
        try:
            mapISET = calculate_I_ISET_square(data= data_set['data'], ISET= ISET)

            header_info = data_set['header_info']

            z_amplitude = calculate_z_amplitude_from_S94_file(
                z_gain= header_info['z_gain'],
                data= data_set['data']
            )

            write_STP_file(
                output_dir_name="I-ISETmap",
                file_name= data_set['file_name'][:-4]+"_I-ISET",
                x_points= header_info['x_points'],
                y_points= header_info['y_points'],
                z_amplitude= z_amplitude,
                image_mode= S94_IMAGE_MODE["S94_CURRENT"],
                x_size= header_info['x_size'],
                y_size= header_info['y_size'],
                x_offset= header_info['x_offset'],
                y_offset= header_info['y_offset'],
                z_gain= header_info['z_gain'],
                data= [i for row in mapISET for i in row]
            )
        except KeyError as ke:
            error_msg = f"proccess_s94_files_I_ISET_map: KeyError: {ke}. Missing key in header_info."
            logger.error(error_msg)
            print(error_msg)
        except Exception as e:
            error_msg = f"proccess_s94_files_I_ISET_map: Error processing data set: {data_set['file_name']}. Error: {e}"
            logger.error(error_msg)
            print(error_msg)

def process_mpp_files_I_ISET_map(data, ISET):
    """
    Process a list of MPP files to calculate I_ISET square and generate corresponding I-ISET maps for each frame.

    Args:
        data (list): A list of dictionaries, each containing 'data' and 'header_info' keys.
        ISET (int, float): The ISET value used for calculating the I_ISET square.

    Raises:
        ValueError: If input data is not provided as a list, or if ISET is not a numeric value.
    """
    if not isinstance(data, list):
        error_msg = "proccess_mpp_files_I_ISET_map: Input data must be provided as a list."
        logger.error(error_msg)
        raise ValueError(error_msg)
    if not all(isinstance(d, dict) and 'data' in d and 'header_info' in d for d in data):
        error_msg = "proccess_mpp_files_I_ISET_map: Each element of the input data list must be a dictionary with 'data' and 'header_info' keys."
        logger.error(error_msg)
        raise ValueError(error_msg)
    if not isinstance(ISET, (int, float)):
        error_msg = "proccess_mpp_files_I_ISET_map: ISET must be a numeric value."
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    for data_set in data:
        try:
            header_info = data_set['header_info']
            num_columns = int(header_info.get("General Info", {}).get("Number of columns", 0))
            num_rows = int(header_info.get("General Info", {}).get("Number of rows", 0))
            
            for i, frame in enumerate(data_set['data'], start=1):
                data_array = np.array(frame).reshape((num_rows, num_columns))
                mapISET = calculate_I_ISET_square(data= data_array, ISET= ISET)

                frame_filename = create_dir_for_mpp_frames(data_set= data_set, frame_num= i)

                extracted_header_info = extract_data_from_mpp_header_for_stp_file(header_info)

                write_STP_file(
                    output_dir_name= "I-ISETmap",
                    file_name= frame_filename,
                    x_points= num_columns,
                    y_points= num_rows,
                    z_amplitude= float(extracted_header_info['z_amplitude']),
                    image_mode= S94_IMAGE_MODE["S94_CURRENT"],
                    x_size= float(extracted_header_info['x_size']),
                    y_size= float(extracted_header_info['y_size']),
                    x_offset= float(extracted_header_info['x_offset']),
                    y_offset= float(extracted_header_info['y_offset']),
                    z_gain= int(extracted_header_info['z_gain']),
                    data= [i for row in mapISET for i in row]
                )
        except KeyError as ke:
            error_msg = f"proccess_mpp_files_I_ISET_map: KeyError: {ke}. Missing key in header_info."
            logger.error(error_msg)
            print(error_msg)
        except Exception as e:
            error_msg = f"proccess_mpp_files_I_ISET_map: Error processing data set: {data_set['file_name']}. Error: {e}"
            logger.error(error_msg)
            print(error_msg)

def process_stp_and_s94_files_l0(data, ISET):
    """
    Process a list of STP and S94 files to calculate l0 parameter for each file, and write it to a text file.

    Args:
        data (list): A list of dictionaries, each containing 'data' and 'file_name' keys.
        ISET (int, float): The ISET value used for calculating the I_ISET square.

    Raises:
        ValueError: If input data is not provided as a list, or if ISET is not a numeric value.
    """
    if not isinstance(data, list):
        error_msg = "process_stp_and_s94_files_l0: Input data must be provided as a list."
        logger.error(error_msg)
        raise ValueError(error_msg)
    if not all(isinstance(d, dict) and 'data' in d and 'file_name' in d for d in data):
        error_msg = "process_stp_and_s94_files_l0: Each element of the input data list must be a dictionary with 'data' and 'file_name' keys."
        logger.error(error_msg)
        raise ValueError(error_msg)
    if not isinstance(ISET, (int, float)):
        error_msg = "process_stp_and_s94_files_l0: ISET must be a numeric value."
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    for data_set in data:
        try:
            mapISET = calculate_I_ISET_square(data_set['data'], ISET)
            l0 = calculate_l0(data_set['data'], mapISET.flatten())
            write_txt_file(data_set['file_name'], l0)
        except KeyError as ke:
            error_msg = f"process_stp_and_s94_files_l0: KeyError: {ke}. Missing key in data_set."
            logger.error(error_msg)
            print(error_msg)
        except Exception as e:
            error_msg = f"process_stp_and_s94_files_l0: Error processing data set: {data_set['file_name']}. Error: {e}"
            logger.error(error_msg)
            print(error_msg)

def process_mpp_files_l0(data, ISET):
    """
    Process a list of MPP files to calculate l0 parameter for each frame, and write it to a text file.

    Args:
        data (list): A list of dictionaries, each containing 'data', 'header_info', and 'file_name' keys.
        ISET (int, float): The ISET value used for calculating the I_ISET square.

    Raises:
        ValueError: If input data is not provided as a list, or if any element of the input data list does not have the required keys.
    """
    if not isinstance(data, list):
        error_msg = "process_mpp_files_l0: Input data must be provided as a list."
        logger.error(error_msg)
        raise ValueError(error_msg)
    if not all(isinstance(d, dict) and 'data' in d and 'header_info' in d and 'file_name' in d for d in data):
        error_msg = "process_mpp_files_l0: Each element of the input data list must be a dictionary with 'data', 'header_info', and 'file_name' keys."
        logger.error(error_msg)
        raise ValueError(error_msg)
    if not isinstance(ISET, (int, float)):
        error_msg = "process_mpp_files_l0: ISET must be a numeric value."
        logger.error(error_msg)
        raise ValueError(error_msg)

    for data_set in data:
        try:
            header_info = data_set['header_info']
            num_columns = int(header_info.get("General Info", {}).get("Number of columns", 0))
            num_rows = int(header_info.get("General Info", {}).get("Number of rows", 0))
            for i, frame in enumerate(data_set['data'], start=1):
                data_array = np.array(frame).reshape((num_rows, num_columns))

                mapISET = calculate_I_ISET_square(data= data_array, ISET= ISET)
                l0 = calculate_l0(data_array, mapISET.flatten())
                write_txt_file(data_set['file_name'], l0, f"frame {i}")
        except KeyError as ke:
            error_msg = f"proccess_mpp_files_l0: KeyError: {ke}. Missing key in data_set."
            logger.error(error_msg)
            print(error_msg)
        except Exception as e:
            error_msg = f"proccess_mpp_files_l0: Error processing data set: {data_set['file_name']}. Error: {e}"
            logger.error(error_msg)
            print(error_msg)

def process_stp_and_s94_files_l0_from_I_ISET_map(data):
    """
    Calculate l0 parameter from the provided data (assuming data is I-ISET square) from .s94 or .stp files, and write it to a text file.

    Args:
        data (list): A list of dictionaries, each containing 'data' and 'file_name' keys.

    Raises:
        ValueError: If input data is not provided as a list, or if any element of the input data list does not have the required keys.
    """
    # Input validation
    if not isinstance(data, list):
        error_msg = "proccess_stp_and_s94_files_l0_from_I_ISET_map: Input data must be provided as a list."
        logger.error(error_msg)
        raise ValueError(error_msg)
    if not all(isinstance(d, dict) and 'data' in d and 'file_name' in d for d in data):
        error_msg = "proccess_stp_and_s94_files_l0_from_I_ISET_map: Each element of the input data list must be a dictionary with 'data' and 'file_name' keys."
        logger.error(error_msg)
        raise ValueError(error_msg)

    for data_set in data:
        try:
            l0 = calculate_l0(data_set['data'])
            write_txt_file(data_set['file_name'], l0)
        except KeyError as ke:
            error_msg = f"proccess_stp_and_s94_files_l0_from_I_ISET_map: KeyError: {ke}. Missing key in data_set."
            logger.error(error_msg)
            print(error_msg)
        except Exception as e:
            error_msg = f"proccess_stp_and_s94_files_l0_from_I_ISET_map: Error processing data set: {data_set['file_name']}. Error: {e}"
            logger.error(error_msg)
            print(error_msg)

def process_mpp_files_l0_from_I_ISET_map(data):
    """
    Calculate l0 parameter from the provided data (assuming data is I-ISET square) from .mpp files, and write it to a text file.

    Args:
        data (list): A list of dictionaries, each containing 'data' and 'header_info' keys.

    Raises:
        ValueError: If input data is not provided as a list, or if any element of the input data list does not have the required keys.
    """
    if not isinstance(data, list):
        error_msg = "proccess_mpp_files_l0_from_I_ISET_map: Input data must be provided as a list."
        logger.error(error_msg)
        raise ValueError(error_msg)
    if not all(isinstance(d, dict) and 'data' in d and 'header_info' in d for d in data):
        error_msg = "proccess_mpp_files_l0_from_I_ISET_map: Each element of the input data list must be a dictionary with 'data' and 'header_info' keys."
        logger.error(error_msg)
        raise ValueError(error_msg)

    for data_set in data:
        try:
            header_info = data_set['header_info']
            num_columns = int(header_info.get("General Info", {}).get("Number of columns", 0))
            num_rows = int(header_info.get("General Info", {}).get("Number of rows", 0))

            for i, frame in enumerate(data_set['data'], start=1):
                data_array = np.array(frame).reshape((num_rows, num_columns))
                l0 = calculate_l0(data_array)
                write_txt_file(data_set['file_name'], l0, f"frame {i}")

        except KeyError as ke:
            error_msg = f"proccess_mpp_files_l0_from_I_ISET_map: KeyError: {ke}. Missing key in data_set."
            logger.error(error_msg)
            print(error_msg)
        except Exception as e:
            error_msg = f"proccess_mpp_files_l0_from_I_ISET_map: Error processing data set: {data_set['file_name']}. Error: {e}"
            logger.error(error_msg)
            print(error_msg)