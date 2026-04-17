import time
import uuid

from app.parsers.txt_parser import parse_txt
from app.schemas.document import (
    ETLResponse,
    SourceMeta,
    DocumentMeta,
    Content,
    Page,
    ProcessingInfo,
)

from app.parsers.pdf_parser import parse_pdf
from app.parsers.image_parser import parse_image
from app.parsers.pdf_ocr_parser import parse_scanned_pdf
from app.parsers.docx_parser import parse_docx
from app.services.text_splitter import build_blocks_from_text, build_chunks_from_blocks, build_blocks_from_pages
from app.utils.file_types import detect_file_type


def run_etl(file_name: str, file_bytes: bytes) -> ETLResponse:
    started = time.time()
    doc_id = str(uuid.uuid4())
    file_type = detect_file_type(file_name)

    warnings = []
    errors = []

    full_text = ""
    page_count = 0
    is_scanned = False
    extraction_method = "native"
    pages = []
    blocks = []

    if file_type == "txt":
        full_text = parse_txt(file_bytes)
        page_count = 1
        is_scanned = False
        extraction_method = "native"

        pages = [
            Page(
                page_num=1,
                text=full_text,
            )
        ]
        blocks = build_blocks_from_text(full_text)

    elif file_type == "docx":
        try:
            full_text = parse_docx(file_bytes)
            page_count = 1
            is_scanned = False
            extraction_method = "native"

            pages = [
                Page(
                    page_num=1,
                    text=full_text,
                )
            ]

            blocks = build_blocks_from_text(full_text)

        except Exception as e:
            errors.append(f"DOCX processing error: {type(e).__name__}: {str(e)}")

    elif file_type == "pdf":
        try:
            page_texts, page_count, has_text_layer = parse_pdf(file_bytes)

            if has_text_layer:
                is_scanned = False
                extraction_method = "native"
            else:
                page_texts, page_count = parse_scanned_pdf(file_bytes)
                is_scanned = True
                extraction_method = "ocr"

            full_text = "\n\n".join([p for p in page_texts if p.strip()])

            pages = [
                Page(
                    page_num=i + 1,
                    text=page_text,
                )
                for i, page_text in enumerate(page_texts)
            ]

            blocks = build_blocks_from_pages(page_texts)

        except Exception as e:
            errors.append(f"PDF processing error: {type(e).__name__}: {str(e)}")

    elif file_type == "image":
        try:
            full_text, _ = parse_image(file_bytes)
            page_count = 1
            is_scanned = True
            extraction_method = "ocr"

            pages = [
                Page(
                    page_num=1,
                    text=full_text,
                )
            ]

            blocks = build_blocks_from_text(full_text) if full_text else []

        except Exception as e:
            errors.append(f"Image processing error: {type(e).__name__}: {str(e)}")

    else:
        warnings.append(f"Parser for file type '{file_type}' is not implemented yet.")

    chunks = build_chunks_from_blocks(blocks)
    duration_ms = int((time.time() - started) * 1000)
    text_extracted = bool(full_text.strip())

    return ETLResponse(
        document_id=doc_id,
        source=SourceMeta(
            file_name=file_name,
            file_type=file_type,
        ),
        document=DocumentMeta(
            language=["ru"],
            page_count=page_count,
            is_scanned=is_scanned,
            extraction_method=extraction_method,
            text_extracted=text_extracted,
        ),
        content=Content(
            full_text=full_text,
            pages=pages,
            blocks=blocks,
            chunks=chunks,
        ),
        processing=ProcessingInfo(
            status="success" if not errors else "failed",
            pipeline_version="0.1.0",
            duration_ms=duration_ms,
            warnings=warnings,
            errors=errors,
        ),
    )