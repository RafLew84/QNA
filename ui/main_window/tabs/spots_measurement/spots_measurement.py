# -*- coding: utf-8 -*-
"""
Module for spots detection in the application.

@author
rlewandkow
"""

import os, sys

sys.path.insert(1, "/".join(os.path.realpath(__file__).split("/")[0:-2]))

import numpy as np
import cv2
from skimage.color import label2rgb
import matplotlib.pyplot as plt
from skimage import measure, morphology
from scipy.spatial import KDTree
from collections import defaultdict
from skimage import feature
import tkinter as tk
from PIL import Image, ImageTk


def label_image(img):
    labeled_image = morphology.label(img)
    regions_num = np.max(labeled_image)  # The number of distinct regions (excluding the background)
    names = ["{:03}".format(i) for i in range(1, regions_num + 1)]  # Creating label names for regions
    return labeled_image, regions_num, names

def calculate_regions(labeled_image):
    regions = measure.regionprops(labeled_image)
    return regions

def create_color_image(labeled_image):
    # Create a color map with distinct colors
    color_image = label2rgb(labeled_image, bg_label=0)
    color_image = (color_image * 255).astype(np.uint8)  # Convert to 8-bit color
    return color_image

def compute_nearest_neighbor_distances(centroids):
    tree = KDTree(centroids)
    distances, _ = tree.query(centroids, k=2)  # k=2 because the first neighbor is the point itself
    nearest_neighbor_distances = distances[:, 1]  # The second column contains the nearest neighbor distances
    return nearest_neighbor_distances

def track_spots(previous_centroids, current_centroids, threshold=5):
    tree = KDTree(previous_centroids)
    distances, indices = tree.query(current_centroids)
    matched_indices = []
    new_spots = []
    
    for i, (dist, idx) in enumerate(zip(distances, indices)):
        if dist < threshold:
            matched_indices.append((i, idx))
        else:
            new_spots.append(i)
    
    return matched_indices, new_spots

def analyze_images(images, threshold=5):
    all_regions = []
    all_centroids = []
    all_areas = []
    all_labels_num = []
    all_labels_names = []
    nearest_neighbor_distances_list = []
    # spot_tracks = defaultdict(list)
    labeled_images = []
    
    for frame_index, img in enumerate(images):
        labeled_image, labels_num, labels_names = label_image(img)
        regions = calculate_regions(labeled_image)
        labeled_images.append(labeled_image)
        all_labels_num.append(labels_num)
        all_labels_names.append(labels_names)

        all_regions.append(regions)
        
        centroids = np.array([region.centroid for region in regions])
        areas = np.array([region.area for region in regions])
        
        all_centroids.append(centroids)
        all_areas.append(areas)
        
        nearest_neighbor_distances = compute_nearest_neighbor_distances(centroids)
        nearest_neighbor_distances_list.append(nearest_neighbor_distances)
        
        # if frame_index == 0:
        #     for i, (centroid, area) in enumerate(zip(centroids, areas)):
        #         spot_tracks[i].append((frame_index, centroid, area))
        # else:
        #     previous_centroids = all_centroids[frame_index - 1]
        #     matched_indices, new_spots = track_spots(previous_centroids, centroids, threshold)
            
        #     for current_idx, prev_idx in matched_indices:
        #         spot_tracks[prev_idx].append((frame_index, centroids[current_idx], areas[current_idx]))
            
        #     max_existing_index = max(spot_tracks.keys()) if spot_tracks else -1
        #     for i, spot_idx in enumerate(new_spots):
        #         new_spot_index = max_existing_index + 1 + i
        #         spot_tracks[new_spot_index].append((frame_index, centroids[spot_idx], areas[spot_idx]))
    
    return all_centroids, all_areas, all_labels_names, nearest_neighbor_distances_list, labeled_images, all_labels_num

# def overlay_labels_on_original(original_images, labeled_images):
#     labeled_overlays = []
#     for original_image, labeled_image in zip(original_images, labeled_images):
#         overlay = original_image.copy()
#         contours = measure.find_contours(labeled_image, 0.5)
#         for contour in contours:
#             for point in contour:
#                 overlay[int(point[0]), int(point[1])] = 255  # Marking contour points as white
#         labeled_overlays.append(overlay)
#     return labeled_overlays

# def overlay_labels_on_original(original_images, labeled_images):
#     labeled_overlays = []
#     for original_image, labeled_image in zip(original_images, labeled_images):
#         overlay = original_image.copy()
        
#         # Perform Canny edge detection on the labeled image
#         edges = feature.canny(labeled_image > 0.5)  # Canny edge detector expects a binary image
        
#         # Overlay edges on the original image
#         overlay[edges] = 255  # Marking edge points as white
        
#         labeled_overlays.append(overlay)
#     return labeled_overlays

def overlay_labels_on_original(original_images, labeled_images, label_names, centroids):
    labeled_overlays = []
    for original_image, labeled_image, label_name, centroid in zip(original_images, labeled_images, label_names, centroids):
        overlay = original_image.copy()
        
        # Perform Canny edge detection on the labeled image
        edges = feature.canny(labeled_image > 0.5)  # Canny edge detector expects a binary image
        
        # Overlay edges on the original image
        overlay[edges] = 0  # Marking edge points as white

        # Ensure label_name is a string
        # label_name = str(label_name)
        
        # Convert labeled image to 8-bit single channel image for findContours
        labeled_image_8bit = (labeled_image > 0).astype(np.uint8)
        for label, center in zip(label_name, centroid):
            overlay = cv2.putText(overlay, label, (int(center[1]), int(center[0])), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (0, 0, 0), 1)
        
        # contours, _ = cv2.findContours(labeled_image_8bit, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # for i, contour in enumerate(contours):
        #     M = cv2.moments(contour)
        #     name = label_name[i]
        #     if M["m00"] != 0:
        #         cX = int(M["m10"] / M["m00"])
        #         cY = int(M["m01"] / M["m00"])
        #         overlay = cv2.putText(overlay, name, (cX, cY), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (255, 255, 255), 1)
        
        labeled_overlays.append(overlay)
    return labeled_overlays

def convert_to_tk_image(image):
    image = Image.fromarray(image)
    return ImageTk.PhotoImage(image)