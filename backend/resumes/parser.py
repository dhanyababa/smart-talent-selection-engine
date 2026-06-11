import re
import os
import docx
import pymupdf
from PIL import Image
import pytesseract


SKILL_MAP = {
    "frontend": ["react", "html", "css", "javascript", "typescript", "redux"],
    "backend": ["python", "django", "flask", "java", "spring", "node", "express"],
    "database": ["mysql", "postgresql", "mongodb", "sqlite"],
    "machine_learning": ["machine learning", "pytorch", "tensorflow", "keras", "scikit-learn"],
    "cloud": ["aws", "azure", "gcp", "docker", "kubernetes"],
}


def extract_text_from_pdf(path):
    text = ""
    doc = pymupdf.open(path)
    for page in doc:
        text += page.get_text()
    return text


def extract_text_from_docx(path):
    document = docx.Document(path)
    return "\n".join([para.text for para in document.paragraphs])


def extract_text_from_image(path):
    image = Image.open(path)
    return pytesseract.image_to_string(image)


def extract_text(file_path):
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".pdf":
        return extract_text_from_pdf(file_path)

    if ext == ".docx":
        return extract_text_from_docx(file_path)

    if ext in [".jpg", ".jpeg", ".png"]:
        return extract_text_from_image(file_path)

    raise ValueError("Unsupported file format")


def extract_email(text):
    match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
    return match.group(0) if match else ""


def extract_phone(text):
    match = re.search(r'(\+?\d[\d\s\-]{8,}\d)', text)
    return match.group(0) if match else ""


def extract_name(text):
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    return lines[0] if lines else "Unknown Candidate"


def extract_years_experience(text):
    matches = re.findall(r'(\d+)\+?\s*(years|year|yrs|yr)', text.lower())
    years = [int(match[0]) for match in matches]
    return max(years) if years else 0


def map_skills(text):
    text_lower = text.lower()
    found = {}

    for category, skills in SKILL_MAP.items():
        found[category] = []
        for skill in skills:
            if skill in text_lower:
                found[category].append(skill)

    return found


def build_profile(text):
    return {
        "name": extract_name(text),
        "email": extract_email(text),
        "phone": extract_phone(text),
        "years_experience": extract_years_experience(text),
        "skills": map_skills(text),
    }