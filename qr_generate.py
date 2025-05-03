import io
from PIL import Image, ImageDraw, ImageFont
import segno
import os
import pandas as pd
# Helper to handle Pillow version differences for resampling
try:
    # Pillow 9.1.0 and later
    NEAREST_RESAMPLE = Image.Resampling.NEAREST
except AttributeError:
    # Older Pillow versions
    NEAREST_RESAMPLE = Image.NEAREST


def create_qr_with_title_and_text(
    data,
    title,
    text,
    font_path=None,
    qr_scale=6,             # New: Scale factor if not resizing
    qr_target_size=None,    # New: Target pixel size (width/height), overrides scale
    qr_border_thickness=4,
    title_corner_radius=10,
    qr_corner_radius=8,
    edge_margin=10,
    canvas_border_thickness=10,  # New: Thickness of the canvas border
    canvas_border_color='black'  # New: Color of the canvas border
):
    """
    Generates a QR code with options for size control, styled title/text,
    rounded borders, controlled margins, and optional canvas border.

    Args:
        data (str): Data to encode.
        title (str): Title text.
        text (str): Bottom text.
        font_path (str, optional): Path to .ttf font file. Defaults to None (PIL default).
        qr_scale (int): Scale factor for QR code generation (pixels per module).
                        Used only if qr_target_size is None. Defaults to 6.
        qr_target_size (int, optional): Desired exact size (width & height in pixels) for the
                                        QR code data area (before manual border is added).
                                        If set, overrides qr_scale and resizes the generated QR.
                                        Defaults to None. Use with caution, small sizes may become unscannable.
        qr_border_thickness (int): Thickness of the border added around the QR code. Defaults to 4.
        title_corner_radius (int): Radius for the rounded corners of the title box. Defaults to 10.
        qr_corner_radius (int): Radius for the rounded corners of the QR code's border. Defaults to 8.
        edge_margin (int): Space between the image edge and the top/bottom elements. Defaults to 10.
        canvas_border_thickness (int): Thickness of the border around the entire canvas. Defaults to 10.
        canvas_border_color (str): Color of the border around the entire canvas. Defaults to 'black'.
    """
    # --- 1. Generate Original QR Code ---
    qr_code = segno.make(data, error='h')
    out = io.BytesIO()

    # --- 1a. Determine Size: Use target_size (resizing) or scale ---
    if qr_target_size is not None:
        # Generate at a reasonably high base scale for better resize quality
        base_scale_for_resize = 10
        # Use minimal quiet zone (border=1) within segno as resizing happens before manual border
        qr_code.save(out, scale=base_scale_for_resize, kind='png', border=1)
        out.seek(0)
        img_qr_original_raw = Image.open(out).convert('RGB')
        # Resize using NEAREST to keep pixels sharp (crucial for QR codes)
        print(f"Resizing QR code data area to {qr_target_size}x{qr_target_size} pixels.")
        if qr_target_size <= 0:
             print("Warning: qr_target_size must be positive. Using original size.")
             img_qr_original = img_qr_original_raw
        else:
             img_qr_original = img_qr_original_raw.resize((qr_target_size, qr_target_size), NEAREST_RESAMPLE)

    else:
        # Generate using the specified scale directly
        print(f"Generating QR code with scale {qr_scale}.")
        # Use minimal quiet zone (border=1) within segno before adding manual border
        qr_code.save(out, scale=qr_scale, kind='png', border=1)
        out.seek(0)
        img_qr_original = Image.open(out).convert('RGB')

    # --- Get Dimensions of the (potentially resized) QR code data area ---
    qr_orig_width, qr_orig_height = img_qr_original.size
    if qr_orig_width == 0 or qr_orig_height == 0:
        raise ValueError("QR Code generation resulted in zero size. Check data or parameters.")

    # --- 1b. Add Thick Border to QR ---
    # (This section remains the same, operating on the sized img_qr_original)
    qr_border_color = 'black'
    bordered_qr_width = qr_orig_width + 2 * qr_border_thickness
    bordered_qr_height = qr_orig_height + 2 * qr_border_thickness
    img_qr_with_border_rect = Image.new('RGB', (bordered_qr_width, bordered_qr_height), qr_border_color)
    img_qr_with_border_rect.paste(img_qr_original, (qr_border_thickness, qr_border_thickness))
    img_qr_content = img_qr_with_border_rect
    qr_width = bordered_qr_width
    qr_height = bordered_qr_height

    # --- 1c. Create Rounded Mask for the QR Border ---
    # (This section remains the same)
    qr_mask = Image.new('L', (qr_width, qr_height), 0)
    mask_draw = ImageDraw.Draw(qr_mask)
    mask_draw.rounded_rectangle(
        [(0, 0), (qr_width - 1, qr_height - 1)],
        radius=qr_corner_radius,
        fill=255
    )

    # --- 2. Setup Fonts and Text ---
    # (Font loading code remains the same)
    title_text = title
    scan_text = text
    title_font_size = 24
    bottom_font_size = 20
    try:
        if font_path and os.path.exists(font_path):
            title_font = ImageFont.truetype(font_path, title_font_size)
            bottom_text_font = ImageFont.truetype(font_path, bottom_font_size)
            print(f"Using font: {font_path}")
        else:
            if font_path: print(f"Warning: Font '{font_path}' not found or invalid.")
            else: print("No font path provided.")
            print("Using PIL default font.")
            title_font = ImageFont.load_default()
            bottom_text_font = ImageFont.load_default()
            title_font_size = 10
            bottom_font_size = 10
    except IOError as e:
        print(f"Error loading font: {e}. Using PIL default font.")
        title_font = ImageFont.load_default()
        bottom_text_font = ImageFont.load_default()
        title_font_size = 10
        bottom_font_size = 10


    # --- 3. Calculate Text Dimensions ---
    # (Text dimension calculation remains the same)
    dummy_img = Image.new('RGB', (1, 1))
    dummy_draw = ImageDraw.Draw(dummy_img)
    title_bbox = dummy_draw.textbbox((0, 0), title_text, font=title_font)
    title_width = title_bbox[2] - title_bbox[0]
    title_height_f = title_font_size * 1.2
    scan_text_bbox = dummy_draw.textbbox((0, 0), scan_text, font=bottom_text_font)
    scan_text_width = scan_text_bbox[2] - scan_text_bbox[0]
    scan_text_height_f = bottom_font_size * 1.2


    # --- 4. Define Spacing ---
    # (Spacing definition remains the same)
    title_padding = 10
    space_above_qr = 10
    space_below_qr = 10


    # --- 5. Calculate Final Image Dimensions ---
    # (Height and Width calculation remains the same)
    title_box_height_f = title_height_f + 2 * title_padding
    total_height_f = (edge_margin + title_box_height_f + space_above_qr + qr_height +
                      space_below_qr + scan_text_height_f + edge_margin)
    text_based_width = max(title_width + 2 * title_padding, scan_text_width)
    content_width = max(qr_width, text_based_width)
    final_width = content_width + 2 * edge_margin

    # --- 6. Create Final Canvas with Border ---
    bordered_width = final_width + 2 * canvas_border_thickness
    bordered_height = total_height_f + 2 * canvas_border_thickness
    img_final_with_border = Image.new('RGB', (int(bordered_width), int(bordered_height)), canvas_border_color)
    img_final = Image.new('RGB', (int(final_width), int(total_height_f)), (255, 255, 255))
    img_final_with_border.paste(img_final, (canvas_border_thickness, canvas_border_thickness))
    draw = ImageDraw.Draw(img_final_with_border)

    # --- 7. Calculate Positions on Final Canvas ---
    title_box_width = title_width + 2 * title_padding
    title_box_x0 = (final_width - title_box_width) // 2 + canvas_border_thickness
    title_box_y0 = edge_margin + canvas_border_thickness
    title_box_x1 = title_box_x0 + title_box_width
    title_box_y1 = title_box_y0 + int(title_box_height_f)
    title_x = title_box_x0 + title_padding
    title_y = title_box_y0 + title_padding
    qr_x = (final_width - qr_width) // 2 + canvas_border_thickness
    qr_y = title_box_y1 + space_above_qr + canvas_border_thickness
    scan_text_x = (final_width - scan_text_width) // 2 + canvas_border_thickness
    scan_text_y = qr_y + qr_height + space_below_qr

    # --- 8. Draw Elements onto Final Canvas ---
    # draw.rounded_rectangle(
    #     [(int(title_box_x0), int(title_box_y0)), (int(title_box_x1), int(title_box_y1))],
    #     radius=title_corner_radius,
    #     fill='black'
    # )
    # draw.text((int(title_x), int(title_y)), title_text, fill='white', font=title_font)
    # img_final_with_border.paste(
    #     img_qr_content,
    #     (int(qr_x), int(qr_y)),
    #     mask=qr_mask
    # )
    # draw.text((int(scan_text_x), int(scan_text_y)), scan_text, fill='black', font=bottom_text_font)
    # return img_final_with_border
        # --- 8. Draw Elements onto Final Canvas ---

    
    # Draw only the title text
    draw.text((int(title_x), int(title_y)), title_text, fill='black', font=title_font)
    
    # Paste the QR code
    img_final_with_border.paste(
        img_qr_content,
        (int(qr_x), int(qr_y)),
        mask=qr_mask
    )
    
    # Draw the bottom text
    draw.text((int(scan_text_x), int(scan_text_y)), scan_text, fill='black', font=bottom_text_font)
    return img_final_with_border


