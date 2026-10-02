"""The LLM used by both the RAG chain and the agents.

Gemini is called through the Gemini API with an API key (GOOGLE_API_KEY).
Embeddings (rag/embeddings.py) use Vertex AI with Google Cloud credentials instead,
so this project shows both ways of authenticating to Google's models.
"""
from functools import lru_cache

from langchain_google_genai import ChatGoogleGenerativeAI

from config.settings import settings


@lru_cache(maxsize=1)
def get_llm() -> ChatGoogleGenerativeAI:
    """Create the chat model on first use (not at import time) and reuse it afterwards."""
    return ChatGoogleGenerativeAI(
        model=settings.llm_model_name,
        google_api_key=settings.GOOGLE_API_KEY,
        temperature=settings.llm_temperature,
    )


def extract_text(content) -> str:
    """Gemini may return a list of content blocks, e.g. [{'type': 'text', 'text': '...'}]; join the text."""
    if isinstance(content, list):
        return "\n".join(
            block.get("text", "") for block in content
            if isinstance(block, dict) and block.get("type") == "text"
        )
    return content
