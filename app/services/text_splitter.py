from app.schemas.document import Block, Chunk


def build_blocks_from_text(text: str) -> list[Block]:
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    blocks = []

    for idx, paragraph in enumerate(paragraphs, start=1):
        block_type = "title" if idx == 1 and len(paragraph) < 120 else "paragraph"

        blocks.append(
            Block(
                block_id=f"b{idx}",
                page_num=1,
                block_order=idx,
                block_type=block_type,
                text=paragraph,
                confidence=1.0,
            )
        )

    return blocks


def build_chunks_from_blocks(blocks: list[Block], max_chars: int = 1000) -> list[Chunk]:
    chunks = []
    current_text = []
    current_ids = []
    chunk_order = 1

    for block in blocks:
        candidate_parts = current_text + [block.text]
        candidate_text = "\n\n".join(candidate_parts)

        if len(candidate_text) <= max_chars:
            current_text.append(block.text)
            current_ids.append(block.block_id)
        else:
            if current_text:
                chunks.append(
                    Chunk(
                        chunk_id=f"c{chunk_order}",
                        chunk_order=chunk_order,
                        block_ids=current_ids.copy(),
                        text="\n\n".join(current_text),
                    )
                )
                chunk_order += 1

            current_text = [block.text]
            current_ids = [block.block_id]

    if current_text:
        chunks.append(
            Chunk(
                chunk_id=f"c{chunk_order}",
                chunk_order=chunk_order,
                block_ids=current_ids.copy(),
                text="\n\n".join(current_text),
            )
        )

    return chunks