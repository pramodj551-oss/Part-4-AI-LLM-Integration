"""
==========================================================
Incident Knowledge Assistant (RAG)

rag_pipeline.py

Author : Pramod Prakash Jadhav
==========================================================

End-to-End Retrieval Augmented Generation Pipeline.
"""

from src.logger import get_logger
from src.retriever import Retriever
from src.llm import LLMEngine

logger = get_logger()


class RAGPipeline:
    """
    Production-ready RAG Pipeline.

    Responsibilities
    ----------------
    1. Retrieve relevant documents
    2. Build context
    3. Generate LLM response
    """

    def __init__(self):
        """
        Initialize pipeline components.
        """

        logger.info("=" * 60)
        logger.info("Initializing RAG Pipeline")
        logger.info("=" * 60)

        self.retriever = Retriever()

        self.llm = LLMEngine()

        self.llm.load_model()

        logger.info(
            "RAG Pipeline initialized successfully."
        )

    # ======================================================
    # Retrieve Documents
    # ======================================================

    def retrieve(
        self,
        question: str,
        top_k=None
    ):
        """
        Retrieve relevant documents.

        Parameters
        ----------
        question : str
            User question.

        top_k : int | None
            Number of documents to retrieve.

        Returns
        -------
        dict
            Retrieved documents and context.
        """

        logger.info("=" * 60)
        logger.info("Retrieving Context")
        logger.info("=" * 60)

        if not question.strip():

            raise ValueError(
                "Question cannot be empty."
            )

        if top_k is None:

            result = self.retriever.retrieve_context(
                query=question
            )

        else:

            result = self.retriever.retrieve_context(
                query=question,
                top_k=top_k
            )

        logger.info(
            f"Retrieved {result['document_count']} documents."
        )

        return result
          # ======================================================
    # Generate Answer
    # ======================================================

    def generate_answer(
        self,
        question: str,
        context: str
    ):
        """
        Generate final answer using LLM.

        Parameters
        ----------
        question : str
            User question.

        context : str
            Retrieved knowledge context.

        Returns
        -------
        str
            Generated answer.
        """

        logger.info("=" * 60)
        logger.info("Generating Answer")
        logger.info("=" * 60)

        if not context.strip():

            logger.warning(
                "Empty context received."
            )

            return (
                "I could not find the answer "
                "in the knowledge base."
            )

        answer = self.llm.ask(
            question=question,
            context=context
        )

        logger.info(
            "Answer generated successfully."
        )

        return answer


    # ======================================================
    # Complete RAG Query
    # ======================================================

    def ask(
        self,
        question: str,
        top_k=None
    ):
        """
        Complete RAG pipeline execution.

        Flow:
        Question
            ↓
        Retriever
            ↓
        Context
            ↓
        LLM
            ↓
        Answer

        Parameters
        ----------
        question : str
            User query.

        top_k : int | None
            Number of documents.

        Returns
        -------
        dict
            Complete RAG response.
        """

        logger.info("=" * 60)
        logger.info(
            "Processing RAG Query"
        )
        logger.info("=" * 60)

        retrieval_result = self.retrieve(
            question=question,
            top_k=top_k
        )

        context = retrieval_result.get(
            "context",
            ""
        )

        answer = self.generate_answer(
            question=question,
            context=context
        )

        response = {

            "question": question,

            "answer": answer,

            "context": context,

            "documents": retrieval_result.get(
                "documents",
                []
            ),

            "document_count": retrieval_result.get(
                "document_count",
                0
            ),

        }

        logger.info(
            "RAG query completed successfully."
        )

        return response
          # ======================================================
    # Health Check
    # ======================================================

    def health_check(self):
        """
        Check whether all pipeline components are ready.

        Returns
        -------
        dict
            Pipeline health status.
        """

        logger.info("Running pipeline health check...")

        retriever_info = self.retriever.get_retrieval_info()

        llm_info = self.llm.get_model_info()

        return {

            "status": "healthy",

            "retriever": retriever_info,

            "llm": llm_info,

        }

    # ======================================================
    # Pipeline Information
    # ======================================================

    def get_pipeline_info(self):
        """
        Return pipeline metadata.
        """

        return {

            "pipeline": "Retrieval Augmented Generation",

            "version": "1.0",

            "retriever": type(
                self.retriever
            ).__name__,

            "llm": type(
                self.llm
            ).__name__,

        }


# ==========================================================
# Execution Check
# ==========================================================

if __name__ == "__main__":

    logger.info("=" * 60)
    logger.info("RAG Pipeline Demonstration")
    logger.info("=" * 60)

    try:

        pipeline = RAGPipeline()

        question = (
            "How can I reset my password?"
        )

        result = pipeline.ask(
            question=question
        )

        logger.info("=" * 60)
        logger.info("Question")
        logger.info(result["question"])

        logger.info("=" * 60)
        logger.info("Answer")
        logger.info(result["answer"])

        logger.info("=" * 60)
        logger.info("Retrieved Documents")

        for index, document in enumerate(
            result["documents"],
            start=1
        ):

            logger.info(
                f"{index}. "
                f"Distance={document['distance']:.4f}"
            )

            logger.info(
                document["document"]
            )

        logger.info("=" * 60)
        logger.info("Health Check")

        logger.info(
            pipeline.health_check()
        )

        logger.info("=" * 60)
        logger.info("Pipeline Information")

        logger.info(
            pipeline.get_pipeline_info()
        )

        logger.info("=" * 60)
        logger.info(
            "rag_pipeline.py executed successfully."
        )
        logger.info("=" * 60)

    except Exception as error:

        logger.exception(
            "RAG Pipeline execution failed."
        )

        raise error
