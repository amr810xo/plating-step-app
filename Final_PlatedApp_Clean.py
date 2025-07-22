import streamlit as st
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
import textwrap

st.set_page_config(page_title="Multi-Step Plating PDF Generator", layout="centered")
st.title("Multi-Step Plating PDF Generator")

meal_name = st.text_input("Meal Name (used for file name only)", key="meal_name")
component_type = st.text_input("Component Type")
step = st.text_input("Step")
meal_code = st.text_input("Meal Code")
placement_en = st.text_area("Placement (English)")
placement_es = st.text_area("Placement (Spanish)")
component_name = st.text_input("Component Name")
standard_weight = st.text_input("Standard Weight")
large_weight = st.text_input("Large Weight")

def draw_autoscaled_text(c, text, max_font_size, x_center, y, max_width, font_name="Helvetica-Bold", min_font=6):
    font_size = max_font_size
    c.setFont(font_name, font_size)
    text_width = c.stringWidth(text, font_name, font_size)
    while text_width > max_width and font_size > min_font:
        font_size -= 1
        c.setFont(font_name, font_size)
        text_width = c.stringWidth(text, font_name, font_size)
    c.drawCentredString(x_center, y, text)
    return font_size

def generate_pdf(component_type, step, meal_code, placement_en, placement_es,
                 component_name, standard_weight, large_weight, filename):
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter
    max_width = width - inch

    x_positions = [inch * 1.5, width / 2, width - inch * 1.5]
    y = height - 0.75 * inch

    # Headers
    c.setFont("Helvetica-Bold", 10)
    c.drawCentredString(x_positions[0], y, "COMPONENT TYPE")
    c.drawCentredString(x_positions[1], y, "STEP")
    c.drawCentredString(x_positions[2], y, "MEAL CODE")
    y -= 12
    c.setFont("Helvetica-Bold", 9)
    c.drawCentredString(x_positions[0], y, "(TIPO DE COMPONENTE)")
    c.drawCentredString(x_positions[1], y, "(PASO)")
    c.drawCentredString(x_positions[2], y, "(CÓDIGO DE COMIDA)")
    y -= 20

    draw_autoscaled_text(c, component_type, 16, x_positions[0], y, 100)
    draw_autoscaled_text(c, step, 16, x_positions[1], y, 100)
    draw_autoscaled_text(c, meal_code, 16, x_positions[2], y, 100)
    y -= 35

    draw_autoscaled_text(c, "PLACEMENT (COLOCACIÓN)", 22, width / 2, y, max_width)
    y -= 20

    placement_text = placement_en + " | " + placement_es
    wrapped_text = textwrap.wrap(placement_text, width=90)
    c.setFont("Helvetica", 10)
    for line in wrapped_text:
        c.drawCentredString(width / 2, y, line)
        y -= 15
    y -= 10

    draw_autoscaled_text(c, "COMPONENT NAME (NOMBRE DEL COMPONENTE)", 18, width / 2, y, max_width)
    y -= 18
    draw_autoscaled_text(c, component_name, 14, width / 2, y, max_width)
    y -= 35

    draw_autoscaled_text(c, "STANDARD (SIZE)", 16, width / 2, y, max_width)
    y -= 40
    draw_autoscaled_text(c, standard_weight, 80, width / 2, y, max_width)
    y -= 80

    draw_autoscaled_text(c, "LARGE (SIZE)", 16, width / 2, y, max_width)
    y -= 40
    draw_autoscaled_text(c, large_weight, 80, width / 2, y, max_width)

    c.save()

if st.button("Generate PDF"):
    filename = f"{meal_name or 'plating_step'}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    buffer = BytesIO()
    generate_pdf(component_type, step, meal_code, placement_en, placement_es,
                 component_name, standard_weight, large_weight, buffer)
    st.success("PDF generated successfully!")
    st.download_button("📄 Download PDF", buffer.getvalue(), file_name=filename, mime="application/pdf")
