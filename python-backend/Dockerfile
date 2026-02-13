# Hugging Face Spaces Docker Image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies including FFmpeg
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libsndfile1 \
    git \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app.py .
COPY config.py .
COPY document_generator.py .
COPY meeting_summarizer.py .

# Create uploads directory
RUN mkdir -p uploads

# Expose port (Hugging Face uses 7860)
EXPOSE 7860

# Set environment variables
ENV PORT=7860
ENV FLASK_HOST=0.0.0.0
ENV PYTHONUNBUFFERED=1

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:7860/api/health || exit 1

# Run the application with gunicorn for production
CMD ["gunicorn", "--bind", "0.0.0.0:7860", "--timeout", "300", "--workers", "1", "--threads", "4", "app:app"]
