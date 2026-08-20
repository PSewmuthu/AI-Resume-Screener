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
