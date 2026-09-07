"""Secure, bounded document upload parsing for P6.

Uploads are kept in Streamlit session state by the application and are never
written to the repository's persistent vector store.
"""

from __future__ import annotations

import csv
import io
from dataclasses import dataclass


ALLOWED_EXTENSIONS = frozenset({"txt", "md", "csv"})
MAX_FILE_BYTES = 1_000_000
MAX_FILES = 5
MAX_DOCUMENT_CHARS = 20_000


@dataclass(frozen=True)
class UploadedDocument:
    """Validated document ready for ephemeral session indexing."""

    name: str
    text: str


def validate_upload(name: str, data: bytes) -> None:
    """Validate filename and bounded payload before parsing."""
    if not isinstance(name, str) or not name.strip():
        raise ValueError("A document filename is required.")
    if not isinstance(data, (bytes, bytearray)):
        raise TypeError("Uploaded document data must be bytes.")
    if len(data) == 0:
        raise ValueError("Uploaded document is empty.")
    if len(data) > MAX_FILE_BYTES:
        raise ValueError("Uploaded document exceeds the 1 MB size limit.")
    suffix = name.rsplit(".", 1)[-1].lower() if "." in name else ""
    if suffix not in ALLOWED_EXTENSIONS:
        raise ValueError("Unsupported document type. Use TXT, MD, or CSV.")


def _decode(data: bytes) -> str:
    try:
        return data.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise ValueError("Document must use UTF-8 text encoding.") from exc


def _parse_csv(text: str) -> str:
    reader = csv.reader(io.StringIO(text))
    rows = [" | ".join(cell.strip() for cell in row) for row in reader]
    return "\n".join(row for row in rows if row.strip())


def parse_upload(name: str, data: bytes) -> UploadedDocument:
    """Validate and parse one upload into bounded plain text."""
    validate_upload(name, data)
    text = _decode(bytes(data))
    suffix = name.rsplit(".", 1)[-1].lower()
    if suffix == "csv":
        text = _parse_csv(text)
    text = " ".join(text.split())
    if not text:
        raise ValueError("Document contains no usable text.")
    return UploadedDocument(name=name.strip(), text=text[:MAX_DOCUMENT_CHARS])


def parse_uploads(files) -> list[UploadedDocument]:
    """Parse a bounded collection of Streamlit-like uploaded files."""
    if files is None:
        return []
    if len(files) > MAX_FILES:
        raise ValueError(f"Upload at most {MAX_FILES} documents at a time.")
    documents = []
    for uploaded in files:
        name = getattr(uploaded, "name", "")
        data = uploaded.getvalue()
        documents.append(parse_upload(name, data))
    return documents
