import tempfile
import requests
from pdfminer.high_level import extract_text


def extract_text_from_pdf(pdf_url: str) -> str:
    """
    Download and extract text from a PDF given its URL, using a temporary file.
    """
    response = requests.get(pdf_url)
    if response.status_code != 200:
        return "Error: Unable to retrieve PDF."

    try:
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=True) as temp_pdf:
            temp_pdf.write(response.content)
            temp_pdf.flush()  # Ensure all data is written before reading

            text = extract_text(temp_pdf.name)
            return text.strip() if text else "Error: No text extracted from PDF."

    except Exception as e:
        return f"Error extracting PDF text: {e}"
