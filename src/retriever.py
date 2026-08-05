"""
==========================================================
Incident Knowledge Assistant (RAG)

retriever.py

Author : Pramod Prakash Jadhav
==========================================================

Retrieve relevant documents from FAISS vector database.
"""

from sentence_transformers import SentenceTransformer

from src.config import (
    EMBEDDING_MODEL,
    TOP_K_RESULTS,
)
from src.logger import get_logger
from src.vector_store import VectorStore

logger = get_logger()


class Retriever:
    """
    Retrieve relevant documents using semantic search.
    """

    def __init__(self):
        """
        Initialize embedding model and vector store.
        """

        logger.info("=" * 60)
        logger.info("Initializing Retriever")
        logger.info("=" * 60)

        self.embedder = SentenceTransformer(
            EMBEDDING_MODEL
        )

        self.vector_store = VectorStore()

        self.vector_store.load()

        logger.info(
            "Retriever initialized successfully."
        )

    # ======================================================
    # Embed Query
    # ======================================================

    def embed_query(
        self,
        query: str
    ):
        """
        Convert user query into embedding.

        Parameters
        ----------
        query : str
            User question.

        Returns
        -------
        numpy.ndarray
            Query embedding.
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
        top_k: int = TOP_K_RESULTS
    ):
        """
        Retrieve the most relevant documents.

        Parameters
        ----------
        query : str
            User query.

        top_k : int
            Number of documents to retrieve.

        Returns
        -------
        list
            List of retrieved documents.
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
        retrieved_documents
    ):
        """
        Build LLM context from retrieved documents.

        Parameters
        ----------
        retrieved_documents : list
            Output from similarity search.

        Returns
        -------
        str
            Combined context.
        """

        logger.info(
            "Building context for LLM..."
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
            f"Context length : {len(context)} characters"
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
        top_k: int = TOP_K_RESULTS
    ):
        """
        Retrieve relevant documents and build context.

        Parameters
        ----------
        query : str
            User query.

        top_k : int
            Number of documents to retrieve.

        Returns
        -------
        dict
            Retrieval result containing query,
            retrieved documents and context.
        """

        documents = self.retrieve(
            query=query,
            top_k=top_k
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
    # Retrieval Information
    # ======================================================

    def get_retrieval_info(self):
        """
        Return retriever information.
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

        query = (
            "How can I reset my password?"
        )

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
            start=1
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

    except Exception as error:

        logger.exception(
            "Retriever execution failed."
        )

        raise error
      
