# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements-railway.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements-railway.txt

# Copy application code
COPY backend/ ./backend/
COPY src/ ./src/
COPY data/ ./data/
COPY knowledge/ ./knowledge/
COPY pyproject.toml .
COPY validate_deployment.py .

# Create outputs directory
RUN mkdir -p outputs /tmp/outputs

# Validate the deployment setup (optional - comment out if causing issues)
# RUN python validate_deployment.py || echo "Warning: Validation failed but continuing..."

# Expose port
EXPOSE 8080

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=8080
ENV PYTHONPATH=/app

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/health', timeout=5)" || exit 1

# Run the application
CMD gunicorn backend.main:app --bind 0.0.0.0:$PORT --timeout 300 --workers 1 --log-level info
