import json
import os
from typing import Any

import faiss
import numpy as np


class FaissIndexStore:
    def __init__(self, index_dir: str = "storage/index"):
        self.index_dir = index_dir
        self.index_path = os.path.join(index_dir, "chunks.index")
        self.meta_path = os.path.join(index_dir, "chunks_meta.json")

        os.makedirs(index_dir, exist_ok=True)

    def save(self, embeddings: list[list[float]], metadata: list[dict[str, Any]]) -> None:
        if not embeddings:
            raise ValueError("No embeddings to save")

        vectors = np.array(embeddings, dtype="float32")
        dim = vectors.shape[1]

        index = faiss.IndexFlatIP(dim)
        index.add(vectors)

        faiss.write_index(index, self.index_path)

        with open(self.meta_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)

    def load(self):
        if not os.path.exists(self.index_path):
            raise FileNotFoundError("FAISS index not found")

        if not os.path.exists(self.meta_path):
            raise FileNotFoundError("Metadata file not found")

        index = faiss.read_index(self.index_path)

        with open(self.meta_path, "r", encoding="utf-8") as f:
            metadata = json.load(f)

        return index, metadata