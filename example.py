import struct
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

# Function to process the PNG image and generate a detailed OBJ file
def generate_obj_from_png(png_data, obj_file_path):
    # Load PNG data into an image using PIL
    image = Image.open(io.BytesIO(png_data))
    image = image.convert('L')  # Convert to grayscale
    width, height = image.size
    image_data = np.array(image)

    # Prepare to write to .obj file
    with open(obj_file_path, 'w') as obj_file:
        # Write material reference (this is now part of the same file)
        obj_file.write("mtllib output.mtl\n")
        
        # Write group and object (optional)
        obj_file.write("g Cube\n")
        obj_file.write("o Cube_Object\n")
        
        # Write vertices
        for y in range(height):
            for x in range(width):
                z = image_data[y, x] / 255.0  # Normalize height values to [0, 1]
                obj_file.write(f"v {x:.6f} {y:.6f} {z:.6f}\n")

        # Write texture coordinates (optional, for more detailed viewing)
        for y in range(height):
            for x in range(width):
                u = x / (width - 1)
                v = y / (height - 1)
                obj_file.write(f"vt {u:.6f} {v:.6f}\n")

        # Write normals (optional, for lighting calculations)
        for _ in range(height * width):
            obj_file.write("vn 0.0000 0.0000 1.0000\n")

        # Write faces (triangles) using the vertices, texture coordinates, and normals
        for y in range(height - 1):
            for x in range(width - 1):
                v1 = y * width + x + 1
                v2 = y * width + (x + 1) + 1
                v3 = (y + 1) * width + x + 1
                v4 = (y + 1) * width + (x + 1) + 1

                # Use texture coordinates (vt) and normals (vn) in face definitions
                obj_file.write(f"f {v1}/{v1}/{v1} {v2}/{v2}/{v2} {v3}/{v3}/{v3}\n")
                obj_file.write(f"f {v2}/{v2}/{v2} {v4}/{v4}/{v4} {v3}/{v3}/{v3}\n")
        
        # Write material assignment (usemtl)
        obj_file.write("usemtl Material01\n")
        
        # Add a comment section (optional)
        obj_file.write("# This is a comment section\n")
        obj_file.write("# Generated from TOM file\n")

    print(f"OBJ file saved to {obj_file_path}")

# Function to generate a basic .mtl file for material references (all in one file)
def generate_mtl_file(obj_file_path):
    with open(obj_file_path, 'a') as obj_file:
        # Write the material information at the end of the .obj file
        obj_file.write("\n# Material definitions\n")
        obj_file.write("newmtl Material01\n")
        obj_file.write("Ka 1.0000 1.0000 1.0000\n")  # Ambient color
        obj_file.write("Kd 0.8000 0.8000 0.8000\n")  # Diffuse color
        obj_file.write("Ks 0.0000 0.0000 0.0000\n")  # Specular color
        obj_file.write("Ns 10.0000\n")  # Shininess
        obj_file.write("d 1.0000\n")  # Transparency
        obj_file.write("illum 2\n")  # Lighting model

    print("Material data added to OBJ file.")

# Main function to convert .tom to .obj
def convert_tom_to_obj(tom_file_path, obj_file_path):
    # Step 1: Extract PNG data from the TOM file
    png_data = extract_png_from_tom(tom_file_path)

    # Step 2: Generate .obj file from PNG data (heightmap)
    generate_obj_from_png(png_data, obj_file_path)

    # Step 3: Add material information to the same .obj file (MTL data)
    generate_mtl_file(obj_file_path)

# Example usage
tom_file_path = 'latesttomfile.tom'
obj_file_path = 'output.obj'
convert_tom_to_obj(tom_file_path, obj_file_path)
