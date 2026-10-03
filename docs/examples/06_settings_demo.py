"""How the project reads its configuration. No cloud account needed.

Run:    python 06_settings_demo.py
Then:   GCP_REGION=europe-west1 python 06_settings_demo.py

Order of priority (highest first): environment variable -> .env file -> default in the code.
"""
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class DemoSettings(BaseSettings):
    region: str = Field("us-central1", validation_alias="GCP_REGION")
    model: str = Field("gemini-3.8-flash", validation_alias="VERTEX_LLM_MODEL_NAME")
    temperature: float = Field(0.0, validation_alias="LLM_TEMPERATURE")

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = DemoSettings()
print("region     :", settings.region)
print("model      :", settings.model)
print("temperature:", settings.temperature, f"(type: {type(settings.temperature).__name__})")
print("\nNote that the text '0.0' from an environment variable became a real float.")
