"""
==========================================================
Incident Knowledge Assistant (RAG)

retriever.py

Author : Pramod Prakash Jadhav
==========================================================

Production-ready Retriever with automatic FAISS
index creation for first deployment.
"""

from pathlib import Path

from sentence_transformers import SentenceTransformer

from src.config import (
    EMBEDDING_MODEL,
    TOP_K_RESULTS,
    FAISS_INDEX_PATH,
    DOCUMENTS_PATH,
)

from src.logger import get_logger
from src.vector_store import VectorStore
from src.data_loader import DataLoader
from src.embeddings import generate_embeddings

logger = get_logger()


class Retriever:
    """
    Production-ready semantic retriever.
    """

    def __init__(self):
        """
        Initialize retriever.
        """

        logger.info("=" * 60)
        logger.info("Initializing Retriever")
        logger.info("=" * 60)

        self.embedder = SentenceTransformer(
            EMBEDDING_MODEL
        )

        self.vector_store = VectorStore()

        self._initialize_vector_store()

        logger.info(
            "Retriever initialized successfully."
        )

    # ======================================================
    # Initialize Vector Store
    # ======================================================

    def _initialize_vector_store(self):
        """
        Load an existing FAISS index.
        If it does not exist, automatically build it.
        """

        if (
            Path(FAISS_INDEX_PATH).exists()
            and
            Path(DOCUMENTS_PATH).exists()
        ):

            logger.info(
                "Existing FAISS index found."
            )

            self.vector_store.load()

            return

        logger.warning(
            "FAISS index not found."
        )

        logger.info(
            "Creating vector database..."
        )

        loader = DataLoader()

        loader.load_data()

        loader.validate_dataset()

        loader.remove_duplicates()

        loader.handle_missing_values()

        documents = loader.prepare_documents()

        _, embeddings = generate_embeddings(
            documents
        )

        self.vector_store.build_index(
            embeddings,
            documents,
        )

        self.vector_store.save()

        logger.info(
            "Vector database created successfully."
        )
            # ======================================================
    # Embed Query
    # ======================================================

    def embed_query(
        self,
        query: str,
    ):
        """
        Convert a user query into an embedding.

        Parameters
        ----------
        query : str

        Returns
        -------
        numpy.ndarray
        """

        if not query.strip():

            raise ValueError(
                "Query cannot be empty."
            )

        logger.info(
            f"Embedding query: {query}"
        )

        embedding = self.embedder.encode(
            query,
            convert_to_numpy=True,
        )

        logger.info(
            "Query embedding generated successfully."
        )

        return embedding

    # ======================================================
    # Retrieve Documents
    # ======================================================

    def retrieve(
        self,
        query: str,
        top_k: int = TOP_K_RESULTS,
    ):
        """
        Retrieve the most relevant documents.

        Parameters
        ----------
        query : str

        top_k : int

        Returns
        -------
        list
        """

        logger.info("=" * 60)
        logger.info("Starting document retrieval")
        logger.info("=" * 60)

        query_embedding = self.embed_query(
            query
        )

        results = self.vector_store.similarity_search(
            query_embedding=query_embedding,
            top_k=top_k,
        )

        logger.info(
            f"Retrieved {len(results)} documents."
        )

        return results

    # ======================================================
    # Build Context
    # ======================================================

    def build_context(
        self,
        retrieved_documents,
    ):
        """
        Build LLM context from retrieved documents.

        Parameters
        ----------
        retrieved_documents : list

        Returns
        -------
        str
        """

        logger.info(
            "Building context..."
        )

        if not retrieved_documents:

            logger.warning(
                "No documents retrieved."
            )

            return ""

        context_parts = []

        for item in retrieved_documents:

            document = item.get(
                "document",
                ""
            )

            if document:

                context_parts.append(
                    document.strip()
                )

        context = "\n\n".join(
            context_parts
        )

        logger.info(
            f"Context length: {len(context)} characters"
        )

        logger.info(
            "Context built successfully."
        )

        return context
            # ======================================================
    # Retrieve Context
    # ======================================================

    def retrieve_context(
        self,
        query: str,
        top_k: int = TOP_K_RESULTS,
    ):
        """
        Retrieve relevant documents and build context.

        Parameters
        ----------
        query : str

        top_k : int

        Returns
        -------
        dict
        """

        documents = self.retrieve(
            query=query,
            top_k=top_k,
        )

        context = self.build_context(
            documents
        )

        return {
            "query": query,
            "documents": documents,
            "context": context,
            "document_count": len(documents),
        }

    # ======================================================
    # Retriever Information
    # ======================================================

    def get_retrieval_info(self):
        """
        Return retriever metadata.
        """

        info = self.vector_store.get_index_info()

        info.update(
            {
                "embedding_model": EMBEDDING_MODEL,
                "default_top_k": TOP_K_RESULTS,
            }
        )

        return info


# ==========================================================
# Execution Check
# ==========================================================

if __name__ == "__main__":

    logger.info("=" * 60)
    logger.info("Retriever Demonstration")
    logger.info("=" * 60)

    try:

        retriever = Retriever()

        query = "How can I reset my password?"

        result = retriever.retrieve_context(
            query=query
        )

        logger.info("=" * 60)
        logger.info("Query")
        logger.info(result["query"])

        logger.info("=" * 60)
        logger.info("Retrieved Documents")

        for index, item in enumerate(
            result["documents"],
            start=1,
        ):

            logger.info(
                f"{index}. "
                f"Distance={item['distance']:.4f}"
            )

            logger.info(
                item["document"]
            )

        logger.info("=" * 60)
        logger.info("Context")

        logger.info(
            result["context"]
        )

        logger.info("=" * 60)
        logger.info("Retriever Information")

        logger.info(
            retriever.get_retrieval_info()
        )

        logger.info("=" * 60)
        logger.info(
            "retriever.py executed successfully."
        )
        logger.info("=" * 60)

    except Exception:

        logger.exception(
            "Retriever execution failed."
        )

        raise
