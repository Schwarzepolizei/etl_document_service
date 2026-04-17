import uuid
from app.schemas.document import ETLResponse, SourceMeta, DocumentMeta, Content, Page, Block, Chunk, ProcessingInfo


def run_etl(file_name: str) -> ETLResponse:
    doc_id = str(uuid.uuid4())

    text = "Это тестовый документ"

    return ETLResponse(
        document_id=doc_id,
        source=SourceMeta(
            file_name=file_name,
            file_type=file_name.split(".")[-1]
        ),
        document=DocumentMeta(
            language=["ru"],
            page_count=1,
            is_scanned=False,
            has_text_layer=True
        ),
        content=Content(
            full_text=text,
            pages=[
                Page(page_num=1, text=text)
            ],
            blocks=[
                Block(
                    block_id="b1",
                    page_num=1,
                    block_order=1,
                    block_type="paragraph",
                    text=text,
                    confidence=1.0
                )
            ],
            chunks=[
                Chunk(
                    chunk_id="c1",
                    chunk_order=1,
                    block_ids=["b1"],
                    text=text
                )
            ]
        ),
        processing=ProcessingInfo(
            status="success",
            pipeline_version="0.1"
        )
    )