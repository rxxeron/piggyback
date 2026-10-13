# Dockerfile for Piggyback Web Workbench
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python requirements (excluding PyQt6 for headless web server)
COPY requirements.txt .
RUN pip install --no-cache-dir Pillow numpy streamlit pytest

# Copy application files
COPY core/ ./core/
COPY assets/ ./assets/
COPY tests/ ./tests/
COPY web_app.py .
COPY README.md .

# Expose Streamlit port
EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

ENTRYPOINT ["streamlit", "run", "web_app.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.headless=true"]
