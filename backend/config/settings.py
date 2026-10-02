import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
# from logger import GLOBAL_LOGGER as log

class Settings(BaseSettings):
    # App
    app_name: str = "Meridian AI - Procurement Intelligence"
    app_env: str = Field("", validation_alias="ENVIRONMENT")
    app_version: str = "1.0.0"
    debug: bool = True

    # GCP
    GOOGLE_API_KEY: str = Field("", validation_alias="GOOGLE_API_KEY")
    GCP_PROJECT: str = Field("", validation_alias="GCP_PROJECT_ID")
    GCP_REGION: str = Field("", validation_alias="GCP_REGION")
    GCS_BUCKET_NAME: str = Field("", validation_alias="GCS_BUCKET_NAME")
    GCS_PREFIX: str = Field("", validation_alias="GCS_PREFIX")
    gcp_service_account_path: str = Field("", validation_alias="GCP_SERVICE_ACCOUNT_PATH")

    # Model / RAG
    llm_model_name: str = Field("gemini-3.8-flash", validation_alias="VERTEX_LLM_MODEL_NAME")
    # 0 = most repeatable answers. If the model loops or repeats itself, try 1.0 (Gemini 3 default)
    llm_temperature: float = Field(0.0, validation_alias="LLM_TEMPERATURE")
    # Must output 768 dimensions to match the Vector Search index (see rag/embeddings.py)
    embedding_model_name: str = Field("text-embedding-005", validation_alias="VERTEX_EMBEDDING_MODEL_NAME")
    # VERTEX AI VECTOR SEARCH
    vector_search_index_id: str = Field("", validation_alias="VECTOR_SEARCH_INDEX_ID")
    vector_search_index_endpoint_id: str = Field("", validation_alias="VECTOR_SEARCH_INDEX_ENDPOINT_ID")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()



# Post-initialization: Set GOOGLE_APPLICATION_CREDENTIALS if path is provided
if settings.gcp_service_account_path:
    # Try to resolve relative to project root (where .env usually is)
    # This is rough but helpful for local dev
    abs_path = os.path.abspath(settings.gcp_service_account_path)
    if os.path.exists(abs_path):
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = abs_path
        # log.info("Google Application Credentials set", path=abs_path)
    else:
        # Try relative to the current working directory if absolute didn't exist
        # log.warning("Service account file not found", path=abs_path)
        pass
