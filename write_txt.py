# -*- coding: utf-8 -*-
"""
write .txt file

@author: rlewandkow
"""
import os
import logging

logger = logging.getLogger(__name__)

def write_txt_file(filename, l0, frame_name = None):
    if not isinstance(filename, str) or (frame_name and not isinstance(frame_name, str)):
        msg = "write_txt_file: Invalid input. filename, and frame_name (if provided) must be strings."
        logger.error(msg)
        raise ValueError(msg)
    
    if not isinstance(l0, float):
        msg = "write_txt_file: Invalid input. l0 should be of type float"
        logger.error(msg)
        raise ValueError(msg)

    try:
        output_dir = os.path.join(os.path.dirname(filename), "l0")
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        filename_only = os.path.basename(filename)
        l0_filename = os.path.join(output_dir, f"l0_{filename_only}.txt")
        with open(l0_filename, 'a') as l0_file:
            if frame_name is None:
                l0_file.write(f'l0 for {filename_only}: {l0}\n')
            else:
                l0_file.write(f'l0 for {filename_only} {frame_name}: {l0}\n')
    except FileNotFoundError as e:
        error_msg = f"write_txt_file: Error: {e}. The specified file or directory does not exist."
        print(error_msg)
        logger.error(error_msg)
    except PermissionError as e:
        error_msg = f"write_txt_file: Error: {e}. Permission denied while trying to write the file."
        print(error_msg)
        logger.error(error_msg)
    except Exception as e:
        error_msg = f"write_txt_file: An unexpected error occurred: {e}"
        print(error_msg)
        logger.error(error_msg)