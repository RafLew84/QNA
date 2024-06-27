# -*- coding: utf-8 -*-
"""
Module for preprocess operations data.

@author
rlewandkow
"""

import os, sys

sys.path.insert(1, "/".join(os.path.realpath(__file__).split("/")[0:-2]))

def create_preprocess_operation(processed_img, process_name, params):
    return {
        "processed_image": processed_img,
        "process_name": process_name,
        "params": params
    }