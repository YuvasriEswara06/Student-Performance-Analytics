# Dockerfile for Student Performance Analytics Portal
# Multi-stage production container image targeting AWS ECS (Express Mode / Fargate)

FROM python:3.11-slim

# Prevent Python from writing .pyc files and enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8501

WORKDIR /app

# Install system dependencies required for OpenCV and PostgreSQL
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgl1-mesa-glx \
    libglib2.0-0 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency specifications first to leverage Docker layer caching
COPY requirements.txt ./

# Install Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code and assets
COPY . .

# Create non-root system user for security best practices
RUN useradd -m -u 1000 appuser && \
    mkdir -p /app/registered_faces && \
    chown -R appuser:appuser /app

USER appuser

EXPOSE 8501

# Healthcheck endpoint targeting Streamlit's health endpoint
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Launch Streamlit server in headless mode on 0.0.0.0:8501
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.headless=true"]
