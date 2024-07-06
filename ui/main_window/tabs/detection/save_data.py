# -*- coding: utf-8 -*-
"""
Functions for data proccessing

@author: rlewandkow
"""

import os, sys

sys.path.insert(1, "/".join(os.path.realpath(__file__).split("/")[0:-2]))

import csv


def save_labeled_image(labeled_image, path, filename, framenumber=""):
    output_dir = os.path.join(os.path.dirname(path), "saved_data")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    if framenumber == "":
        name = filename[:-4]
    else:
        name = filename[:-4] + "_frame" + framenumber

    output_path = os.path.join(output_dir, name + ".png")
    labeled_image.save(output_path)
    return output_dir,name

def save_avg_area_to_csv(output_dir, csv_filename, avg_area):
    with open(os.path.join(output_dir, csv_filename), mode='a', newline='') as file:
        writer = csv.writer(file)
        
        # Write the average area as a header for the new column
        writer.writerow(["Average Area [nm2]"])
        
        # Write the average area value in the next row
        writer.writerow([avg_area])

def save_data_to_csv(output_dir, contours_data, csv_filename):
    fieldnames = ["name", "area [nm2]", "distance_to_nearest_neighbour [nm]", "nearest_neighbour"]

    # Create a dictionary for the header of the CSV file
    header_dict = {field: field for field in fieldnames}

    # Write the data to the CSV file
    with open(os.path.join(output_dir, csv_filename), mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        
        # Write the header
        writer.writerow(header_dict)
        
        # Write each row
        for item in contours_data:
            writer.writerow({
                "name": item["name"],
                "area [nm2]": item["area"],
                "distance_to_nearest_neighbour [nm]": item["distance_to_nearest_neighbour"],
                "nearest_neighbour": item["nearest_neighbour"]
            })