from sentence_transformers import SentenceTransformer


class EmbeddingService:
    def __init__(self, model_name: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"):
        print(f"Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)
        print("Embedding model loaded")

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []

        embeddings = self.model.encode(
            texts,
            normalize_embeddings=True,
            convert_to_numpy=True,
        )
        return embeddings.tolist()

    def embed_query(self, text: str) -> list[float]:
        embedding = self.model.encode(
            [text],
            normalize_embeddings=True,
            convert_to_numpy=True,
        )[0]
        return embedding.tolist()