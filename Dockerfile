FROM python:3.11-slim-bullseye

# Set working directory
WORKDIR /app

# Copy requirements first (for caching)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8080

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8080/health')" || exit 1

# Run with gunicorn
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:8080", "--workers", "1", "--threads", "1", "--timeout", "30"]
