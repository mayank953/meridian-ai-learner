"""Getting documents INTO the vector database.

    PDF file -> pages -> chunks (~1000 characters) -> embeddings -> Vector Search

Two entry points share the same steps:
  * ingest_pdf()           - one local PDF (used by the upload endpoint)
  * ingest_data_from_gcs() - every PDF under the configured GCS bucket/prefix
"""
import os
import shutil
import tempfile

from google.cloud import storage
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from config.settings import settings
from logger import GLOBAL_LOGGER as log
from rag.vector_store import get_vector_store

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 100  # neighbouring chunks share 100 characters so sentences are not cut off


def split_into_chunks(pages: list[Document]) -> list[Document]:
    splitter = RecursiveCharacterTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
    return splitter.split_documents(pages)


def ingest_pdf(local_path: str, source: str) -> dict:
    """Load one PDF, chunk it and store it. Returns {"pages": n, "chunks": n}.

    `source` is saved in each chunk's metadata so answers can be traced back to a file.
    """
    pages = PyPDFLoader(local_path).load()
    for page in pages:
        page.metadata["source"] = source

    chunks = split_into_chunks(pages)
    if chunks:
        log.info("Embedding chunks and pushing to Vector Search", source=source, chunks=len(chunks))
        get_vector_store().add_documents(chunks)
    return {"pages": len(pages), "chunks": len(chunks)}


def ingest_data_from_gcs() -> dict:
    """Ingest every PDF found in the GCS bucket under settings.GCS_PREFIX."""
    log.info("Connecting to GCS bucket", bucket=settings.GCS_BUCKET_NAME)

    client = storage.Client(project=settings.GCP_PROJECT)
    blobs = client.bucket(settings.GCS_BUCKET_NAME).list_blobs(prefix=settings.GCS_PREFIX)

    totals = {"files": 0, "pages": 0, "chunks": 0}
    tmp_dir = tempfile.mkdtemp()
    try:
        for blob in blobs:
            if not blob.name.lower().endswith(".pdf"):
                continue
            local_path = os.path.join(tmp_dir, os.path.basename(blob.name))
            blob.download_to_filename(local_path)
            result = ingest_pdf(local_path, source=f"gs://{settings.GCS_BUCKET_NAME}/{blob.name}")
            log.info("Ingested PDF from GCS", blob=blob.name, **result)
            totals["files"] += 1
            totals["pages"] += result["pages"]
            totals["chunks"] += result["chunks"]
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)

    if totals["files"] == 0:
        log.warning("No PDF documents found in the specified bucket/prefix")
    log.info("Ingestion complete", **totals)
    return totals
