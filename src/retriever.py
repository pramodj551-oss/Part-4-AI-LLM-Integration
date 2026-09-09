"""Production semantic retriever with safe session document support."""
from pathlib import Path
from sentence_transformers import SentenceTransformer
from src.config import EMBEDDING_MODEL, EMBEDDING_BATCH_SIZE, NORMALIZE_EMBEDDINGS, TOP_K_RESULTS, FAISS_INDEX_PATH, DOCUMENTS_PATH, MAX_RETRIEVAL_DISTANCE
from src.data_loader import DataLoader
from src.logger import get_logger
from src.security import MAX_CONTEXT_LENGTH, query_fingerprint, validate_query, validate_top_k
from src.vector_store import VectorStore

logger = get_logger()

class Retriever:
    """Semantic retriever with bounded user-controlled parameters and relevance gating."""
    def __init__(self, documents=None):
        logger.info("Initializing Retriever")
        self.embedder = SentenceTransformer(EMBEDDING_MODEL)
        self.vector_store = VectorStore()
        if documents is None:
            self._initialize_vector_store()
        else:
            if not documents or any(not isinstance(item, str) or not item.strip() for item in documents):
                raise ValueError("Session document collection must contain non-empty strings.")
            embeddings = self.embedder.encode(
                documents,
                batch_size=EMBEDDING_BATCH_SIZE,
                convert_to_numpy=True,
                normalize_embeddings=NORMALIZE_EMBEDDINGS,
                show_progress_bar=False,
            )
            self.vector_store.build_index(embeddings, documents)
        logger.info("Retriever initialized successfully.")

    @classmethod
    def from_documents(cls, documents):
        """Create an ephemeral retriever without modifying persistent storage."""
        return cls(documents=list(documents))

    def _initialize_vector_store(self):
        if Path(FAISS_INDEX_PATH).exists() and Path(DOCUMENTS_PATH).exists():
            self.vector_store.load()
            return
        loader = DataLoader()
        loader.load_data()
        loader.validate_dataset()
        loader.remove_duplicates()
        loader.handle_missing_values()
        documents = loader.prepare_documents()
        embeddings = self.embedder.encode(
            documents,
            batch_size=EMBEDDING_BATCH_SIZE,
            convert_to_numpy=True,
            normalize_embeddings=NORMALIZE_EMBEDDINGS,
            show_progress_bar=False,
        )
        self.vector_store.build_index(embeddings, documents)
        self.vector_store.save()

    def embed_query(self, query: str):
        query = validate_query(query)
        logger.info("Embedding query fingerprint=%s", query_fingerprint(query))
        return self.embedder.encode(query, convert_to_numpy=True, normalize_embeddings=NORMALIZE_EMBEDDINGS)

    def retrieve(self, query: str, top_k: int = TOP_K_RESULTS):
        query = validate_query(query)
        top_k = validate_top_k(top_k)
        logger.info("Starting retrieval fingerprint=%s top_k=%d", query_fingerprint(query), top_k)
        results = self.vector_store.similarity_search(query_embedding=self.embed_query(query), top_k=top_k)
        relevant = [item for item in results if item.get("distance", float("inf")) <= MAX_RETRIEVAL_DISTANCE]
        rejected = len(results) - len(relevant)
        if rejected:
            logger.info("Relevance guardrail rejected %d low-relevance results.", rejected)
        logger.info("Retrieved %d relevant documents.", len(relevant))
        return relevant

    def build_context(self, retrieved_documents):
        if not retrieved_documents:
            logger.warning("No relevant documents retrieved.")
            return ""
        context_parts, total_length = [], 0
        for item in retrieved_documents:
            document = item.get("document", "")
            if not isinstance(document, str) or not document.strip():
                continue
            document = document.strip()
            remaining = MAX_CONTEXT_LENGTH - total_length
            if remaining <= 0:
                break
            context_parts.append(document[:remaining])
            total_length += min(len(document), remaining) + 2
        context = "\n\n".join(context_parts)[:MAX_CONTEXT_LENGTH]
        logger.info("Context built successfully: %d characters.", len(context))
        return context

    def retrieve_context(self, query: str, top_k: int = TOP_K_RESULTS):
        query = validate_query(query)
        documents = self.retrieve(query=query, top_k=top_k)
        return {"query": query, "documents": documents, "context": self.build_context(documents), "document_count": len(documents)}

    def get_retrieval_info(self):
        info = self.vector_store.get_index_info()
        info.update({"embedding_model": EMBEDDING_MODEL, "default_top_k": TOP_K_RESULTS, "max_retrieval_distance": MAX_RETRIEVAL_DISTANCE})
        return info
