import pytest

from src.document_upload import MAX_DOCUMENT_CHARS, parse_upload, parse_uploads


def test_txt_upload_is_normalized_and_bounded():
    result = parse_upload("notes.txt", b"hello\n   incident   response")
    assert result.name == "notes.txt"
    assert result.text == "hello incident response"


def test_csv_upload_is_converted_to_searchable_text():
    result = parse_upload("incidents.csv", b"title,severity\nLogin issue,high")
    assert "title | severity" in result.text
    assert "Login issue | high" in result.text


def test_unsupported_extension_is_rejected():
    with pytest.raises(ValueError, match="Unsupported document type"):
        parse_upload("payload.exe", b"data")


def test_oversized_upload_is_rejected():
    with pytest.raises(ValueError, match="1 MB"):
        parse_upload("large.txt", b"x" * 1_000_001)


def test_invalid_utf8_is_rejected():
    with pytest.raises(ValueError, match="UTF-8"):
        parse_upload("bad.txt", b"\xff\xfe")


def test_document_text_is_bounded():
    result = parse_upload("long.md", ("x" * (MAX_DOCUMENT_CHARS + 500)).encode())
    assert len(result.text) == MAX_DOCUMENT_CHARS


def test_upload_collection_is_bounded():
    files = [type("Upload", (), {"name": f"{i}.txt", "getvalue": lambda self: b"text"})() for i in range(6)]
    with pytest.raises(ValueError, match="at most 5"):
        parse_uploads(files)
