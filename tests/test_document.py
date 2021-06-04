import pathlib
import pytest
from drawbot_skia.document import PDFDocument


def test_pdf_document(tmpdir):
    tmpdir = pathlib.Path(tmpdir)
    pdf_path = tmpdir / "test.pdf"
    doc = PDFDocument(pdf_path)
    with doc.drawing() as db:
        db.newPage(400, 500)
        db.rect(100, 100, 200, 300)


def test_pdf_document_error(tmpdir):
    tmpdir = pathlib.Path(tmpdir)
    pdf_path = tmpdir / "test.pdf"
    doc = PDFDocument(pdf_path)
    with pytest.raises(ZeroDivisionError):
        with doc.drawing() as db:
            db.newPage(400, 500)
            db.rect(100, 100, 200, 300)
            1 / 0
