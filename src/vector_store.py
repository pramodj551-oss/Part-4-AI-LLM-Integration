"""FAISS vector store with safe JSON document persistence."""
from pathlib import Path
import json

import faiss
import numpy as np

from src.logger import get_logger
from src.config import FAISS_INDEX_PATH, DOCUMENTS_PATH

logger = get_logger()


class VectorStore:
    """Store FAISS vectors and trusted string documents."""

    def __init__(self):
        self.index = None
        self.documents = []
        logger.info("VectorStore initialized.")

    def build_index(self, embeddings, documents):
        if embeddings is None:
            raise ValueError("Embeddings cannot be None.")
        vectors = np.asarray(embeddings, dtype=np.float32)
        if vectors.ndim != 2:
            raise ValueError("Embeddings must be 2-dimensional.")
        if len(vectors) == 0:
            raise ValueError("Embedding matrix is empty.")
        if len(vectors) != len(documents):
            raise ValueError("Embeddings and documents must have the same length.")
        if any(not isinstance(document, str) for document in documents):
            raise TypeError("All documents must be strings.")
        if not np.isfinite(vectors).all():
            raise ValueError("Embeddings contain non-finite values.")

        self.index = faiss.IndexFlatL2(vectors.shape[1])
        self.index.add(vectors)
        self.documents = list(documents)
        return self

    def save(self):
        if self.index is None:
            raise RuntimeError("Vector index has not been built.")
        Path(FAISS_INDEX_PATH).parent.mkdir(parents=True, exist_ok=True)
        faiss.write_index(self.index, str(FAISS_INDEX_PATH))
        with open(DOCUMENTS_PATH, "w", encoding="utf-8") as file:
            json.dump(self.documents, file, ensure_ascii=False, indent=2)
        return self

    def load(self):
        index_path = Path(FAISS_INDEX_PATH)
        documents_path = Path(DOCUMENTS_PATH)
        if not index_path.exists():
            raise FileNotFoundError(f"FAISS index not found: {index_path}")
        if not documents_path.exists():
            raise FileNotFoundError(f"Documents file not found: {documents_path}")

        self.index = faiss.read_index(str(index_path))
        with open(documents_path, "r", encoding="utf-8") as file:
            documents = json.load(file)
        if not isinstance(documents, list) or any(not isinstance(item, str) for item in documents):
            raise ValueError("Documents store must contain a JSON list of strings.")
        if self.index.ntotal != len(documents):
            raise ValueError("FAISS index and documents store are inconsistent.")
        self.documents = documents
        return self

    def similarity_search(self, query_embedding, top_k=5):
        if self.index is None:
            raise RuntimeError("Vector Store is not loaded.")
        if not isinstance(top_k, int) or top_k < 1:
            raise ValueError("top_k must be a positive integer.")
        if self.index.ntotal == 0:
            return []
        top_k = min(top_k, self.index.ntotal)
        query_vector = np.asarray([query_embedding], dtype=np.float32)
        if query_vector.ndim != 2 or query_vector.shape[1] != self.index.d:
            raise ValueError("Query embedding dimension does not match the FAISS index.")
        if not np.isfinite(query_vector).all():
            raise ValueError("Query embedding contains non-finite values.")
        distances, indices = self.index.search(query_vector, top_k)
        return [
            {"document": self.documents[index], "distance": float(distance), "index": int(index)}
            for distance, index in zip(distances[0], indices[0])
            if index >= 0
        ]

    def get_index_info(self):
        if self.index is None:
            return {"loaded": False, "documents": 0, "vectors": 0, "dimension": 0}
        return {
            "loaded": True,
            "documents": len(self.documents),
            "vectors": self.index.ntotal,
            "dimension": self.index.d,
        }


if __name__ == "__main__":
    logger.info("Vector store module loaded successfully.")
