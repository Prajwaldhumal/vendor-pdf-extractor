import re
from typing import Dict, List

import fitz  # PyMuPDF


FIELD_ALIASES = {
    "Vendor Name": ["vendor name", "supplier name", "company name", "name of supplier", "name"],
    "Vendor Code": ["vendor code", "supplier code", "vendor id", "supplier id"],
    "GST Number": ["gst number", "gst no", "gstin", "gst registration number", "gst registration"],
    "PAN Number": ["pan number", "pan no", "pan"],
    "Address": ["registered address", "vendor address", "supplier address", "address"],
    "Contact Person": ["contact person", "contact name", "person name"],
    "Phone Number": ["phone number", "phone", "mobile number", "mobile", "contact number", "telephone"],
    "Email": ["email address", "email", "e-mail"],
    "Bank Name": ["bank name", "bank"],
    "Account Number": ["account number", "account no", "a/c number", "a/c no"],
    "IFSC Code": ["ifsc code", "ifsc", "ifsc no"],
}


def extract_pdf_text(pdf_bytes: bytes) -> str:
    """Extract selectable text from a PDF. OCR can be added later for scanned PDFs."""
    document = fitz.open(stream=pdf_bytes, filetype="pdf")
    pages = [page.get_text("text") for page in document]
    document.close()
    return "\n".join(pages)


def clean_value(value: str) -> str:
    value = re.sub(r"\s+", " ", value).strip(" :\t-|;")
    return value


def extract_by_label(text: str, aliases: List[str]) -> str:
    """Find a value occurring after a known label, primarily for label:value layouts."""
    lines = [line.strip() for line in text.splitlines() if line.strip()]

    # Prefer the longest aliases first to avoid matching 'pan' inside other labels.
    aliases = sorted(aliases, key=len, reverse=True)
    for i, line in enumerate(lines):
        lower = line.lower()
        for alias in aliases:
            pattern = rf"^\s*{re.escape(alias)}\s*(?:[:\-]|\|)\s*(.+)$"
            match = re.match(pattern, line, flags=re.IGNORECASE)
            if match:
                return clean_value(match.group(1))

            # Handle labels where the value is separated by whitespace.
            if lower == alias.lower() and i + 1 < len(lines):
                return clean_value(lines[i + 1])

            # Handle label followed by whitespace and value, e.g. "GSTIN 27..."
            pattern = rf"^\s*{re.escape(alias)}\s+(.+)$"
            match = re.match(pattern, line, flags=re.IGNORECASE)
            if match:
                candidate = clean_value(match.group(1))
                if candidate and candidate.lower() != alias.lower():
                    return candidate

    return ""


def extract_structured_fields(text: str) -> Dict[str, str]:
    """Extract common vendor fields using aliases and basic validation."""
    result = {field: extract_by_label(text, aliases) for field, aliases in FIELD_ALIASES.items()}

    # Strong pattern-based extraction for identifiers/contact information.
    if not result["GST Number"]:
        gst = re.search(r"\b\d{2}[A-Z]{5}\d{4}[A-Z][A-Z0-9]Z[A-Z0-9]\b", text, re.I)
        if gst:
            result["GST Number"] = gst.group(0).upper()

    if not result["PAN Number"]:
        pan = re.search(r"\b[A-Z]{5}\d{4}[A-Z]\b", text, re.I)
        if pan:
            result["PAN Number"] = pan.group(0).upper()

    if not result["Email"]:
        email = re.search(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", text, re.I)
        if email:
            result["Email"] = email.group(0)

    if not result["Phone Number"]:
        phone = re.search(r"(?<!\d)(?:\+91[\s-]?)?[6-9]\d{9}(?!\d)", text)
        if phone:
            result["Phone Number"] = phone.group(0)

    if not result["IFSC Code"]:
        ifsc = re.search(r"\b[A-Z]{4}0[A-Z0-9]{6}\b", text, re.I)
        if ifsc:
            result["IFSC Code"] = ifsc.group(0).upper()

    return result
