from pptx import Presentation
from pptx.util import Inches

def position_image(pptx_file, image_path, top_in, left_in):
    """
    Adds an image to a PowerPoint slide at the specified position in inches.

    Args:
        pptx_file (str): Path to the PowerPoint file.
        image_path (str): Path to the image file.
        top_in (float): Top position of the image in inches.
        left_in (float): Left position of the image in inches.
    """

    try:
        prs = Presentation(pptx_file)
        slide = prs.slides[0]  # Assuming you want to add to the first slide

        # Calculate the top and left position in EMUs (English Metric Units)
        # 1 inch = 914400 EMUs
        top = Inches(top_in)
        left = Inches(left_in)

        # Add the image to the slide
        slide.shapes.add_picture(image_path, left, top)

        prs.save(pptx_file)
        print(f"Image added successfully to {pptx_file} at top={top_in}in, left={left_in}in")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    pptx_file = "NB case poster prep.pptx"  # Replace with your PowerPoint file name
    image_path = "my_qr_code4.png"  # Replace with your image file path
    top_in = 0.63
    left_in = 32.02

    position_image(pptx_file, image_path, top_in, left_in)