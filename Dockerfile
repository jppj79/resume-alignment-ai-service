# --- Stage 1: Builder ---
# Use Python 3.13 slim as builder image
FROM python:3.13.7-slim AS builder

# Install minimal build tools (in case some package requires compilation)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc \
    && rm -rf /var/lib/apt/lists/*

# Install pip tools for building wheels
RUN pip install --no-cache-dir wheel

# Set working directory
WORKDIR /app

# Copy only requirements first to leverage Docker layer caching
COPY requirements.txt .

# Build wheels for all dependencies into /wheels directory
RUN pip wheel --no-cache-dir -r requirements.txt -w /wheels

# --- Stage 2: Runtime ---
# Use a clean Python 3.13 slim image for the runtime
FROM python:3.13.7-slim

# Set working directory
WORKDIR /app

# Create a non-root user for better security
RUN useradd -m appuser

# Copy wheels from builder and install dependencies from local wheels only
COPY --from=builder /wheels /wheels
RUN pip install --no-cache-dir --no-index --find-links=/wheels /wheels/* \
    && rm -rf /wheels

# Install curl for healthcheck
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Copy application source code
COPY ./app /app/app

# Switch to non-root user
USER appuser

# Internal FastAPI port
ENV PORT=8000
EXPOSE $PORT

# Default command to run the application
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port $PORT"]
