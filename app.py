import io
import streamlit as st
import pandas as pd
from extractor import extract_vendor_data

st.set_page_config(page_title="Vendor PDF → Excel", page_icon="📄", layout="wide")

st.title("📄 Vendor PDF → Excel Extractor")
st.caption("Upload multiple vendor PDFs. All extracted vendor records are combined into ONE Excel file.")

uploaded_files = st.file_uploader(
    "Upload Vendor PDF(s)",
    type=["pdf"],
    accept_multiple_files=True
)

if uploaded_files and st.button("🔎 Extract All Details", type="primary"):
    rows = []
    raw_texts = {}

    with st.spinner("Extracting all vendor PDFs..."):
        for uploaded_file in uploaded_files:
            data, raw_text = extract_vendor_data(uploaded_file)
            data["Source PDF"] = uploaded_file.name
            rows.append(data)
            raw_texts[uploaded_file.name] = raw_text

    fields = [
        "Source PDF", "Vendor Name", "Vendor Code", "GST Number",
        "PAN Number", "Address", "Contact Person", "Phone Number",
        "Email", "Bank Name", "Account Number", "IFSC Code"
    ]

    df = pd.DataFrame(rows)
    for col in fields:
        if col not in df.columns:
            df[col] = ""
    df = df[fields]

    st.session_state["df"] = df
    st.session_state["raw_texts"] = raw_texts

if "df" in st.session_state:
    st.subheader("📊 Combined Extraction Result")
    st.info(f"{len(st.session_state['df'])} vendor PDF(s) → 1 Excel file")

    edited_df = st.data_editor(
        st.session_state["df"],
        use_container_width=True,
        num_rows="fixed"
    )
    st.session_state["df"] = edited_df

    excel_buffer = io.BytesIO()
    with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
        st.session_state["df"].to_excel(
            writer, index=False, sheet_name="Vendor Details"
        )

    st.download_button(
        "📥 Download ONE Excel File",
        data=excel_buffer.getvalue(),
        file_name="vendor_details.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    with st.expander("🔍 View extracted raw text"):
        for name, text in st.session_state["raw_texts"].items():
            st.markdown(f"**{name}**")
            st.text(text[:10000])
