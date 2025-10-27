FROM python:3.10-slim

# Install OS-level dependencies required by OpenCV and video processing
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    ffmpeg \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python deps
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

ENV PORT 8080
EXPOSE 8080

# Run with gunicorn in production
CMD ["gunicorn", "app:app", "-b", "0.0.0.0:8080", "--workers", "2"]
