"""Test setup: fake config so the tests run without Google Cloud or a Gemini key."""
import os
import sys

# Make `import api`, `import rag`, ... work when pytest is run from the project root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

os.environ.setdefault("GOOGLE_API_KEY", "test-key")
os.environ.setdefault("GCP_PROJECT_ID", "test-project")
os.environ.setdefault("GCP_REGION", "us-central1")
# Empty on purpose: the logger skips its upload-logs-to-GCS-on-exit step when no bucket is set
os.environ["GCS_BUCKET_NAME"] = ""
os.environ.setdefault("GCS_PREFIX", "uploads/")
