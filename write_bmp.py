# -*- coding: utf-8 -*-
"""
write .bmp file in greyscale

@author
"""

from PIL import Image

def save_bmp_from_s94(file_name, tab):
    try:
        # Create a new grayscale image
        img = Image.new('L', (len(tab[0]), len(tab)))

        # Normalize the values in tab to the range [0, 255]
        max_z = max(map(max, tab))
        min_z = min(map(min, tab))
        if max_z == min_z:
            max_z += 1
        for i in range(len(tab)):
            for j in range(len(tab[i])):
                val = int(255 * (tab[i][j] - min_z) / (max_z - min_z))
                img.putpixel((j, i), val)

        # Save the image to a file
        output_name = file_name[:-4] + ".bmp"
        img.save(output_name)
        print(f"Image saved as {output_name}")

    except Exception as e:
        print(f"An error occurred while saving the image: {e}")