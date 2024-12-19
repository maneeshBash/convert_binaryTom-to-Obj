import struct
import zlib
import io
from PIL import Image
import numpy as np

# Function to extract PNG data from TOM file
def extract_png_from_tom(tom_file_path):
    with open(tom_file_path, 'rb') as file:
        data = file.read()

    # Search for PNG header and extract PNG binary data
    png_start = data.find(b'\x89PNG\r\n\x1a\n')
    if png_start == -1:
        raise ValueError("PNG data not found in TOM file")
    
    png_end = data.find(b'IEND', png_start)
    if png_end == -1:
        raise ValueError("End of PNG data not found in TOM file")
    
    png_data = data[png_start:png_end + 4]  # Including IEND
    return png_data

# Function to process the PNG image and generate an OBJ file
def generate_obj_from_png(png_data, obj_file_path):
    # Load PNG data into an image using PIL
    image = Image.open(io.BytesIO(png_data))
    image = image.convert('L')  # Convert to grayscale
    width, height = image.size
    image_data = np.array(image)

    # Prepare to write to .obj file
    with open(obj_file_path, 'w') as obj_file:
        # Write vertices
        for y in range(height):
            for x in range(width):
                z = image_data[y, x] / 255.0  # Normalize height values to [0, 1]
                obj_file.write(f"v {x} {y} {z}\n")

        # Write faces
        for y in range(height - 1):
            for x in range(width - 1):
                # Each face is made up of 2 triangles: 1st triangle: (x, y), (x+1, y), (x, y+1), 2nd triangle: (x+1, y), (x+1, y+1), (x, y+1)
                v1 = y * width + x + 1
                v2 = y * width + (x + 1) + 1
                v3 = (y + 1) * width + x + 1
                v4 = (y + 1) * width + (x + 1) + 1
                obj_file.write(f"f {v1} {v2} {v3}\n")
                obj_file.write(f"f {v2} {v3} {v4}\n")

    print(f"OBJ file saved to {obj_file_path}")

# Main function to convert .tom to .obj
def convert_tom_to_obj(tom_file_path, obj_file_path):
    # Step 1: Extract PNG data from the TOM file
    png_data = extract_png_from_tom(tom_file_path)

    # Step 2: Generate .obj file from PNG data (heightmap)
    generate_obj_from_png(png_data, obj_file_path)

# Example usage
tom_file_path = 'latesttomfile.tom'
obj_file_path = 'output.obj'
convert_tom_to_obj(tom_file_path, obj_file_path)
