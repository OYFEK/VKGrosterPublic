
import streamlit as st
import fitz  # PyMuPDF
import re
from io import BytesIO

def extract_htl_entries(pdf_bytes, iata_code):
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    matches = []
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text = page.get_text()

        # Split by crew member blocks (each starts with a long employee number, e.g., 72121)
        blocks = re.split(r"(?=\n\d{5}\s+[A-ZÅÄÖa-zåäö ]+\n)", text)

        for block in blocks:
            if iata_code.upper() in block and "HTL" in block:
                name_match = re.search(r"\n(\d{5})\s+([A-ZÅÄÖa-zåäö ]+)", block)
                if name_match:
                    emp_id, name = name_match.groups()
                else:
                    emp_id, name = "UKENDT", "UKENDT"

                # Find lines with HTL and matching IATA
                htl_lines = []
                for line in block.split("\n"):
                    if "HTL" in line and iata_code.upper() in line:
                        htl_lines.append(line.strip())

                if htl_lines:
                    matches.append({
                        "name": name.strip(),
                        "iata": iata_code.upper(),
                        "lines": htl_lines
                    })
    return matches

st.title("🛏️ HTL Checker by IATA-kode")
st.write("Upload en Sunclass-vagtplan i PDF-format, og skriv en IATA-kode (f.eks. CPH, OSL, PMI) for at finde ud af, hvem der er på hotel der.")

uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])
iata_code = st.text_input("IATA-kode (f.eks. CPH)").upper()

if uploaded_file and iata_code:
    with st.spinner("Analyserer PDF..."):
        result = extract_htl_entries(uploaded_file.read(), iata_code)
    if result:
        st.success(f"Fandt {len(result)} personer med HTL i {iata_code}")
        for entry in result:
            st.markdown(f"### {entry['name']}")
            for line in entry["lines"]:
                st.write(f"• {line}")
    else:
        st.warning(f"Ingen fundet med HTL i {iata_code}")
