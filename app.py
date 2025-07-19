import streamlit as st
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.units import inch
from reportlab.lib import colors

st.title("Multi-Step Plating PDF Generator")

st.write("Enter the meal code once, then add plating steps one by one.")

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
            f"COMPONENT\n(TYPE)\n{step['Component Type']}",
            f"STEP (#)\n{step['Step']}",
            f"MEAL CODE\n{step['Meal Code']}"
        ]]
        table = Table(table_data, colWidths=[2.2 * inch] * 3)
        table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('BOX', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(table)
        elements.append(Spacer(1, 0.3 * inch))

        # Placement moved below the header table
        elements.append(Paragraph("PLACEMENT", center_heading))
        elements.append(Paragraph(f"<b>{step['Placement']}</b>", styles['Title']))
        elements.append(Spacer(1, 0.3 * inch))

        elements.append(Paragraph("MEAL COMPONENT NAME", center_heading))
        elements.append(Paragraph(f"<b>{step['Meal Component Name']}</b>", styles['Title']))
        elements.append(Spacer(1, 0.3 * inch))

        elements.append(Paragraph("STANDARD (SIZE)", center_heading))
        elements.append(Paragraph(f"<font size=28><b>{step['Standard Size']}</b></font>", center_heading))
        elements.append(Spacer(1, 0.2 * inch))

        elements.append(Paragraph("LARGE (SIZE)", center_heading))
        elements.append(Paragraph(f"<font size=28><b>{step['Large Size']}</b></font>", center_heading))
        elements.append(Spacer(1, 0.8 * inch))

        elements.append(Spacer(1, 0.2 * inch))

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
        st.download_button("📥 Download PDF", data=pdf_buffer, file_name="plating_steps.pdf", mime="application/pdf")

    if st.button("🗑️ Clear All Steps"):
        st.session_state.steps.clear()
        st.experimental_rerun()
else:
    st.info("Add at least one step to generate a PDF.")
