"""Connection to Vertex AI Vector Search (the database that stores our embeddings)."""
from functools import lru_cache

from google.cloud import aiplatform
from langchain_google_vertexai import VectorSearchVectorStore

from config.settings import settings
from rag.embeddings import get_embeddings


@lru_cache(maxsize=1)
def get_vector_store() -> VectorSearchVectorStore:
    """Connect on first use, so the API can start (e.g. /api/health) before GCP is configured."""
    aiplatform.init(project=settings.GCP_PROJECT, location=settings.GCP_REGION)

    return VectorSearchVectorStore.from_components(
        project_id=settings.GCP_PROJECT,
        region=settings.GCP_REGION,
        embedding=get_embeddings(),  # NOTE: singular "embedding", not "embeddings"
        index_id=settings.vector_search_index_id,
        endpoint_id=settings.vector_search_index_endpoint_id,
        gcs_bucket_name=settings.GCS_BUCKET_NAME,
        stream_update=True,
    )
