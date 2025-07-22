import streamlit as st
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.units import inch
from reportlab.lib import colors
import re

st.set_page_config(page_title="Multi-Step Plating PDF Generator", layout="centered")
st.title("Multi-Step Plating PDF Generator")

st.write("Paste a step description below. Standard Size and Large Size must still be entered manually.")

# Inject JavaScript for auto-expanding text fields
st.markdown("""
<style>
textarea {
  overflow: hidden;
  resize: none;
}
</style>
<script>
document.addEventListener('input', function (event) {
  if (event.target.tagName.toLowerCase() !== 'textarea') return;
  event.target.style.height = 'auto';
  event.target.style.height = (event.target.scrollHeight) + 'px';
}, false);
</script>
""", unsafe_allow_html=True)

# Meal name input (used for filename only)
meal_name = st.text_input("Meal Name (used for file name only)", key="meal_name")

# Persistent meal code
meal_code = st.text_input("Meal Code (e.g. A, B, AV2)", key="meal_code")

if "steps" not in st.session_state:
    st.session_state.steps = []

with st.form("step_form"):
    raw_input = st.text_area("Paste Step Description")
    standard_size = st.text_input("Standard Size (g)")
    large_size = st.text_input("Large Size (g)")

    submitted = st.form_submit_button("➕ Add Step")
    if submitted and raw_input:
        try:
            # Remove leading number and dash
            line = re.sub(r"^\d+\s*-\s*", "", raw_input)
            # Extract Component Type
            component_type = re.findall(r"^(.*?):", line)[0].strip()
            line = line.split(":", 1)[1]
            # Remove parentheses section
            line = re.sub(r"\(.*?\)", "", line).strip()
            # Extract Meal Component Name (before →)
            meal_component_name = line.split("→")[0].strip()
            rest = line.split("→")[1].strip()
            # Extract Step Code (e.g. 1) P1 → 1-P1)
            step_match = re.search(r"(\d+)\)\s*(P\d+)", rest)
            step_code = f"{step_match.group(1)}-{step_match.group(2)}" if step_match else ""
            # Extract placement section (after step), keeping '|', removing "Paso" part
            placement_text = rest.split(step_match.group(0), 1)[1].strip() if step_match else rest
            english, spanish = placement_text.split("|", 1)
            spanish = re.sub(r"Paso\s*\d+\)\s*P\d+", "", spanish).strip()
            placement = f"{english.strip()} | {spanish.strip()}"

            st.session_state.steps.append({
                "Component Type": component_type,
                "Placement": placement,
                "Step": step_code,
                "Meal Code": meal_code,
                "Meal Component Name": meal_component_name,
                "Standard Size": standard_size,
                "Large Size": large_size
            })
        except Exception as e:
            st.error(f"Error parsing step: {e}")

# PDF generation function using reportlab
def generate_pdf_from_steps(steps):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()
    center_heading = ParagraphStyle(name='CenterHeading', parent=styles['Heading2'], alignment=TA_CENTER)
    centered_normal = ParagraphStyle(name='CenteredNormal', parent=styles['Normal'], alignment=TA_CENTER)

    for step in steps:
        header_data = [[
            "COMPONENT TYPE (TIPO DE COMPONENTE)",
            "STEP (PASO)",
            "MEAL CODE (CÓDIGO DE COMIDA)"
        ]]
        header_table = Table(header_data, colWidths=[2.2 * inch] * 3)
        header_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9)
        ]))
        elements.append(header_table)

        data_table = Table([[
            Paragraph(f"<font size=8>{step['Component Type']}</font>", centered_normal),
            Paragraph(f"<font size=8>{step['Step']}</font>", centered_normal),
            Paragraph(f"<font size=8>{step['Meal Code']}</font>", centered_normal)
        ]], colWidths=[2.2 * inch] * 3)
        data_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.black)
        ]))
        elements.append(data_table)
        elements.append(Spacer(1, 0.2 * inch))

        placement_table = Table([["PLACEMENT (COLOCACIÓN)"]], colWidths=[6.6 * inch])
        placement_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('BOX', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(placement_table)
        elements.append(Paragraph(f"<b>{step['Placement']}</b>", center_heading))
        elements.append(Spacer(1, 0.2 * inch))

        name_table = Table([["COMPONENT NAME (NOMBRE DEL COMPONENTE)"]], colWidths=[6.6 * inch])
        name_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('BOX', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(name_table)
        elements.append(Paragraph(f"<b>{step['Meal Component Name']}</b>", center_heading))
        elements.append(Spacer(1, 0.2 * inch))

        std_table = Table([["STANDARD (ESTÁNDAR)"]], colWidths=[6.6 * inch])
        std_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('BOX', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(std_table)
        elements.append(Paragraph(f"<font size=28><b>{step['Standard Size']}</b></font>", center_heading))
        elements.append(Spacer(1, 0.2 * inch))

        lg_table = Table([["LARGE (GRANDE)"]], colWidths=[6.6 * inch])
        lg_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('BOX', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(lg_table)
        elements.append(Paragraph(f"<font size=28><b>{step['Large Size']}</b></font>", center_heading))

        elements.append(PageBreak())

    doc.build(elements)
    buffer.seek(0)
    return buffer

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
