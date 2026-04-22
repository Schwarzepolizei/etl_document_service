from pydantic import BaseModel
from typing import Any


class SearchRequest(BaseModel):
    query: str
    top_k: int = 5


class IndexResponse(BaseModel):
    status: str
    indexed_chunks: int
    document_id: str | None = None
    file_name: str | None = None


class SearchResult(BaseModel):
    document_id: str | None = None
    file_name: str | None = None
    chunk_id: str | None = None
    chunk_order: int | None = None
    text: str
    page_span: list[int] = []
    block_types: list[str] = []
    char_count: int = 0
    score: float


class SearchResponse(BaseModel):
    query: str
    top_k: int
    results: list[SearchResult]