import os
import atexit
import logging
from datetime import datetime
import structlog
from google.cloud import storage
from config.settings import settings

def add_severity(logger, method_name, event_dict):
    """Copy the log level into a field called "severity".

    Cloud Logging (which collects Cloud Run's output) recognises "severity" in a JSON
    log line and uses it to colour and filter entries. Our own "level" field is kept
    too, so nothing that reads "level" breaks.
    """
    level = event_dict.get("level")
    if level:
        event_dict["severity"] = level.upper()
    return event_dict


class CustomLogger:
    def __init__(self, log_dir="logs"):
        # Ensure logs directory exists
        self.logs_dir = os.path.join(os.getcwd(), log_dir)
        os.makedirs(self.logs_dir, exist_ok=True)

        # Timestamped log file (for persistence)
        self._timestamp = datetime.now().strftime('%m_%d_%Y_%H_%M_%S')
        log_file = f"{self._timestamp}.log"
        self.log_file_path = os.path.join(self.logs_dir, log_file)

        self._gcs_flushed = False

        # Register atexit to auto-flush logs to GCS on shutdown
        atexit.register(self.flush_to_gcs)

    def get_logger(self, name=__file__):
        logger_name = os.path.basename(name)

        # Configure logging for console + file (both JSON)
        file_handler = logging.FileHandler(self.log_file_path)
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(logging.Formatter("%(message)s"))  # Raw JSON lines

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(logging.Formatter("%(message)s"))

        logging.basicConfig(
            level=logging.INFO,
            format="%(message)s",  # Structlog will handle JSON rendering
            handlers=[console_handler, file_handler]
        )

        # Configure structlog for JSON structured logging
        structlog.configure(
            processors=[
                structlog.processors.TimeStamper(fmt="iso", utc=True, key="timestamp"),
                structlog.processors.add_log_level,
                add_severity,
                structlog.processors.EventRenamer(to="event"),
                structlog.processors.JSONRenderer()
            ],
            logger_factory=structlog.stdlib.LoggerFactory(),
            cache_logger_on_first_use=True,
        )

        return structlog.get_logger(logger_name)

    def flush_to_gcs(self):
        """Upload the current log file to GCS. Safe to call multiple times."""
        if self._gcs_flushed:
            return

        try:
            
            gcs_bucket = settings.GCS_BUCKET_NAME
            gcp_project = settings.GCP_PROJECT
        except Exception:
            # Fallback for environments lacking the settings module
            gcs_bucket = os.environ.get("GCS_BUCKET_NAME", "")
            gcp_project = os.environ.get("GCP_PROJECT_ID", "")

        if not gcs_bucket:
            print("[Logger] GCS_BUCKET_NAME not set — skipping GCS log upload.")
            return

        if not os.path.exists(self.log_file_path):
            print("[Logger] Log file not found — skipping GCS log upload.")
            return

        try:
            client = storage.Client(project=gcp_project or None)
            bucket = client.bucket(gcs_bucket)
            gcs_path = f"logs/{self._timestamp}.log"
            blob = bucket.blob(gcs_path)
            blob.upload_from_filename(self.log_file_path, content_type="text/plain")

            self._gcs_flushed = True
            print(f"[Logger] Logs uploaded to gs://{gcs_bucket}/{gcs_path}")
        except Exception as e:
            # Use print here intentionally — the structlog logger may not be
            # available during shutdown, and we don't want to lose this error
            print(f"[Logger] Failed to upload logs to GCS: {e}")
