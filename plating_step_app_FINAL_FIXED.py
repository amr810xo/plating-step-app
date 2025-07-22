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

st.write("Paste multiple step descriptions below. Each step can be multiple lines, separated by blank lines.")

# Scrollable text area style
st.markdown("""
<style>
textarea {
  resize: none;
  overflow-y: auto !important;
  max-height: 300px;
}
</style>
<script>
document.addEventListener('input', function (event) {
  if (event.target.tagName.toLowerCase() !== 'textarea') return;
  if (event.target.scrollHeight <= 300) {
    event.target.style.height = 'auto';
    event.target.style.height = (event.target.scrollHeight) + 'px';
  }
}, false);
</script>
""", unsafe_allow_html=True)

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

def generate_pdf_from_steps(steps):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()
    center_heading = ParagraphStyle(name='CenterHeading', parent=styles['Heading2'], alignment=TA_CENTER)
    centered_normal = ParagraphStyle(name='CenteredNormal', parent=styles['Normal'], alignment=TA_CENTER)

    for step in steps:
        header_data = [[
            "COMPONENT TYPE\n(TIPO DE COMPONENTE)",
            "STEP\n(PASO)",
            "MEAL CODE\n(CÓDIGO DE COMIDA)"
        ]]
        header_table = Table(header_data, colWidths=[2.2 * inch] * 3)
        header_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 14)
        ]))
        elements.append(header_table)

        data_table = Table([[
            Paragraph(f"<font size=12>{step['Component Type']}</font>", centered_normal),
            Paragraph(f"<font size=12>{step['Step']}</font>", centered_normal),
            Paragraph(f"<font size=12>{step['Meal Code']}</font>", centered_normal)
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
            ('FONTSIZE', (0, 0), (-1, -1), 14),
            ('BOX', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(placement_table)
        elements.append(Paragraph(f"<b>{step['Placement']}</b>", center_heading))
        elements.append(Spacer(1, 0.2 * inch))

        name_table = Table([["MEAL COMPONENT NAME"]], colWidths=[6.6 * inch])
        name_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 14),
            ('BOX', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(name_table)
        elements.append(Paragraph(f"<b>{step['Meal Component Name']}</b>", center_heading))
        elements.append(Spacer(1, 0.2 * inch))

        std_table = Table([["STANDARD (SIZE)"], [f"<b>{step['Standard Size']}</b>"]], colWidths=[6.6 * inch])
        std_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('FONTSIZE', (0, 1), (-1, -1), 36),
            ('BOX', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(std_table)

        large_table = Table([["LARGE (SIZE)"], [f"<b>{step['Large Size']}</b>"]], colWidths=[6.6 * inch])
        large_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('FONTSIZE', (0, 1), (-1, -1), 36),
            ('BOX', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(large_table)
        elements.append(PageBreak())

    doc.build(elements)
    buffer.seek(0)
    return buffer

if "steps" in st.session_state and st.session_state.steps:
    if st.button("📄 Generate PDF"):
        pdf_bytes = generate_pdf_from_steps(st.session_state.steps)
        st.download_button(
            label="📥 Download PDF",
            data=pdf_bytes,
            file_name=f"{meal_name[:25].strip().replace(' ', '_')}.pdf",
            mime="application/pdf"
        )
