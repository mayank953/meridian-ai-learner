FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend

COPY frontend/package.json frontend/package-lock.json* ./
# Use npm ci if package-lock is present, else install
RUN if [ -f package-lock.json ]; then npm ci; else npm install; fi

COPY frontend/ ./
RUN npm run build


FROM python:3.12-slim AS backend-builder
WORKDIR /app

# Set environment variables for Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies if required by some Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend application code
COPY backend/ ./backend/

# Copy environment variables and credentials (Uncomment during local development)
# COPY .env ./
# COPY credentials/ ./credentials/

# Copy built frontend static files from the frontend-builder stage
COPY --from=frontend-builder /app/frontend/dist /app/frontend/dist

# Expose the single port Cloud Run / local test will use
EXPOSE 8080

# Start the application using Uvicorn
# Use shell form to allow environment variable expansion for PORT
CMD uvicorn api.main:app --app-dir backend --host 0.0.0.0 --port ${PORT:-8080}

