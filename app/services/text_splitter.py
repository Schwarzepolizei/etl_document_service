from app.schemas.document import Block, Chunk


def guess_block_type(paragraph: str, is_first: bool = False) -> str:
    text = paragraph.strip()

    if not text:
        return "unknown"

    if is_first and len(text) < 80 and "\n" not in text and text.count(".") <= 1:
        return "title"

    return "paragraph"


def build_blocks_from_text(text: str) -> list[Block]:
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    blocks = []

    for idx, paragraph in enumerate(paragraphs, start=1):
        block_type = guess_block_type(paragraph, is_first=(idx == 1))

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


def build_blocks_from_pages(page_texts: list[str]) -> list[Block]:
    blocks = []
    block_counter = 1

    for page_num, page_text in enumerate(page_texts, start=1):
        paragraphs = [p.strip() for p in page_text.split("\n\n") if p.strip()]

        for paragraph in paragraphs:
            block_type = guess_block_type(paragraph, is_first=(block_counter == 1))

            blocks.append(
                Block(
                    block_id=f"b{block_counter}",
                    page_num=page_num,
                    block_order=block_counter,
                    block_type=block_type,
                    text=paragraph,
                    confidence=1.0,
                )
            )
            block_counter += 1

    return blocks


def build_chunks_from_blocks(
    blocks: list[Block],
    max_chars: int = 1200,
    soft_min_chars: int = 400,
) -> list[Chunk]:
    if not blocks:
        return []

    chunks = []
    current_blocks = []
    chunk_order = 1

    def flush_chunk(block_group: list[Block], chunk_order: int) -> Chunk | None:
        if not block_group:
            return None

        texts = [b.text.strip() for b in block_group if b.text.strip()]
        if not texts:
            return None

        chunk_text = "\n\n".join(texts)
        page_nums = sorted({b.page_num for b in block_group})
        block_types = [b.block_type for b in block_group]

        return Chunk(
            chunk_id=f"c{chunk_order}",
            chunk_order=chunk_order,
            block_ids=[b.block_id for b in block_group],
            text=chunk_text,
            page_span=page_nums,
            block_types=block_types,
            char_count=len(chunk_text),
        )

    for block in blocks:
        if not block.text.strip():
            continue

        candidate_blocks = current_blocks + [block]
        candidate_text = "\n\n".join(b.text.strip() for b in candidate_blocks if b.text.strip())

        if not current_blocks:
            current_blocks.append(block)
            continue

        prev_block = current_blocks[-1]
        page_changed = prev_block.page_num != block.page_num
        is_title_block = block.block_type in {"title", "section_header"}
        exceeds_limit = len(candidate_text) > max_chars

        should_flush = False

        if exceeds_limit:
            should_flush = True
        elif page_changed and len("\n\n".join(b.text for b in current_blocks)) >= soft_min_chars:
            should_flush = True
        elif is_title_block and len("\n\n".join(b.text for b in current_blocks)) >= soft_min_chars:
            should_flush = True

        if should_flush:
            chunk = flush_chunk(current_blocks, chunk_order)
            if chunk:
                chunks.append(chunk)
                chunk_order += 1
            current_blocks = [block]
        else:
            current_blocks.append(block)

    chunk = flush_chunk(current_blocks, chunk_order)
    if chunk:
        chunks.append(chunk)

    return chunks