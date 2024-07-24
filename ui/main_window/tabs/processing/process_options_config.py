# -*- coding: utf-8 -*-
"""
Configuration options for proces.

@author
rlewandkow
"""

import os, sys

sys.path.insert(1, "/".join(os.path.realpath(__file__).split("/")[0:-2]))

from ui.main_window.tabs.processing.process_params_default import process_params

from ui.main_window.tabs.processing.processing_operations import (
    perform_otsu_threshold
)

options_config = {

}

process_operations = {
    "Otsu Threshold": perform_otsu_threshold
}