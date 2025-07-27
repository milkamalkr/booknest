from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from barcode import Code128
from barcode.writer import ImageWriter
from PIL import Image
import io
import argparse

def generate_barcode(serial_number, output_file="single_barcode.pdf"):
    # Set dimensions
    barcode_width = 50 * mm
    barcode_height = 20 * mm
    
    # Create PDF canvas
    c = canvas.Canvas(output_file, pagesize=A4)
    
    # Generate barcode image
    barcode = Code128(serial_number, writer=ImageWriter())
    buffer = io.BytesIO()
    barcode.write(buffer, {
        'module_width': 0.2,
        'module_height': 10.0,
        'quiet_zone': 1.0,
        'font_size': 8,
        'text_distance': 4
    })
    buffer.seek(0)
    img = Image.open(buffer)
    
    # Calculate positioning (center of page)
    page_width, page_height = A4
    x = (page_width - barcode_width) / 2
    y = (page_height - barcode_height) / 2
    
    # Draw barcode
    c.drawInlineImage(img, x, y, width=barcode_width, height=barcode_height)
    c.save()
    print(f"Barcode generated: {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate a single barcode PDF')
    parser.add_argument('serial_number', help='Serial number for the barcode')
    parser.add_argument('--output', help='Output PDF file name', default='single_barcode.pdf')
    args = parser.parse_args()
    
    generate_barcode(args.serial_number, args.output)