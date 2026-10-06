import re
import fitz

FIELD_ALIASES = {
    "Vendor Name": ["vendor name", "supplier name", "company name", "name of supplier", "name of vendor"],
    "Vendor Code": ["vendor code", "supplier code", "vendor id", "supplier id"],
    "GST Number": ["gst no", "gst number", "gstin", "gst registration number", "gst registration"],
    "PAN Number": ["pan", "pan no", "pan number"],
    "Address": ["address", "registered address", "office address", "supplier address", "vendor address"],
    "Contact Person": ["contact person", "contact name", "person name"],
    "Phone Number": ["phone", "phone number", "mobile", "mobile number", "contact number", "telephone"],
    "Email": ["email", "email id", "e-mail", "e-mail id"],
    "Bank Name": ["bank name", "bank"],
    "Account Number": ["account number", "account no", "bank account"],
    "IFSC Code": ["ifsc", "ifsc code"],
}

PATTERNS = {
    "GST Number": r"\b\d{2}[A-Z]{5}\d{4}[A-Z][A-Z0-9]Z[A-Z0-9]\b",
    "PAN Number": r"\b[A-Z]{5}\d{4}[A-Z]\b",
    "Email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
    "Phone Number": r"\b(?:\+91[-\s]?)?[6-9]\d{9}\b",
    "IFSC Code": r"\b[A-Z]{4}0[A-Z0-9]{6}\b",
}

def extract_text(pdf_file):
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    return "\n".join(page.get_text("text") for page in doc)

def clean_value(value):
    return re.sub(r"\s+", " ", value).strip(" :-\t")

def extract_labeled_value(text, aliases):
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    for line in lines:
        lower = line.lower()
        for alias in aliases:
            if alias in lower:
                parts = re.split(r"[:\-]\s*", line, maxsplit=1)
                if len(parts) == 2 and parts[1].strip():
                    return clean_value(parts[1])
                idx = lower.find(alias)
                value = line[idx + len(alias):].strip(" :-\t")
                if value:
                    return clean_value(value)
    return ""

def extract_vendor_data(pdf_file):
    text = extract_text(pdf_file)
    result = {}

    for field, aliases in FIELD_ALIASES.items():
        result[field] = extract_labeled_value(text, aliases)

    for field, pattern in PATTERNS.items():
        if not result.get(field):
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                result[field] = (
                    match.group(0).upper()
                    if field != "Email" else match.group(0)
                )

    return result, text
