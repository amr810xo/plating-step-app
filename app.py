
import streamlit as st
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.units import inch
from reportlab.lib import colors
import re
import textwrap

st.set_page_config(page_title="Multi-Step Plating PDF Generator", layout="centered")
st.title("Multi-Step Plating PDF Generator")

st.write("Paste multiple step descriptions below. Each step can be multiple lines, separated by blank lines.")

meal_name = st.text_input("Meal Name (used for file name only)", key="meal_name")
meal_code = st.text_input("Meal Code (e.g. A, B, AV2)", key="meal_code")

if "parsed_steps" not in st.session_state:
    st.session_state.parsed_steps = []

multi_input = st.text_area(
    "Paste Multiple Steps",
    height=150,
    help="Use blank lines between steps. Wrapped lines will be joined automatically."
)

if st.button("🧩 Parse Steps"):
    st.session_state.parsed_steps.clear()
    lines = multi_input.strip().split("\n")
    blocks = []
    buffer = []

    for line in lines:
        if line.strip() == "":
            if buffer:
                blocks.append(" ".join(buffer).strip())
                buffer = []
        else:
            buffer.append(line.strip())

    if buffer:
        blocks.append(" ".join(buffer).strip())

    parsed = []
    for idx, raw_input in enumerate(blocks):
        try:
            line = re.sub(r"^\d+\s*-\s*", "", raw_input)
            component_type = re.findall(r"^(.*?):", line)[0].strip()
            line = line.split(":", 1)[1]
            line = re.sub(r"\(.*?\)", "", line).strip()
            meal_component_name = line.split("→")[0].strip()
            rest = line.split("→")[1].strip()
            step_match = re.search(r"(\d+)\)\s*(P\d+)", rest)
            step_code = f"{step_match.group(1)}-{step_match.group(2)}" if step_match else ""
            placement_text = rest.split(step_match.group(0), 1)[1].strip() if step_match else rest
            english, spanish = placement_text.split("|", 1)
            spanish = re.sub(r"Paso\s*\d+\)\s*P\d+", "", spanish).strip()
            placement = f"{english.strip()} | {spanish.strip()}"

            parsed.append({
                "Component Type": component_type,
                "Placement": placement,
                "Step": step_code,
                "Meal Code": meal_code,
                "Meal Component Name": meal_component_name,
                "Standard Size": "",
                "Large Size": ""
            })
        except Exception as e:
            st.error(f"Line {idx+1} parse error: {e}")

    st.session_state.parsed_steps = parsed

if st.session_state.parsed_steps:
    st.write("### Review and fill in sizes:")
    for i, step in enumerate(st.session_state.parsed_steps):
        st.markdown(f"**{i+1}. {step['Step']} - {step['Meal Component Name']} ({step['Component Type']})**")
        step["Standard Size"] = st.text_input(f"Standard Size (g) for Step {i+1}", key=f"std_{i}")
        step["Large Size"] = st.text_input(f"Large Size (g) for Step {i+1}", key=f"lg_{i}")

    if st.button("➕ Add All Steps"):
        if "steps" not in st.session_state:
            st.session_state.steps = []
        st.session_state.steps.extend(st.session_state.parsed_steps)
        st.session_state.parsed_steps.clear()
        st.rerun()


def autoscale_font(c, text, max_font_size, max_width, fontname="Helvetica-Bold"):
    font_size = max_font_size
    text_width = c.stringWidth(text, fontname, font_size)
    while text_width > max_width and font_size > 1:
        font_size -= 1
        text_width = c.stringWidth(text, fontname, font_size)
    return font_size


def generate_pdf_from_steps(steps):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()
    
    header_style = ParagraphStyle(name='Header', alignment=TA_CENTER, fontSize=30, leading=34, underline=True)
    value_style = ParagraphStyle(name='Value', alignment=TA_CENTER, fontSize=25)
    component_style = ParagraphStyle(name='Component', alignment=TA_CENTER, fontSize=25)
    placement_style = ParagraphStyle(name='Placement', alignment=TA_CENTER, fontSize=25)
    weight_style = ParagraphStyle(name='Weight', alignment=TA_CENTER, fontSize=90)

    for step in steps:
        # Header labels
        col_data = [["COMPONENT TYPE", "STEP", "MEAL CODE"],
                    ["(TIPO DE COMPONENTE)", "(PASO)", "(CÓDIGO DE COMIDA)"]]
        table = Table(col_data, colWidths=[2 * inch] * 3)
        table.setStyle(TableStyle([
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
            ("FONTSIZE", (0, 0), (-1, -1), 14),
        ]))
        elements.append(table)

        # Header values
        val_data = [[
            Paragraph(step["Component Type"], value_style),
            Paragraph(step["Step"], value_style),
            Paragraph(step["Meal Code"], value_style),
        ]]
        val_table = Table(val_data, colWidths=[2 * inch] * 3)
        val_table.setStyle(TableStyle([
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ]))
        elements.append(val_table)
        elements.append(Spacer(1, 20))

        # Placement
        elements.append(Paragraph("PLACEMENT (COLOCACIÓN)", header_style))
        wrapped = textwrap.wrap(step["Placement"], width=100)
        for line in wrapped:
            elements.append(Paragraph(line, placement_style))
        elements.append(Spacer(1, 20))

        # Component Name
        elements.append(Paragraph("COMPONENT NAME (NOMBRE DEL COMPONENTE)", header_style))
        elements.append(Paragraph(step["Meal Component Name"], component_style))
        elements.append(Spacer(1, 30))

        # Standard
        elements.append(Paragraph("STANDARD (ESTÁNDAR)", header_style))
        elements.append(Spacer(1, 20))
        elements.append(Paragraph(step['Standard Size'], weight_style))
        elements.append(Spacer(1, 50))  # More spacing to prevent overlap

        # Large
        elements.append(Paragraph("LARGE (GRANDE)", header_style))
        elements.append(Spacer(1, 20))
        elements.append(Paragraph(step['Large Size'], weight_style))

        elements.append(PageBreak())

    doc.build(elements)
    return buffer



if st.button("📄 Generate PDF"):
    if "steps" in st.session_state and st.session_state.steps:
        pdf = generate_pdf_from_steps(st.session_state.steps)
        st.download_button("⬇️ Download PDF", data=pdf, file_name=f"{meal_name[:25]}.pdf")
    else:
        st.warning("No steps added yet.")
