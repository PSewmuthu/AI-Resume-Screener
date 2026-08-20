"""
resume_parser.py
-----------------
Utility functions to extract plain text from resumes in different
file formats (.txt, .pdf, .docx) so they can be fed into the LLM.
"""

from pathlib import Path
import pdfplumber
import docx
import io


def parse_txt(file_bytes: bytes) -> str:
    """Decode a plain text resume file."""
    return file_bytes.decode('utf-8', errors='ignore')


def parse_pdf(file_bytes: bytes) -> str:
    """Extract text from a PDF resume file."""
    text_parts = []
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
    return "\n".join(text_parts)


def parse_docx(file_bytes: bytes) -> str:
    """Extract text from a DOCX resume file."""
    document = docx.Document(io.BytesIO(file_bytes))
    return "\n".join(p.text for p in document.paragraphs if p.text.strip())


def parse_resume(filename: str, file_bytes: bytes) -> str:
    """
    Dispatch to the right extractor based on file extension.

    Parameters
    ----------
    filename : str
        Original filename, used only to detect the extension.
    file_bytes : bytes
        Raw file content.

    Returns
    -------
    str
        Plain text content of the resume.
    """
    suffix = Path(filename).suffix.lower()

    if suffix == '.txt':
        return parse_txt(file_bytes)
    elif suffix == '.pdf':
        return parse_pdf(file_bytes)
    elif suffix == '.docx':
        return parse_docx(file_bytes)
    else:
        raise ValueError(
            f"Unsupported file type '{suffix}'. Please upload .txt, .pdf, or .docx files.")
