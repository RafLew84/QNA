# -*- coding: utf-8 -*-
"""
config for the project

@author
"""

import logging

def setup_logging():
    # Configure logging
    logging.basicConfig(filename='error.log', level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')