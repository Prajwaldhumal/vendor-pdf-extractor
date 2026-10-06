# Vendor PDF → Excel Extractor

A first prototype for extracting common vendor information from differently formatted PDFs and exporting the results to Excel.

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Current version

- Supports multiple PDF uploads.
- Extracts selectable PDF text with PyMuPDF.
- Uses common field aliases and regex validation for GST, PAN, email, phone and IFSC.
- Shows an editable-style preview table.
- Exports extracted records to Excel.
- Shows raw extracted text for debugging.

## Next improvements

1. Add OCR for scanned/image-only PDFs.
2. Improve table extraction.
3. Add confidence scores and manual correction.
4. Add an AI/LLM extraction layer for highly variable vendor formats.
5. Add duplicate detection and validation rules.
