#!/bin/bash
set -e

# Start Ollama server in the background
/bin/ollama serve &
pid=$!

# Wait for Ollama API to be ready
echo "Waiting for Ollama API..."
sleep 5

# Pull the Typhoon OCR model if missing
echo "🔴 Retrieve Typhoon OCR model..."
/bin/ollama pull scb10x/typhoon-ocr-7b:latest >/dev/null 2>&1
echo "🟢 Done!"

# Run the model once to warm it up
echo "Warming up the model..."
/bin/ollama run scb10x/typhoon-ocr-7b "warmup" >/dev/null 2>&1 || true

# Wait for Ollama process to finish
wait $pid
