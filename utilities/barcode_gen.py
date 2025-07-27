from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from barcode import Code128
from barcode.writer import ImageWriter
from PIL import Image
import io

# Configuration
page_width, page_height = A4
margin = 5 * mm
columns = 8
rows = 7
total_stickers = columns * rows
label_width = (page_width - 2 * margin) / columns
label_height = (page_height - 2 * margin) / rows

def generate_barcode_image(data, width):
    # Remove add_checksum parameter
    barcode = Code128(data, writer=ImageWriter())
    buffer = io.BytesIO()
    barcode.write(buffer, {'module_width': 0.2, 'module_height': 10.0, 'quiet_zone': 1.0, 'font_size': 5, 'text_distance': 1})
    buffer.seek(0)
    img = Image.open(buffer)
    # Resize barcode to fit 60% of label width
    target_width = int(width * 0.6)
    w_percent = (target_width / float(img.size[0]))
    target_height = int((float(img.size[1]) * float(w_percent)))
    img = img.resize((target_width, target_height), Image.LANCZOS)
    return img

def draw_label(c, x, y, code):
    # Label content
    c.setFont("Helvetica", 6.5)
    c.drawCentredString(x + label_width / 2, y + label_height - 10, "BookNest SNN GB")

    # Barcode image
    img = generate_barcode_image(code, label_width)
    img_x = x + (label_width - img.width) / 2
    img_y = y + 5  # Leave 5pt padding from bottom

    c.drawInlineImage(img, img_x, img_y, width=img.width, height=img.height)

def create_pdf():
    c = canvas.Canvas("booknest_barcodes.pdf", pagesize=A4)
    count = 1
    for row in range(rows):
        for col in range(columns):
            if count > total_stickers:
                break
            x = margin + col * label_width
            y = page_height - margin - (row + 1) * label_height
            code = f"SGB{count:05d}"
            draw_label(c, x, y, code)
            count += 1
    c.save()
    print("PDF generated: booknest_barcodes.pdf")

create_pdf()
