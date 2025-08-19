#!/usr/bin/env python3
"""
PDF to Text Converter using Typhoon OCR + Ollama
Converts PDF files to text using typhoon_ocr.prepare_ocr_messages
and OpenAI API compatible with Ollama.
"""

import os
import sys
import time
import logging
from pathlib import Path
from openai import OpenAI
from typhoon_ocr import prepare_ocr_messages
# importing PyPDF2 library
import PyPDF2

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class TyphoonOCRConverter:
    def __init__(self,
                 ollama_host: str = "localhost",
                 ollama_port: int = 11434,
                 model_name: str = "scb10x/typhoon-ocr-7b:latest"):
        """
        Initialize the converter with Ollama + Typhoon OCR model.
        """
        self.model_name = model_name
        self.client = OpenAI(
            base_url=f"http://{ollama_host}:{ollama_port}/v1",
            api_key="not-needed"
        )

    def convert_pdf_to_text(self, pdf_path: str, output_path: str) -> bool:
        """
        Convert a single PDF into a text file.
        """
        try:
            logger.info(f"Processing: {pdf_path}")
            # opened file as reading (r) in binary (b) mode
            file = open(pdf_path,
                        'rb')

            # store data in pdfReader
            pdfReader = PyPDF2.PdfReader(file)

            # count number of pages
            totalPages = len(pdfReader.pages)

            # Always OCR page 1 (typhoon_ocr currently supports page_num=1)
            messages = prepare_ocr_messages(
                pdf_or_image_path=pdf_path,
                task_type="default",  # or "structure" if you want table format preserved
                page_num=totalPages
            )

            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                max_tokens=16000,
                extra_body={
                    "repetition_penalty": 1.2,
                    "temperature": 0.1,
                    "top_p": 0.6,
                },
            )

            text = response.choices[0].message.content.strip()

            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(text)

            logger.info(f"Converted -> {output_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to convert {pdf_path}: {e}")
            return False

    def batch_convert(self, input_dir: str, output_dir: str) -> dict:
        """
        Convert all PDFs in a folder.
        """
        input_path = Path(input_dir)
        output_path = Path(output_dir)

        if not input_path.exists():
            return {"success": 0, "failed": 0, "errors": [f"Input dir not found: {input_dir}"]}

        pdf_files = list(input_path.glob("*.pdf"))
        if not pdf_files:
            return {"success": 0, "failed": 0, "errors": ["No PDF files found"]}

        results = {"success": 0, "failed": 0, "errors": []}
        total_start = time.time()

        for i, pdf_file in enumerate(pdf_files, 1):
            logger.info(f"[{i}/{len(pdf_files)}] {pdf_file.name}")
            text_file = output_path / f"{pdf_file.stem}.txt"

            if self.convert_pdf_to_text(str(pdf_file), str(text_file)):
                results["success"] += 1
            else:
                results["failed"] += 1
                results["errors"].append(str(pdf_file))

        logger.info(f"Batch done in {time.time() - total_start:.2f}s")
        return results


def main():
    DOC_DIR = "/app/doc"
    DOC_TEXT_DIR = "/app/doc_text"
    OLLAMA_HOST = os.getenv("OLLAMA_HOST", "localhost")
    OLLAMA_PORT = int(os.getenv("OLLAMA_PORT", "11434"))
    MODEL_NAME = os.getenv("MODEL_NAME", "scb10x/typhoon-ocr-7b:latest")

    print("="*60)
    print("PDF to Text Converter using Typhoon OCR + Ollama")
    print("="*60)
    print(f"Ollama Server: {OLLAMA_HOST}:{OLLAMA_PORT}")
    print(f"Model: {MODEL_NAME}")
    print(f"Input dir: {DOC_DIR}")
    print(f"Output dir: {DOC_TEXT_DIR}")
    print("="*60)

    if not os.path.exists(DOC_DIR):
        logger.error(f"Input dir missing: {DOC_DIR}")
        sys.exit(1)

    converter = TyphoonOCRConverter(
        ollama_host=OLLAMA_HOST,
        ollama_port=OLLAMA_PORT,
        model_name=MODEL_NAME
    )

    results = converter.batch_convert(DOC_DIR, DOC_TEXT_DIR)

    print("\nRESULTS")
    print("-"*50)
    print(f"Success: {results['success']} | Failed: {results['failed']}")
    if results["errors"]:
        print("Errors:")
        for e in results["errors"]:
            print("  -", e)


if __name__ == "__main__":
    main()
