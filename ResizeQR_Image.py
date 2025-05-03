from PIL import Image
import os

# Define the folder containing the images
folder_path = "/Users/pkimmd/QR_PPT/QR_Poster_Images"

# Define the target dimensions in inches
target_width_in = 2.3
target_height_in = 3.4

# Define the DPI (dots per inch) for resizing
dpi = 300  # Adjust this value if needed

# Calculate the target dimensions in pixels
target_width_px = int(target_width_in * dpi)
target_height_px = int(target_height_in * dpi)

# Iterate through all files in the folder
for filename in os.listdir(folder_path):
    if filename.endswith(".png"):
        file_path = os.path.join(folder_path, filename)

        # Open the image
        with Image.open(file_path) as img:
            # Resize the image
            resized_img = img.resize(
                (target_width_px, target_height_px), Image.Resampling.LANCZOS
            )

            # Overwrite the original image
            resized_img.save(file_path, dpi=(dpi, dpi))
            print(f"Resized and saved: {filename}")
