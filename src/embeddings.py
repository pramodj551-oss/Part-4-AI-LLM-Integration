"""
==========================================================
Incident Knowledge Assistant (RAG)

embeddings.py

Author : Pramod Prakash Jadhav
==========================================================

Generate SentenceTransformer embeddings for
incident knowledge documents.
"""

from sentence_transformers import SentenceTransformer

from src.config import (
    EMBEDDING_MODEL,
    EMBEDDING_BATCH_SIZE,
    NORMALIZE_EMBEDDINGS,
)
from src.logger import get_logger

logger = get_logger()


class EmbeddingGenerator:
    """
    Generate document embeddings using
    SentenceTransformers.
    """

    def __init__(self):
        """
        Initialize embedding model.
        """

        logger.info("=" * 60)
        logger.info("Initializing Embedding Generator")
        logger.info("=" * 60)

        self.model = SentenceTransformer(
            EMBEDDING_MODEL
        )

        logger.info(
            f"Embedding model loaded: "
            f"{EMBEDDING_MODEL}"
        )

        logger.info(
            "Embedding Generator initialized successfully."
  )
      # ======================================================
    # Generate Single Embedding
    # ======================================================

    def generate_embedding(
        self,
        text: str
    ):
        """
        Generate embedding for a single document.

        Parameters
        ----------
        text : str
            Input document.

        Returns
        -------
        numpy.ndarray
            Embedding vector.
        """

        if not text.strip():

            raise ValueError(
                "Input text cannot be empty."
            )

        logger.info(
            "Generating embedding for one document..."
        )

        embedding = self.model.encode(
            text,
            convert_to_numpy=True,
            normalize_embeddings=NORMALIZE_EMBEDDINGS,
        )

        logger.info(
            "Embedding generated successfully."
        )

        return embedding

    # ======================================================
    # Generate Multiple Embeddings
    # ======================================================

    def generate_embeddings(
        self,
        documents
    ):
        """
        Generate embeddings for multiple documents.

        Parameters
        ----------
        documents : list[str]

        Returns
        -------
        numpy.ndarray
            Matrix of document embeddings.
        """

        if not documents:

            raise ValueError(
                "Document list cannot be empty."
            )

        logger.info("=" * 60)
        logger.info(
            "Generating document embeddings..."
        )
        logger.info("=" * 60)

        embeddings = self.model.encode(
            documents,
            batch_size=EMBEDDING_BATCH_SIZE,
            convert_to_numpy=True,
            normalize_embeddings=NORMALIZE_EMBEDDINGS,
            show_progress_bar=True,
        )

        logger.info(
            f"Generated embeddings for "
            f"{len(documents)} documents."
        )

        return embeddings
      # ======================================================
    # Save Embeddings
    # ======================================================

    def save_embeddings(
        self,
        embeddings,
        output_path
    ):
        """
        Save embeddings to a NumPy file.

        Parameters
        ----------
        embeddings : numpy.ndarray
            Embedding matrix.

        output_path : str | Path
            Destination file.
        """

        from pathlib import Path
        import numpy as np

        output_path = Path(output_path)

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        np.save(
            output_path,
            embeddings
        )

        logger.info(
            f"Embeddings saved to: {output_path}"
        )

    # ======================================================
    # Load Embeddings
    # ======================================================

    def load_embeddings(
        self,
        input_path
    ):
        """
        Load embeddings from a NumPy file.

        Parameters
        ----------
        input_path : str | Path

        Returns
        -------
        numpy.ndarray
        """

        from pathlib import Path
        import numpy as np

        input_path = Path(input_path)

        if not input_path.exists():

            raise FileNotFoundError(
                f"Embedding file not found: "
                f"{input_path}"
            )

        embeddings = np.load(
            input_path
        )

        logger.info(
            f"Loaded {len(embeddings)} embeddings."
        )

        return embeddings

    # ======================================================
    # Embedding Information
    # ======================================================

    def get_embedding_info(
        self,
        embeddings
    ):
        """
        Return embedding statistics.

        Parameters
        ----------
        embeddings : numpy.ndarray

        Returns
        -------
        dict
        """

        info = {

            "embedding_model":
                EMBEDDING_MODEL,

            "documents":
                int(len(embeddings)),

            "dimension":
                int(embeddings.shape[1]),

            "batch_size":
                EMBEDDING_BATCH_SIZE,

            "normalized":
                NORMALIZE_EMBEDDINGS,
        }

        logger.info(
            "Embedding information generated."
        )

        return info
      # ==========================================================
# Execution Check
# ==========================================================

if __name__ == "__main__":

    from src.data_loader import DataLoader
    from src.config import EMBEDDINGS_FILE

    logger.info("=" * 60)
    logger.info("Embedding Generator Demonstration")
    logger.info("=" * 60)

    try:

        loader = DataLoader()

        loader.load_data()

        loader.validate_dataset()

        loader.remove_duplicates()

        loader.handle_missing_values()

        documents = loader.prepare_documents()

        generator = EmbeddingGenerator()

        embeddings = generator.generate_embeddings(
            documents
        )

        generator.save_embeddings(
            embeddings,
            EMBEDDINGS_FILE,
        )

        loaded_embeddings = (
            generator.load_embeddings(
                EMBEDDINGS_FILE
            )
        )

        info = generator.get_embedding_info(
            loaded_embeddings
        )

        logger.info("=" * 60)
        logger.info("Embedding Information")

        for key, value in info.items():

            logger.info(
                f"{key}: {value}"
            )

        logger.info("=" * 60)

        logger.info(
            f"Embedding Matrix Shape: "
            f"{loaded_embeddings.shape}"
        )

        logger.info("=" * 60)
        logger.info(
            "embeddings.py executed successfully."
        )
        logger.info("=" * 60)

    except Exception as error:

        logger.exception(
            "Embedding generation failed."
        )

        raise error


# ==========================================================
# Convenience Function
# ==========================================================

def generate_embeddings(
    documents
):
    """
    Convenience wrapper used by other modules.

    Parameters
    ----------
    documents : list[str]

    Returns
    -------
    tuple
        (EmbeddingGenerator, embeddings)
    """

    generator = EmbeddingGenerator()

    embeddings = generator.generate_embeddings(
        documents
    )

    return generator, embeddings
