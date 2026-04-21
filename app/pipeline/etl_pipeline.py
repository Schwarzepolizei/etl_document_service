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

from app.parsers.doc_parser import parse_doc
from app.parsers.pdf_parser import parse_pdf
from app.parsers.image_parser import parse_image
from app.parsers.pdf_ocr_parser import parse_scanned_pdf
from app.parsers.docx_parser import parse_docx
from app.services.ocr_extractor import build_ocr_line_blocks, merge_ocr_lines_to_paragraphs
from app.services.text_splitter import build_blocks_from_text, build_chunks_from_blocks, build_blocks_from_pages
from app.services.text_cleaner import clean_text
from app.services.quality_scorer import (
    compute_page_quality_score,
    compute_document_quality_score,
    get_quality_label,
)
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
    page_scores = []

    if file_type == "txt":
        full_text = clean_text(parse_txt(file_bytes))
        page_count = 1
        is_scanned = False
        extraction_method = "native"

        page_score = compute_page_quality_score(
            text=full_text,
            extraction_method="native",
            confidence=None,
        )
        page_scores = [page_score]

        pages = [
            Page(
                page_num=1,
                text=full_text,
                quality_score=page_score,
            )
        ]
        blocks = build_blocks_from_text(full_text)

    elif file_type == "docx":
        try:
            full_text = clean_text(parse_docx(file_bytes))
            page_count = 1
            is_scanned = False
            extraction_method = "native"

            page_score = compute_page_quality_score(
                text=full_text,
                extraction_method="native",
                confidence=None,
            )
            page_scores = [page_score]

            pages = [
                Page(
                    page_num=1,
                    text=full_text,
                    quality_score=page_score,
                )
            ]

            blocks = build_blocks_from_text(full_text)

        except Exception as e:
            errors.append(f"DOCX processing error: {type(e).__name__}: {str(e)}")

    elif file_type == "doc":
        try:
            full_text = clean_text(parse_doc(file_bytes))
            page_count = 1
            is_scanned = False
            extraction_method = "native"

            page_score = compute_page_quality_score(
                text=full_text,
                extraction_method="native",
                confidence=None,
            )
            page_scores = [page_score]

            pages = [
                Page(
                    page_num=1,
                    text=full_text,
                    quality_score=page_score,
                )
            ]

            blocks = build_blocks_from_text(full_text)

        except Exception as e:
            errors.append(f"DOC processing error: {type(e).__name__}: {str(e)}")

    elif file_type == "pdf":
        try:
            page_texts, page_count, has_text_layer = parse_pdf(file_bytes)

            if has_text_layer:
                is_scanned = False
                extraction_method = "native"
                cleaned_pages = [clean_text(p) for p in page_texts]
                page_confidences = [None] * len(cleaned_pages)
            else:
                page_texts, page_count, page_ocr_data, page_confidences = parse_scanned_pdf(file_bytes)
                is_scanned = True
                extraction_method = "ocr"
                cleaned_pages = [clean_text(p) for p in page_texts]

            full_text = "\n\n".join([p for p in cleaned_pages if p.strip()])

            if extraction_method == "ocr":
                pages = []
                page_scores = []

                for i, page_text in enumerate(cleaned_pages):
                    page_conf = page_confidences[i]
                    page_score = compute_page_quality_score(
                        text=page_text,
                        extraction_method="ocr",
                        confidence=page_conf,
                    )
                    page_scores.append(page_score)

                    pages.append(
                        Page(
                            page_num=i + 1,
                            text=page_text,
                            confidence=page_conf,
                            quality_score=page_score,
                        )
                    )
            else:
                pages = []
                page_scores = []

                for i, page_text in enumerate(cleaned_pages):
                    page_score = compute_page_quality_score(
                        text=page_text,
                        extraction_method="native",
                        confidence=None,
                    )
                    page_scores.append(page_score)

                    pages.append(
                        Page(
                            page_num=i + 1,
                            text=page_text,
                            quality_score=page_score,
                        )
                    )

            if extraction_method == "ocr":
                blocks = []
                paragraph_index = 1

                for page_num, ocr_data in enumerate(page_ocr_data, start=1):
                    line_blocks = build_ocr_line_blocks(
                        ocr_data,
                        page_num=page_num,
                        start_block_index=1,
                    )

                    paragraph_blocks = merge_ocr_lines_to_paragraphs(line_blocks)

                    for block in paragraph_blocks:
                        block.block_id = f"b{paragraph_index}"
                        block.block_order = paragraph_index
                        blocks.append(block)
                        paragraph_index += 1
            else:
                blocks = build_blocks_from_pages(cleaned_pages)

        except Exception as e:
            errors.append(f"PDF processing error: {type(e).__name__}: {str(e)}")

    elif file_type == "image":
        try:
            raw_text, _, avg_conf, ocr_data = parse_image(file_bytes)
            full_text = clean_text(raw_text)
            page_count = 1
            is_scanned = True
            extraction_method = "ocr"

            page_score = compute_page_quality_score(
                text=full_text,
                extraction_method="ocr",
                confidence=avg_conf,
            )
            page_scores = [page_score]

            pages = [
                Page(
                    page_num=1,
                    text=full_text,
                    confidence=avg_conf,
                    quality_score=page_score,
                )
            ]

            line_blocks = build_ocr_line_blocks(ocr_data, page_num=1) if ocr_data else []
            blocks = merge_ocr_lines_to_paragraphs(line_blocks) if line_blocks else []

        except Exception as e:
            errors.append(f"Image processing error: {type(e).__name__}: {str(e)}")

    else:
        warnings.append(f"Parser for file type '{file_type}' is not implemented yet.")

    if extraction_method == "ocr":
        chunks = build_chunks_from_blocks(blocks, mode="ocr")
    else:
        chunks = build_chunks_from_blocks(blocks, mode="native")
    duration_ms = int((time.time() - started) * 1000)
    text_extracted = bool(full_text.strip())

    document_quality_score = compute_document_quality_score(page_scores) if pages else 0.0
    document_quality_label = get_quality_label(document_quality_score)

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
            quality_score=document_quality_score,
            quality_label=document_quality_label,
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