import streamlit as st
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Frame
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.units import inch
from reportlab.lib import colors
import re

st.title("Multi-Step Plating PDF Generator")

st.write("Enter the meal name (for file name), meal code once, then add plating steps one by one.")

# Meal name input (used for filename only)
meal_name = st.text_input("Meal Name (used for file name only)", key="meal_name")

# Persistent meal code
meal_code = st.text_input("Meal Code (e.g. A, B, AV2)", key="meal_code")

if "steps" not in st.session_state:
    st.session_state.steps = []

with st.form("step_form"):
    component_type = st.text_input("Component Type (e.g. VEG 1, PROTEIN 1)")
    placement = st.text_input("Placement (e.g. Bottom, On top of Mash)")
    step_code = st.text_input("Step Code (e.g. 1-P1)")
    meal_component_name = st.text_input("Meal Component Name")
    standard_size = st.text_input("Standard Size (g)")
    large_size = st.text_input("Large Size (g)")

    submitted = st.form_submit_button("➕ Add Step")
    if submitted:
        st.session_state.steps.append({
            "Component Type": component_type,
            "Placement": placement,
            "Step": step_code,
            "Meal Code": meal_code,
            "Meal Component Name": meal_component_name,
            "Standard Size": standard_size,
            "Large Size": large_size
        })

# PDF generation function using reportlab
def generate_pdf_from_steps(steps):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()
    center_heading = ParagraphStyle(name='CenterHeading', parent=styles['Heading2'], alignment=TA_CENTER)

    for step in steps:
        table_data = [[
            "COMPONENT TYPE (TIPO DE COMPONENTE)",
            "STEP (PASO)",
            "MEAL CODE (CÓDIGO DE COMIDA)"
        ], [
            Paragraph(f"<font size=9>{step['Component Type']}</font>", styles["Normal"]),
            Paragraph(f"<font size=9>{step['Step']}</font>", styles["Normal"]),
            Paragraph(f"<font size=9>{step['Meal Code']}</font>", styles["Normal"])
        ]]
        table = Table(table_data, colWidths=[2.2 * inch] * 3)
        table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, 1), 'Helvetica'),
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.black)
        ]))
        elements.append(table)
        elements.append(Spacer(1, 0.2 * inch))

        # Placement
        placement_table = Table([["PLACEMENT (COLOCACIÓN)"]], colWidths=[6.6 * inch])
        placement_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('BOX', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(placement_table)
        elements.append(Paragraph(f"<b>{step['Placement']}</b>", center_heading))
        elements.append(Spacer(1, 0.2 * inch))

        # Component Name
        name_table = Table([["COMPONENT NAME (NOMBRE DEL COMPONENTE)"]], colWidths=[6.6 * inch])
        name_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('BOX', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(name_table)
        elements.append(Paragraph(f"<b>{step['Meal Component Name']}</b>", center_heading))
        elements.append(Spacer(1, 0.2 * inch))

        # Standard Size
        std_table = Table([["STANDARD (ESTÁNDAR)"]], colWidths=[6.6 * inch])
        std_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('BOX', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(std_table)
        elements.append(Paragraph(f"<font size=28><b>{step['Standard Size']}</b></font>", center_heading))
        elements.append(Spacer(1, 0.2 * inch))

        # Large Size
        lg_table = Table([["LARGE (GRANDE)"]], colWidths=[6.6 * inch])
        lg_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('BOX', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(lg_table)
        elements.append(Paragraph(f"<font size=28><b>{step['Large Size']}</b></font>", center_heading))
        elements.append(Spacer(1, 0.6 * inch))

    doc.build(elements)
    buffer.seek(0)
    return buffer

# Show and download section
if st.session_state.steps:
    st.write("### Steps to Include:")
    for i, step in enumerate(st.session_state.steps):
        st.markdown(f"**{i+1}. {step['Step']} - {step['Meal Component Name']} ({step['Component Type']})**")

    if st.button("📄 Generate PDF"):
        pdf_buffer = generate_pdf_from_steps(st.session_state.steps)
        safe_filename = re.sub(r'[^a-zA-Z0-9_-]', '_', meal_name)[:25] or "plating_steps"
        st.download_button("📥 Download PDF", data=pdf_buffer, file_name=f"{safe_filename}.pdf", mime="application/pdf")

    if st.button("🗑️ Clear All Steps"):
        st.session_state.steps.clear()
        st.experimental_rerun()
else:
    st.info("Add at least one step to generate a PDF.")
