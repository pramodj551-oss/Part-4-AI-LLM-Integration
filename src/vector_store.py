"""
==========================================================
Incident Knowledge Assistant (RAG)

vector_store.py

Author : Pramod Prakash Jadhav
==========================================================

Production-ready FAISS Vector Store
with automatic index creation support.
"""

from pathlib import Path
import pickle

import faiss
import numpy as np

from src.logger import get_logger
from src.config import (
    FAISS_INDEX_PATH,
    DOCUMENTS_PATH,
)

logger = get_logger()


class VectorStore:
    """
    Production-ready FAISS Vector Store.
    """

    def __init__(self):
        """
        Initialize Vector Store.
        """

        self.index = None
        self.documents = []

        logger.info("=" * 60)
        logger.info("VectorStore initialized.")
        logger.info("=" * 60)

    # ======================================================
    # Build Index
    # ======================================================

    def build_index(
        self,
        embeddings,
        documents,
    ):
        """
        Build FAISS index from embeddings.

        Parameters
        ----------
        embeddings : numpy.ndarray

        documents : list[str]

        Returns
        -------
        VectorStore
        """

        logger.info("=" * 60)
        logger.info("Building FAISS Index")
        logger.info("=" * 60)

        if embeddings is None:

            raise ValueError(
                "Embeddings cannot be None."
            )

        vectors = np.asarray(
            embeddings,
            dtype=np.float32,
        )

        if vectors.ndim != 2:

            raise ValueError(
                "Embeddings must be 2-dimensional."
            )

        if len(vectors) == 0:

            raise ValueError(
                "Embedding matrix is empty."
            )

        dimension = vectors.shape[1]

        logger.info(
            f"Embedding Dimension : {dimension}"
        )

        logger.info(
            f"Documents : {len(documents)}"
        )

        self.index = faiss.IndexFlatL2(
            dimension
        )

        self.index.add(vectors)

        self.documents = list(documents)

        logger.info(
            f"Vectors Indexed : "
            f"{self.index.ntotal}"
        )

        logger.info(
            "FAISS index built successfully."
        )

        return self
            # ======================================================
    # Save Vector Store
    # ======================================================

    def save(self):
        """
        Save FAISS index and documents.
        """

        logger.info("=" * 60)
        logger.info("Saving Vector Store")
        logger.info("=" * 60)

        if self.index is None:

            raise RuntimeError(
                "Vector index has not been built."
            )

        Path(
            FAISS_INDEX_PATH
        ).parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        faiss.write_index(
            self.index,
            str(FAISS_INDEX_PATH),
        )

        with open(
            DOCUMENTS_PATH,
            "wb",
        ) as file:

            pickle.dump(
                self.documents,
                file,
            )

        logger.info(
            "Vector Store saved successfully."
        )

        logger.info(
            f"Index : {FAISS_INDEX_PATH}"
        )

        logger.info(
            f"Documents : {DOCUMENTS_PATH}"
        )

        return self

    # ======================================================
    # Load Vector Store
    # ======================================================

    def load(self):
        """
        Load FAISS index and documents.
        """

        logger.info("=" * 60)
        logger.info("Loading Vector Store")
        logger.info("=" * 60)

        if not Path(
            FAISS_INDEX_PATH
        ).exists():

            raise FileNotFoundError(
                f"FAISS index not found: "
                f"{FAISS_INDEX_PATH}"
            )

        if not Path(
            DOCUMENTS_PATH
        ).exists():

            raise FileNotFoundError(
                f"Documents file not found: "
                f"{DOCUMENTS_PATH}"
            )

        self.index = faiss.read_index(
            str(FAISS_INDEX_PATH)
        )

        with open(
            DOCUMENTS_PATH,
            "rb",
        ) as file:

            self.documents = pickle.load(
                file
            )

        logger.info(
            f"Loaded vectors : "
            f"{self.index.ntotal}"
        )

        logger.info(
            f"Loaded documents : "
            f"{len(self.documents)}"
        )

        logger.info(
            "Vector Store loaded successfully."
        )

        return self
            # ======================================================
    # Similarity Search
    # ======================================================

    def similarity_search(
        self,
        query_embedding,
        top_k=5,
    ):
        """
        Perform similarity search.
        """

        if self.index is None:

            raise RuntimeError(
                "Vector Store is not loaded."
            )

        query_vector = np.asarray(
            [query_embedding],
            dtype=np.float32,
        )

        distances, indices = self.index.search(
            query_vector,
            top_k,
        )

        results = []

        for distance, index in zip(
            distances[0],
            indices[0],
        ):

            if index == -1:
                continue

            results.append(
                {
                    "document": self.documents[index],
                    "distance": float(distance),
                    "index": int(index),
                }
            )

        logger.info(
            f"Retrieved {len(results)} documents."
        )

        return results

    # ======================================================
    # Vector Store Information
    # ======================================================

    def get_index_info(self):
        """
        Return vector store metadata.
        """

        if self.index is None:

            return {
                "loaded": False,
                "documents": 0,
                "vectors": 0,
                "dimension": 0,
            }

        return {
            "loaded": True,
            "documents": len(self.documents),
            "vectors": self.index.ntotal,
            "dimension": self.index.d,
        }


# ==========================================================
# Execution Check
# ==========================================================

if __name__ == "__main__":

    from src.data_loader import DataLoader
    from src.embeddings import generate_embeddings

    logger.info("=" * 60)
    logger.info("Vector Store Demonstration")
    logger.info("=" * 60)

    try:

        loader = DataLoader()

        loader.load_data()

        loader.validate_dataset()

        loader.remove_duplicates()

        loader.handle_missing_values()

        documents = loader.prepare_documents()

        embedder, embeddings = generate_embeddings(
            documents
        )

        vector_store = VectorStore()

        vector_store.build_index(
            embeddings,
            documents,
        )

        vector_store.save()

        vector_store.load()

        query_embedding = embedder.generate_embedding(
            "How do I reset my password?"
        )

        results = vector_store.similarity_search(
            query_embedding=query_embedding,
            top_k=3,
        )

        logger.info("=" * 60)
        logger.info("Similarity Search Results")
        logger.info("=" * 60)

        for result in results:

            logger.info(
                f"[{result['index']}] "
                f"Distance={result['distance']:.4f}"
            )

            logger.info(
                result["document"]
            )

        logger.info("=" * 60)

        logger.info(
            vector_store.get_index_info()
        )

        logger.info("=" * 60)
        logger.info(
            "vector_store.py executed successfully."
        )
        logger.info("=" * 60)

    except Exception as error:

        logger.exception(
            "Vector Store execution failed."
        )

        raise