if __name__ == "__main__":
     # Example usage (only runs when the script is executed directly)
    font_paths_to_try = [
        "/System/Library/Fonts/Supplemental/Arial.ttf", # macOS (newer)
        "/Library/Fonts/Arial.ttf",                    # macOS (older)
        "C:/Windows/Fonts/arial.ttf",                  # Windows
        "/usr/share/fonts/truetype/msttcorefonts/Arial.ttf", # Linux (if MS Core Fonts installed)
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf" # Linux (common alternative)
    ]
    found_font_path = None
    for path in font_paths_to_try:
        if os.path.exists(path):
            found_font_path = path
            break
    if not found_font_path:
        print("Could not find Arial or Liberation Sans font in common locations.")
        
    ####--- QR Code Generation ---####
    # Ensure the folder exists
    output_folder = "QR_Poster_Images"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Load the CSV file
    csv_file = "URLfanfav.csv"  # Ensure the file is in the same directory or provide the full path
    data = pd.read_csv(csv_file)

    # Iterate through each row in the CSV
    for index, row in data.iterrows():
        poster_id = row['POSTER_ID']  # Access POSTER_ID column
        fan_fav_url = row['FanFavURL']  # Access FanFavURL column

        # Generate the QR code
        qr_image = create_qr_with_title_and_text(
            data=fan_fav_url,
            title=str(poster_id),
            text="VOTE FOR ME!",
            qr_target_size=150,  # Set to None to use scale
            font_path=found_font_path,
            qr_border_thickness=5,
            qr_corner_radius=0,
            edge_margin=15,
            canvas_border_thickness=2,
            qr_scale=5
        )

        # Save the QR code image
        output_path = os.path.join(output_folder, f"{poster_id}.png")
        qr_image.save(output_path)
        print(f"Saved QR code for POSTER_ID {poster_id} to {output_path}")