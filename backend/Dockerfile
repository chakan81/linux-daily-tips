# Multi-stage Dockerfile for FastAPI Backend
# Production and CI optimized with uv

# Base image with Python 3.12
FROM python:3.12-slim-bullseye as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    libpq-dev \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install uv (ultra-fast Python package installer)
RUN curl -LsSf https://astral.sh/uv/install.sh | sh && \
    mv /root/.local/bin/uv /usr/local/bin/uv && \
    mv /root/.local/bin/uvx /usr/local/bin/uvx

WORKDIR /app

# Copy dependency files
COPY pyproject.toml README.md ./

# Development stage
FROM base as development

# Install all dependencies including dev and test
RUN uv pip install --system --no-cache -e ".[dev,test]"

# Copy source code
COPY . .

# Expose port
EXPOSE 8000

# Development command
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# Testing stage (for CI)
FROM base as testing

# Install all dependencies including dev and test
RUN uv pip install --system --no-cache -e ".[dev,test]"

# Copy source code
COPY . .

# Set up test environment
ENV ENVIRONMENT=testing

# Production stage
FROM base as production

# Install only production dependencies
RUN uv pip install --system --no-cache --no-dev .

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Copy source code
COPY --chown=appuser:appuser . .

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Production command
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]