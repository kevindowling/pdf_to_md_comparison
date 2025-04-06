import asyncio
import pathlib
import time
import logging

import pymupdf4llm
from docling.document_converter import DocumentConverter


from markitdown import MarkItDown

from marker.converters.pdf import PdfConverter
from marker.models import create_model_dict
from marker.output import text_from_rendered
import torch

# Explicit logging configuration to output to both file and console
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# File handler
file_handler = logging.FileHandler('app.log')
file_handler.setLevel(logging.INFO)
file_formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
console_handler.setFormatter(console_formatter)
logger.addHandler(console_handler)

# Conversion functions with progress tracking, telemetry, and exception handling.
def get_device_map() -> str:
    return 'cuda' if torch.cuda.is_available() else 'cpu'

def pdf_to_md_pymu(filename: str):
    start_time = time.perf_counter()
    try:
        logging.info("[pymupdf4llm] Starting conversion for %s", filename)
        md_text = pymupdf4llm.to_markdown(filename)
        output_path = pathlib.Path(f'pymupdf4llm/{pathlib.Path(filename).stem}.md')
        output_path.parent.mkdir(exist_ok=True, parents=True)
        output_path.write_bytes(md_text.encode())
        elapsed = time.perf_counter() - start_time
        logging.info("[pymupdf4llm] Completed conversion for %s in %.2f seconds", filename, elapsed)
    except Exception as e:
        logging.exception("[pymupdf4llm] Exception during conversion for %s: %s", filename, e)

def pdf_to_md_mid(filename: str):
    start_time = time.perf_counter()
    try:
        logging.info("[markitdown] Starting conversion for %s", filename)
        md = MarkItDown(enable_plugins=False)
        result = md.convert(filename)
        output_path = pathlib.Path(f'markitdown/{pathlib.Path(filename).stem}.md')
        output_path.parent.mkdir(exist_ok=True, parents=True)
        output_path.write_bytes(result.text_content.encode())
        elapsed = time.perf_counter() - start_time
        logging.info("[markitdown] Completed conversion for %s in %.2f seconds", filename, elapsed)
    except Exception as e:
        logging.exception("[markitdown] Exception during conversion for %s: %s", filename, e)

def pdf_to_md_docling(filename: str):
    start_time = time.perf_counter()
    try:
        logging.info("[docling] Starting conversion for %s", filename)
        converter = DocumentConverter()
        result = converter.convert(filename)
        output_path = pathlib.Path(f'docling/{pathlib.Path(filename).stem}.md')
        output_path.parent.mkdir(exist_ok=True, parents=True)
        output_path.write_bytes(result.document.export_to_markdown().encode())
        elapsed = time.perf_counter() - start_time
        logging.info("[docling] Completed conversion for %s in %.2f seconds", filename, elapsed)
    except Exception as e:
        logging.exception("[docling] Exception during conversion for %s: %s", filename, e)

def pdf_to_md_marker(filename: str):
    start_time = time.perf_counter()
    try:
        logging.info("[marker] Starting conversion for %s", filename)
        converter = PdfConverter(
            artifact_dict=create_model_dict(device=get_device_map()),
        )
        # Replace "FILEPATH" with the actual filename
        rendered = converter(filename)
        text, _, images = text_from_rendered(rendered)
        output_path = pathlib.Path(f'marker/{pathlib.Path(filename).stem}.md')
        output_path.parent.mkdir(exist_ok=True, parents=True)
        output_path.write_bytes(text.encode())
        elapsed = time.perf_counter() - start_time
        logging.info("[marker] Completed conversion for %s in %.2f seconds", filename, elapsed)
    except Exception as e:
        logging.exception("[marker] Exception during conversion for %s: %s", filename, e)



# Async wrapper to run the conversion functions concurrently for a single file.
def process_file(filename: str):
    file_start_time = time.perf_counter()
    logging.info("[process_file] Starting processing for %s", filename)

    pdf_to_md_pymu(filename)
    pdf_to_md_mid(filename)
    pdf_to_md_docling(filename)
    pdf_to_md_marker(filename)


    file_elapsed = time.perf_counter() - file_start_time
    logging.info("[process_file] Finished processing for %s in %.2f seconds", filename, file_elapsed)

def main():
    resources_path = pathlib.Path("resources")
    tasks = []

    # Glob for PDF files in the resources directory
    pdf_files = list(resources_path.glob("*.pdf"))
    if not pdf_files:
        logging.info("No PDF files found in the resources directory.")
        return

    logging.info("Found %d PDF file(s) in the resources directory.", len(pdf_files))
    for pdf_file in pdf_files:
        process_file(str(pdf_file))
    
    overall_start = time.perf_counter()
    # Run all conversion tasks concurrently
    #await asyncio.gather(*tasks)
    overall_elapsed = time.perf_counter() - overall_start
    logging.info("All files have been processed in %.2f seconds.", overall_elapsed)

if __name__ == "__main__":
    asyncio.run(main())
