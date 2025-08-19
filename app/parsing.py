# app/parsing.py
from __future__ import annotations

import io
from typing import Optional
from werkzeug.datastructures import FileStorage

# PDF/DOCX parsers
from PyPDF2 import PdfReader
from docx import Document


def _extract_pdf_text(raw_bytes: bytes) -> str:
    with io.BytesIO(raw_bytes) as buf:
        reader = PdfReader(buf)
        parts = []
        for page in reader.pages:
            txt = page.extract_text() or ""
            parts.append(txt)
        return "\n".join(parts).strip()


def _extract_docx_text(raw_bytes: bytes) -> str:
    with io.BytesIO(raw_bytes) as buf:
        doc = Document(buf)
        return "\n".join(p.text for p in doc.paragraphs).strip()


def extract_text_from_resume(file: FileStorage) -> str:
    """
    Read a Flask FileStorage (PDF or DOCX) and return plain text.
    Safe for small files (we already limit size in Config).
    """
    if not file or not file.filename:
        return ""

    filename = file.filename.lower()
    raw = file.read()  # read the upload
    file.stream.seek(0)  # rewind for any later use

    if filename.endswith(".pdf"):
        return _extract_pdf_text(raw)
    if filename.endswith(".docx"):
        return _extract_docx_text(raw)

    # Unsupported extension
    return ""
