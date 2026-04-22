from typing import Any

import numpy as np

from app.rag.embedder import EmbeddingService
from app.rag.index_store import FaissIndexStore


class Retriever:
    def __init__(self):
        self.embedder = EmbeddingService()
        self.store = FaissIndexStore()

    def search(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        index, metadata = self.store.load()

        query_vector = np.array([self.embedder.embed_query(query)], dtype="float32")
        scores, indices = index.search(query_vector, top_k)

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < 0 or idx >= len(metadata):
                continue

            item = metadata[idx].copy()
            item["score"] = float(score)
            results.append(item)

        return results