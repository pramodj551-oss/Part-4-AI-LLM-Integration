"""
==========================================================
Incident Knowledge Assistant (RAG)

vector_store.py

Author : Pramod Prakash Jadhav
==========================================================

Build, save and load FAISS vector database.
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
    FAISS Vector Store
    """

    def __init__(self):

        self.index = None

        self.documents = []

    # ======================================================
    # Build Vector Store
    # ======================================================

    def build_index(

        self,

        embeddings,

        documents

    ):
        """
        Build FAISS index from embeddings.
        """

        logger.info("=" * 60)
        logger.info("Building FAISS Vector Store")
        logger.info("=" * 60)

        if len(embeddings) == 0:

            raise ValueError(
                "Embeddings list is empty."
            )

        vectors = np.asarray(

            embeddings,

            dtype=np.float32

        )

        dimension = vectors.shape[1]

        self.index = faiss.IndexFlatL2(
            dimension
        )

        self.index.add(vectors)

        self.documents = list(documents)

        logger.info(
            f"Vector dimension : {dimension}"
        )

        logger.info(
            f"Indexed documents : "
            f"{len(self.documents)}"
        )

        return self

    # ======================================================
    # Save Vector Store
    # ======================================================

    def save(self):
        """
        Save FAISS index and documents.
        """

        logger.info(
            "Saving vector database..."
        )

        Path(
            FAISS_INDEX_PATH
        ).parent.mkdir(

            parents=True,

            exist_ok=True

        )

        faiss.write_index(

            self.index,

            str(FAISS_INDEX_PATH)

        )

        with open(

            DOCUMENTS_PATH,

            "wb"

        ) as file:

            pickle.dump(

                self.documents,

                file

            )

        logger.info(
            "Vector database saved successfully."
      )
          # ======================================================
    # Load Vector Store
    # ======================================================

    def load(self):
        """
        Load FAISS index and stored documents.
        """

        logger.info("=" * 60)
        logger.info("Loading FAISS Vector Store")
        logger.info("=" * 60)

        if not Path(FAISS_INDEX_PATH).exists():

            raise FileNotFoundError(
                f"FAISS index not found: {FAISS_INDEX_PATH}"
            )

        if not Path(DOCUMENTS_PATH).exists():

            raise FileNotFoundError(
                f"Documents file not found: {DOCUMENTS_PATH}"
            )

        self.index = faiss.read_index(
            str(FAISS_INDEX_PATH)
        )

        with open(
            DOCUMENTS_PATH,
            "rb"
        ) as file:

            self.documents = pickle.load(file)

        logger.info(
            f"Loaded {len(self.documents)} documents."
        )

        logger.info(
            f"Vector dimension : {self.index.d}"
        )

        return self

    # ======================================================
    # Similarity Search
    # ======================================================

    def similarity_search(
        self,
        query_embedding,
        top_k=5
    ):
        """
        Perform similarity search using FAISS.

        Parameters
        ----------
        query_embedding : list | numpy.ndarray
            Embedding of the user query.

        top_k : int
            Number of nearest neighbours.

        Returns
        -------
        list
            Retrieved documents with scores.
        """

        if self.index is None:

            raise RuntimeError(
                "Vector store has not been loaded."
            )

        query_vector = np.asarray(
            [query_embedding],
            dtype=np.float32
        )

        distances, indices = self.index.search(
            query_vector,
            top_k
        )

        results = []

        for distance, index in zip(
            distances[0],
            indices[0]
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
            f"Retrieved {len(results)} similar documents."
        )

        return results
          # ======================================================
    # Vector Store Information
    # ======================================================

    def get_index_info(self):
        """
        Return information about the loaded vector store.
        """

        if self.index is None:

            return {
                "loaded": False,
                "documents": 0,
                "dimension": 0,
                "vectors": 0,
            }

        return {
            "loaded": True,
            "documents": len(self.documents),
            "dimension": self.index.d,
            "vectors": self.index.ntotal,
        }


# ==========================================================
# Execution Check
# ==========================================================

if __name__ == "__main__":

    from src.embeddings import (
        generate_embeddings,
    )

    sample_documents = [

        "Reset your password using the self-service portal.",

        "VPN access requires multi-factor authentication.",

        "Incident severity P1 requires immediate escalation.",

        "Employees must complete security awareness training every year.",

    ]

    logger.info("=" * 60)
    logger.info("Vector Store Demonstration")
    logger.info("=" * 60)

    try:

        embedder, embeddings = generate_embeddings(
            sample_documents
        )

        vector_store = VectorStore()

        vector_store.build_index(
            embeddings,
            sample_documents,
        )

        vector_store.save()

        vector_store.load()

        query_embedding = embedder.encode(
            [
                "How do I reset my password?"
            ]
        )[0]

        results = vector_store.similarity_search(
            query_embedding=query_embedding,
            top_k=2,
        )

        logger.info(
            "Similarity Search Results"
        )

        for result in results:

            logger.info(
                f"[{result['index']}] "
                f"Distance={result['distance']:.4f}"
            )

            logger.info(
                result["document"]
            )

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

        raise error
