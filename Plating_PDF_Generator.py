
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import textwrap

pdfmetrics.registerFont(TTFont('Helvetica-Bold', 'Helvetica-Bold.ttf'))

def draw_autoscaled_text(c, text, max_font_size, x_center, y, max_width):
    font_size = max_font_size
    c.setFont("Helvetica-Bold", font_size)
    text_width = c.stringWidth(text, "Helvetica-Bold", font_size)
    while text_width > max_width and font_size > 1:
        font_size -= 1
        c.setFont("Helvetica-Bold", font_size)
        text_width = c.stringWidth(text, "Helvetica-Bold", font_size)
    c.drawCentredString(x_center, y, text)
    return font_size

def generate_pdf(component_type, step, meal_code, placement_en, placement_es,
                 component_name, standard_weight, large_weight, filename):
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter

    max_width = width - inch  # 0.5 inch margin on each side
    x_positions = [inch * 1.5, width / 2, width - inch * 1.5]
    y = height - 0.75 * inch

    c.setFont("Helvetica-Bold", 11)
    c.drawCentredString(x_positions[0], y, "COMPONENT TYPE")
    c.drawCentredString(x_positions[1], y, "STEP")
    c.drawCentredString(x_positions[2], y, "MEAL CODE")
    y -= 12
    c.setFont("Helvetica-Bold", 9)
    c.drawCentredString(x_positions[0], y, "(TIPO DE COMPONENTE)")
    c.drawCentredString(x_positions[1], y, "(PASO)")
    c.drawCentredString(x_positions[2], y, "(CÓDIGO DE COMIDA)")
    y -= 18

    draw_autoscaled_text(c, component_type, 16, x_positions[0], y, 100)
    draw_autoscaled_text(c, step, 16, x_positions[1], y, 100)
    draw_autoscaled_text(c, meal_code, 16, x_positions[2], y, 100)
    y -= 40

    draw_autoscaled_text(c, "PLACEMENT (COLOCACIÓN)", 22, width / 2, y, max_width)
    y -= 25

    placement_text = placement_en + " | " + placement_es
    wrapped_text = textwrap.wrap(placement_text, width=90)
    c.setFont("Helvetica", 12)
    for line in wrapped_text:
        c.drawCentredString(width / 2, y, line)
        y -= 16
    y -= 10

    draw_autoscaled_text(c, "COMPONENT NAME (NOMBRE DEL COMPONENTE)", 18, width / 2, y, max_width)
    y -= 20

    draw_autoscaled_text(c, component_name, 14, width / 2, y, max_width)
    y -= 40

    draw_autoscaled_text(c, "STANDARD (SIZE)", 16, width / 2, y, max_width)
    y -= 50

    draw_autoscaled_text(c, standard_weight, 90, width / 2, y, max_width)
    y -= 100

    draw_autoscaled_text(c, "LARGE (SIZE)", 16, width / 2, y, max_width)
    y -= 50

    draw_autoscaled_text(c, large_weight, 90, width / 2, y, max_width)

    c.save()
