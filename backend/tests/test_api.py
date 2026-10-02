"""Smoke tests: the API starts and its routes work WITHOUT Google Cloud (everything external is faked)."""
from fastapi.testclient import TestClient
from langchain_core.documents import Document

from api import endpoints
from api.main import app

client = TestClient(app)


def test_health():
    assert client.get("/api/health").json() == {"status": "ok"}


def test_status_shows_config_without_calling_gcp():
    body = client.get("/api/status").json()
    assert body["gcp"]["project_id"] == "test-project"
    assert body["models"]["embedding"] == "text-embedding-005"


def test_unknown_api_route_is_404():
    assert client.get("/api/does-not-exist").status_code == 404


def test_ask_returns_answer(monkeypatch):
    monkeypatch.setattr(endpoints, "ask_question", lambda query, retriever_type: f"answer to: {query}")
    res = client.post("/api/rag/ask", json={"query": "hello", "retriever_type": "similarity"})
    assert res.status_code == 200
    assert res.json() == {"answer": "answer to: hello"}


def test_audit_returns_all_four_sections(monkeypatch):
    class FakeSupervisor:
        def run_audit(self, text):
            return {"risk_result": "r", "tax_result": "t", "control_result": "c", "cfo_memo": "m"}

    monkeypatch.setattr(endpoints, "get_supervisor", lambda: FakeSupervisor())
    res = client.post("/api/agent/audit", json={"request_text": "buy 200 PLCs"})
    assert res.status_code == 200
    assert set(res.json()) == {"risk_result", "tax_result", "control_result", "cfo_memo"}


def test_upload_skips_non_pdf():
    res = client.post("/api/rag/upload", files={"files": ("notes.txt", b"hi", "text/plain")})
    assert res.json()["results"][0]["status"] == "skipped"


def test_chunking_splits_long_text_and_keeps_metadata():
    from rag.data_ingestion import split_into_chunks

    page = Document(page_content="word " * 1000, metadata={"source": "test.pdf"})
    chunks = split_into_chunks([page])
    assert len(chunks) > 1
    assert all(c.metadata["source"] == "test.pdf" for c in chunks)
    assert all(len(c.page_content) <= 1000 for c in chunks)


def test_sample_pdfs_load_and_chunk():
    """The demo PDFs in sample_docs/ can be read and split (no Google Cloud needed)."""
    import glob
    import os

    from langchain_community.document_loaders import PyPDFLoader

    from rag.data_ingestion import split_into_chunks

    folder = os.path.join(os.path.dirname(__file__), "..", "..", "sample_docs")
    pdfs = glob.glob(os.path.join(folder, "*.pdf"))
    assert len(pdfs) == 4
    for pdf in pdfs:
        assert split_into_chunks(PyPDFLoader(pdf).load()), pdf


def test_log_lines_carry_a_severity_field_for_cloud_logging():
    from logger.custom_logger import add_severity

    assert add_severity(None, "info", {"event": "x", "level": "info"})["severity"] == "INFO"
    assert add_severity(None, "error", {"event": "x", "level": "error"})["severity"] == "ERROR"
    assert "severity" not in add_severity(None, "info", {"event": "x"})
