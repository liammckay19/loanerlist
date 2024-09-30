import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import isSeq
import qrcode  # Import the qrcode library
import io
import os
import constants

def wrap_text(text, width, font, font_size, canvas_instance):
    """Wrap text to fit within a specified width when using the given font and font size."""
    canvas_instance.setFont(font, font_size)
    words = str(text).split()
    wrapped_lines = []
    line = ""

    for word in words:
        if line:
            test_line = f"{line} {word}"
        else:
            test_line = word

        if canvas_instance.stringWidth(test_line) < width:
            line = test_line
        else:
            wrapped_lines.append(line)
            line = word

    wrapped_lines.append(line)  # Add the last line
    return wrapped_lines[0] # truncate - only 1 line for description

# def calculate_row_height(row, max_width, description_font_size, make_font_size, canvas_instance):
#     """Calculate the total height needed for a row, skipping NaN values."""
#     base_height_per_line = 14  # Base height per line of text
#     make_height_per_line = 28  # Adjusted height for MAKE column with larger font
#     description_lines = wrap_text(row['DESCRIPTION'], max_width, "Helvetica", description_font_size, canvas_instance) if not pd.isna(row['DESCRIPTION']) else []
#     total_height = len(description_lines) * base_height_per_line + make_height_per_line
#     for col in row.index:
#         if col not in ['MAKE', 'DESCRIPTION'] and not pd.isna(row[col]):
#             total_height += base_height_per_line
#     return total_height

def create_pdf_equally_spaced(data):
    buffer = io.BytesIO()

    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    rows_per_page = 5
    margin_bottom = 50  # Bottom margin
    margin_top = 50  # Top margin
    row_height = (height - margin_bottom - margin_top) / rows_per_page  # Calculate row height
    description_font_size = 12  # Font size for description
    make_font_size = 24  # Font size for MAKE
    base_height_per_line = 14  # Base height per line of text
    max_width = width - 110  # Max width for text

    # Starting Y position
    start_y_position = height - margin_top
    current_row = 0

    for index, row in data.iterrows():
        # Calculate current Y position
        y_position = start_y_position - (current_row % rows_per_page) * row_height

        # Reset Y position and create a new page after every 'rows_per_page' rows
        if current_row % rows_per_page == 0 and current_row != 0:
            c.showPage()
            y_position = start_y_position

        # Drawing content for each row
        x_position = 70  # Starting X position
        # text = f"{row['MAKE']} - {row.get('PART NUMBER', '')} - {row.get('PRODUCT NAME', '')}"
        # c.drawString(x_position, y_position, text)
        c.setFont("Helvetica", make_font_size)

        circle_x = 40 # X position of the circle (60 units from the right edge)
        circle_y = y_position  # Y position of the circle (60 units from the top edge)
        circle_radius = 20  # Radius of the circle

        # Example of drawing a circle on a single page
        c.circle(circle_x, circle_y, circle_radius, stroke=1, fill=0)


        if not pd.isna(row["id"]):
            item_url = f"http://{constants.CURRENT_DOMAIN_NAME}/{row['id']}/"

            # Generate QR code for each row using the URL column
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=0,
            )
            qr.add_data(item_url)  # Assuming your DataFrame has a 'URL' column
            qr.make(fit=True)

            # Create an image from the QR Code instance
            img = qr.make_image(fill_color="black", back_color="white")
            qr_temp_path = f"/tmp/qr_{index}.bmp"  # Temporary file path for the QR code image
            img.save(qr_temp_path)

            # Draw the QR code on the PDF
            qr_size = 40  # Size of the QR code on the PDF
            qr_y_shift = 40
            c.drawImage(qr_temp_path, 20, y_position - qr_size - qr_y_shift, width=qr_size, height=qr_size)

            # delete temp QR Code image
            os.remove(f"/tmp/qr_{index}.bmp")

        if not pd.isna(row["MAKE"]):
            c.drawString(x_position, y_position, f"{row['MAKE']}")
            y_position -= make_font_size

        if not pd.isna(row['DESCRIPTION']):
            c.setFont("Helvetica", description_font_size)
            wrapped_lines = wrap_text(row['DESCRIPTION'], max_width, "Helvetica", description_font_size, c)
            # for line in wrapped_lines:
            c.drawString(x_position, y_position, wrapped_lines)
            y_position -= base_height_per_line


        c.setFont("Helvetica", 12)  # Reset font size for other columns
        for col in ['PART_NUMBER', 'PRODUCT_NAME', 'SERIAL', 'NOTE', 'SHELF', 'PRODUCT_TYPE']:
            if col in row and not pd.isna(row[col]):
                if col in ['PART NUMBER', 'PRODUCT NAME']:
                    c.setFont("Helvetica-Bold", 12)
                else:
                    c.setFont("Helvetica", 12)
                c.drawString(x_position, y_position, f"{col}: {row[col]}")
                y_position -= base_height_per_line


        # Increment row count
        current_row += 1

    c.save()
    buffer.seek(0)
    return buffer