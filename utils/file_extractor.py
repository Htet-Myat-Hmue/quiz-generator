import docx
import PyPDF2

def extract_text_from_file(file):
    if file.filename.endswith('.docx'):
        return extract_text_from_docx(file)
    elif file.filename.endswith('.pdf'):
        return extract_text_from_pdf(file)

def extract_text_from_docx(file):
    doc = docx.Document(file)
    return "\n".join([para.text for para in doc.paragraphs])

def extract_text_from_pdf(file):
    reader = PyPDF2.PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text
