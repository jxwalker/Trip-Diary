# Multi-stage Docker build for TripCraft AI Backend
# Production-optimized with security and performance features

# Build stage
FROM python:3.11-slim as builder

# Set build arguments
ARG BUILD_ENV=production
ARG BUILD_VERSION=latest

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt requirements-dev.txt ./

# Create virtual environment and install dependencies
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.11-slim as production

# Set labels for metadata
LABEL maintainer="TripCraft AI Team"
LABEL version="${BUILD_VERSION}"
LABEL environment="${BUILD_ENV}"
LABEL description="TripCraft AI Backend - Production Ready"

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user for security
RUN groupadd -r tripcraft && useradd -r -g tripcraft tripcraft

# Set working directory
WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p logs data uploads outputs backups && \
    chown -R tripcraft:tripcraft /app

# Set environment variables
ENV PYTHONPATH=/app/src
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV ENVIRONMENT=production

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Switch to non-root user
USER tripcraft

# Expose port
EXPOSE 8000

# Default command
CMD ["python", "main.py"]

# Development stage
FROM production as development

# Switch back to root for development tools
USER root

# Install development dependencies
RUN pip install --no-cache-dir -r requirements-dev.txt

# Install additional development tools
RUN apt-get update && apt-get install -y \
    vim \
    htop \
    && rm -rf /var/lib/apt/lists/*

# Set development environment
ENV ENVIRONMENT=development
ENV DEBUG=true

# Switch back to tripcraft user
USER tripcraft

# Development command with auto-reload
CMD ["python", "-m", "uvicorn", "src.api.app_factory:create_app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
