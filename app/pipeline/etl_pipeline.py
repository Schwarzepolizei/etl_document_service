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
from app.services.text_splitter import build_blocks_from_text, build_chunks_from_blocks
from app.utils.file_types import detect_file_type


def run_etl(file_name: str, file_bytes: bytes) -> ETLResponse:
    started = time.time()
    doc_id = str(uuid.uuid4())
    file_type = detect_file_type(file_name)

    warnings = []
    errors = []

    if file_type == "txt":
        text = parse_txt(file_bytes)
        is_scanned = False
        has_text_layer = True
    else:
        text = "Формат пока не поддерживается"
        warnings.append(f"Parser for file type '{file_type}' is not implemented yet.")
        is_scanned = False
        has_text_layer = False

    blocks = build_blocks_from_text(text)
    chunks = build_chunks_from_blocks(blocks)

    duration_ms = int((time.time() - started) * 1000)

    return ETLResponse(
        document_id=doc_id,
        source=SourceMeta(
            file_name=file_name,
            file_type=file_type,
        ),
        document=DocumentMeta(
            language=["ru"],
            page_count=1,
            is_scanned=is_scanned,
            has_text_layer=has_text_layer,
        ),
        content=Content(
            full_text=text,
            pages=[
                Page(
                    page_num=1,
                    text=text,
                )
            ],
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