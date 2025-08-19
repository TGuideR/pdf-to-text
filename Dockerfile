FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    poppler-utils \
    libpoppler-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Install Python dependencies
RUN pip install --no-cache-dir \
    openai \
    typhoon-ocr \
    pathlib \
    PyPDF2

# Create necessary directories
RUN mkdir -p /app/doc /app/doc_text

# Copy the Python script
COPY converter.py /app/

# Make sure the script is executable
RUN chmod +x /app/converter.py

# Default command
CMD ["python", "converter.py"]