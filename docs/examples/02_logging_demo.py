"""Structured logging, the same style Meridian uses (structlog -> JSON lines).

Run:    python 02_logging_demo.py

Compare the two outputs. The first is easy for a person to read but hard for a
program to search. The second is one JSON object per line: every field can be
filtered, counted and graphed (Cloud Logging does exactly that).
"""
import logging
import sys

import structlog

# ---- 1. Plain text logging ------------------------------------------------------
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s", stream=sys.stdout)
plain = logging.getLogger("plain")
plain.info("Loaded PDF from GCS blob=policy.pdf pages=12")

# ---- 2. Structured logging (what the project does) ------------------------------
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso", utc=True, key="timestamp"),
        structlog.processors.add_log_level,
        structlog.processors.EventRenamer(to="event"),
        structlog.processors.JSONRenderer(),
    ],
    logger_factory=structlog.PrintLoggerFactory(file=sys.stdout),
)
log = structlog.get_logger("demo")

log.info("Loaded PDF from GCS", blob="policy.pdf", pages=12)          # INFO: normal progress
log.warning("No chunks extracted, skipping indexing", filename="scan.pdf")  # WARNING: odd but handled
try:
    1 / 0
except ZeroDivisionError as e:
    log.error("Upload failed", error=str(e))                           # ERROR: something broke

# Levels in order of severity:  DEBUG < INFO < WARNING < ERROR < CRITICAL
# A logger set to INFO shows INFO and above, and hides DEBUG.
