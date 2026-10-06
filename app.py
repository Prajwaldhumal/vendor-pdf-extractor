import io
import pandas as pd
import streamlit as st

from extractor import extract_pdf_text, extract_structured_fields


st.set_page_config(page_title="Vendor PDF Extractor", page_icon="📄", layout="wide")

st.title("📄 Vendor PDF → Excel Extractor")
st.write("Upload one or more vendor PDFs. The application will extract common vendor details and prepare an Excel file.")

with st.sidebar:
    st.header("Extraction Fields")
    fields = [
        "Vendor Name", "Vendor Code", "GST Number", "PAN Number", "Address",
        "Contact Person", "Phone Number", "Email", "Bank Name", "Account Number", "IFSC Code"
    ]
    selected_fields = [field for field in fields if st.checkbox(field, value=True)]

uploaded_files = st.file_uploader(
    "Upload Vendor PDF files",
    type=["pdf"],
    accept_multiple_files=True,
)

if uploaded_files:
    rows = []
    raw_texts = {}

    with st.spinner("Extracting vendor details..."):
        for uploaded_file in uploaded_files:
            pdf_bytes = uploaded_file.read()
            try:
                text = extract_pdf_text(pdf_bytes)
                raw_texts[uploaded_file.name] = text
                extracted = extract_structured_fields(text)
                row = {field: extracted.get(field, "") for field in selected_fields}
                row["Source PDF"] = uploaded_file.name
                rows.append(row)
            except Exception as exc:
                st.error(f"Could not process {uploaded_file.name}: {exc}")

    if rows:
        df = pd.DataFrame(rows)
        columns = ["Source PDF"] + selected_fields
        df = df[[c for c in columns if c in df.columns]]

        st.subheader("Extraction Preview")
        st.dataframe(df, use_container_width=True, hide_index=True)

        st.subheader("Raw Text Preview")
        selected_pdf = st.selectbox("Choose a PDF to inspect", list(raw_texts.keys()))
        st.text_area("Extracted text", raw_texts[selected_pdf], height=250)

        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Vendor Details")
        output.seek(0)

        st.download_button(
            label="⬇️ Export to Excel",
            data=output,
            file_name="vendor_details.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            type="primary",
        )
else:
    st.info("Upload one or more PDF files to begin.")
