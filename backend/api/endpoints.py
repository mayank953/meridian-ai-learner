"""REST endpoints. Each route is thin: validate input, call the real logic, return JSON.

    /api/health        - is the server up?
    /api/status        - configuration summary shown on the System Status tab
    /api/agent/audit   - run the multi-agent procurement audit        (agent/agents.py)
    /api/rag/ask       - ask a question about the ingested documents  (rag/retrieval.py)
    /api/rag/upload    - upload PDFs and index them                   (rag/data_ingestion.py)
    /api/rag/ingest-gcs- index every PDF already sitting in the bucket
"""
import os
import platform
import shutil
import sys
import tempfile
import traceback
from datetime import datetime, timezone
from functools import lru_cache

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.concurrency import run_in_threadpool
from google.cloud import storage

from agent.agents import ProcurementSupervisor
from api.schemas import AuditRequest, AuditResponse, QueryRequest, QueryResponse
from config.settings import settings
from logger import GLOBAL_LOGGER as log
from rag.data_ingestion import ingest_data_from_gcs, ingest_pdf
from rag.retrieval import ask_question

health_router = APIRouter(prefix="/api", tags=["Health"])
status_router = APIRouter(prefix="/api", tags=["Status"])
agent_router = APIRouter(prefix="/api/agent", tags=["Agent"])
rag_router = APIRouter(prefix="/api/rag", tags=["RAG"])

# In-memory upload tracker (reset on restart)
_upload_history: list[dict] = []
_server_start_time = datetime.now(timezone.utc)


@lru_cache(maxsize=1)
def get_supervisor() -> ProcurementSupervisor:
    """Build the agents on the first audit request, not when the server starts."""
    return ProcurementSupervisor()


# ---------------------------------------------------------------------------
# Health & status
# ---------------------------------------------------------------------------

@health_router.get("/health")
def health():
    return {"status": "ok"}


@status_router.get("/status")
def system_status():
    """Return system configuration and health information (no calls to GCP)."""
    uptime_seconds = int((datetime.now(timezone.utc) - _server_start_time).total_seconds())
    hours, remainder = divmod(uptime_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    return {
        "backend": {
            "status": "healthy",
            "uptime": f"{hours:02d}h {minutes:02d}m {seconds:02d}s",
            "python_version": sys.version.split()[0],
            "platform": platform.system(),
        },
        "gcp": {
            "project_id": settings.GCP_PROJECT,
            "region": settings.GCP_REGION,
        },
        "storage": {
            "gcs_bucket": settings.GCS_BUCKET_NAME,
            "gcs_prefix": settings.GCS_PREFIX,
        },
        "vector_search": {
            "index_id": settings.vector_search_index_id or "NA",
            "endpoint_id": settings.vector_search_index_endpoint_id or "NA",
            "stream_update": True,
        },
        "models": {
            "embedding": settings.embedding_model_name,
            "llm": settings.llm_model_name,
            "llm_framework": "Gemini API (chat) + Vertex AI (embeddings) via LangChain",
        },
        "ingestion": {
            "uploads_this_session": len(_upload_history),
        },
    }


# ---------------------------------------------------------------------------
# Agent
# ---------------------------------------------------------------------------

@agent_router.post("/audit", response_model=AuditResponse)
def run_audit(payload: AuditRequest):
    """Run the full multi-agent procurement audit and return all phase results."""
    try:
        result = get_supervisor().run_audit(payload.request_text)
        return AuditResponse(**result)
    except Exception as e:
        log.error("Audit failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------------------------------------------------------
# RAG
# ---------------------------------------------------------------------------

@rag_router.post("/ask", response_model=QueryResponse)
def rag_query(payload: QueryRequest):
    """Query the RAG pipeline (Vertex AI Vector Search + Gemini)."""
    try:
        return QueryResponse(answer=ask_question(payload.query, payload.retriever_type))
    except Exception as e:
        log.error("RAG query failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@rag_router.post("/upload")
async def upload_documents(files: list[UploadFile] = File(...)):
    """Accept one or more PDFs, keep a copy in GCS, then chunk, embed and index them."""
    if not files:
        raise HTTPException(status_code=400, detail="No files provided.")

    results = []
    tmp_dir = tempfile.mkdtemp()

    try:
        for upload in files:
            if not upload.filename.lower().endswith(".pdf"):
                results.append({
                    "filename": upload.filename,
                    "status": "skipped",
                    "reason": "Only PDF files are supported.",
                })
                continue

            # Save to a temp file (the async UploadFile must be awaited to read it)
            local_path = os.path.join(tmp_dir, os.path.basename(upload.filename))
            with open(local_path, "wb") as f:
                f.write(await upload.read())

            # Keep the original PDF in the bucket as well
            try:
                bucket = storage.Client(project=settings.GCP_PROJECT).bucket(settings.GCS_BUCKET_NAME)
                gcs_path = f"{settings.GCS_PREFIX}{upload.filename}"
                bucket.blob(gcs_path).upload_from_filename(local_path, content_type="application/pdf")
                log.info("File saved to GCS", filename=upload.filename, gcs_path=f"gs://{settings.GCS_BUCKET_NAME}/{gcs_path}")
            except Exception as gcs_err:
                log.warning("Could not save to GCS", error=str(gcs_err))

            # ingest_pdf is slow and blocking, so run it in a worker thread to keep the server responsive
            summary = await run_in_threadpool(ingest_pdf, local_path, f"upload://{upload.filename}")

            if summary["chunks"] == 0:
                log.warning("No chunks extracted, skipping indexing", filename=upload.filename)
                results.append({
                    "filename": upload.filename,
                    "status": "skipped",
                    "reason": "No extractable text found in PDF (may be a scanned/image-based PDF).",
                })
                continue

            log.info("Successfully ingested chunks", filename=upload.filename, **summary)
            results.append({"filename": upload.filename, "status": "ingested", **summary})
    except Exception as e:
        log.error("Upload failed", traceback=traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)

    _upload_history.extend(results)
    return {"results": results}


@rag_router.get("/uploads")
def list_uploads():
    """Return the history of uploaded documents (in-memory, resets on restart)."""
    return {"uploads": _upload_history}


@rag_router.post("/ingest-gcs")
def trigger_gcs_ingestion():
    """Index every PDF that is already in the GCS bucket."""
    try:
        totals = ingest_data_from_gcs()
        return {"status": "GCS ingestion complete", **totals}
    except Exception as e:
        log.error("GCS ingestion failed", traceback=traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))
