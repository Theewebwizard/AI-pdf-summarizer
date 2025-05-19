from PyPDF2 import PdfReader

def clean_text(text: str) -> str:
    """Remove PDF artifacts and normalize text"""
    text = re.sub(r'\s+', ' ', text)  # Fix broken spacing
    text = re.sub(r'http\S+|www\S+|DOI:\s*\S+', '', text)  # Remove URLs/DOIs
    text = re.sub(r'[^\w\s.,;:!?()-]', '', text)  # Keep only readable chars
    #  Join words split across lines by a hyphen
    text = re.sub(r'(\w+)-\s*\n\s*(\w+)', r'\1\2', text)
    #  Join words split without a hyphen
    text = re.sub(r'(\w+)\s*\n\s*(\w+)', r'\1 \2', text)
    #  Remove extra whitespaces
    text = ' '.join(text.split())
    return text.strip()

def extract_text_from_pdf(path: str) -> str:
    reader = PdfReader(path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
        text += page_text + " "  # Add space between pages
    text = clean_text(text)
    return text
