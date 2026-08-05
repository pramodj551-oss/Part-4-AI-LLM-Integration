"""
==========================================================
Incident Knowledge Assistant (RAG)

rag_pipeline.py

Author : Pramod Prakash Jadhav
==========================================================

Production-ready Retrieval Augmented Generation Pipeline.
"""

from src.logger import get_logger
from src.retriever import Retriever
from src.llm import LLMEngine

logger = get_logger()


class RAGPipeline:
    """
    Production-ready RAG Pipeline.

    Pipeline Flow
    -------------
    User Question
          │
          ▼
      Retriever
          │
          ▼
      Relevant Context
          │
          ▼
      LLM Generation
          │
          ▼
      Final Answer
    """

    def __init__(self):
        """
        Initialize all pipeline components.
        """

        logger.info("=" * 60)
        logger.info("Initializing RAG Pipeline")
        logger.info("=" * 60)

        try:

            self.retriever = Retriever()

            logger.info(
                "Retriever initialized successfully."
            )

            self.llm = LLMEngine()

            self.llm.load_model()

            logger.info(
                "LLM initialized successfully."
            )

            logger.info(
                "RAG Pipeline initialized successfully."
            )

        except Exception as error:

            logger.exception(
                "Pipeline initialization failed."
            )

            raise RuntimeError(
                f"Unable to initialize the AI Assistant: {error}"
            ) from error

    # ======================================================
    # Retrieve Context
    # ======================================================

    def retrieve(
        self,
        question: str,
        top_k=None,
    ):
        """
        Retrieve relevant context.

        Parameters
        ----------
        question : str

        top_k : int | None

        Returns
        -------
        dict
        """

        logger.info("=" * 60)
        logger.info("Retrieving Context")
        logger.info("=" * 60)

        if not question.strip():

            raise ValueError(
                "Question cannot be empty."
            )

        if top_k is None:

            return self.retriever.retrieve_context(
                query=question
            )

        return self.retriever.retrieve_context(
            query=question,
            top_k=top_k,
            )
            # ======================================================
    # Generate Answer
    # ======================================================

    def generate_answer(
        self,
        question: str,
        context: str,
    ):
        """
        Generate answer using the LLM.

        Parameters
        ----------
        question : str

        context : str

        Returns
        -------
        str
        """

        logger.info("=" * 60)
        logger.info("Generating Answer")
        logger.info("=" * 60)

        if not context.strip():

            logger.warning(
                "No context available."
            )

            return (
                "I could not find any relevant "
                "information in the knowledge base."
            )

        try:

            answer = self.llm.ask(
                question=question,
                context=context,
            )

            if answer is None:

                logger.warning(
                    "LLM returned None."
                )

                return (
                    "The language model did not "
                    "return a response."
                )

            answer = str(answer).strip()

            if answer == "":

                logger.warning(
                    "LLM returned an empty response."
                )

                return (
                    "The language model returned "
                    "an empty response."
                )

            logger.info(
                "Answer generated successfully."
            )

            return answer

        except Exception as error:

            logger.exception(
                "LLM generation failed."
            )

            return (
                "An error occurred while generating "
                f"the answer: {error}"
            )
                # ======================================================
    # Complete RAG Query
    # ======================================================

    def ask(
        self,
        question: str,
        top_k=None,
    ):
        """
        Execute the complete RAG pipeline.

        Parameters
        ----------
        question : str

        top_k : int | None

        Returns
        -------
        dict
        """

        logger.info("=" * 60)
        logger.info("Processing RAG Query")
        logger.info("=" * 60)

        retrieval_result = self.retrieve(
            question=question,
            top_k=top_k,
        )

        context = retrieval_result.get(
            "context",
            "",
        )

        answer = self.generate_answer(
            question=question,
            context=context,
        )

        response = {
            "question": question,
            "answer": answer,
            "context": context,
            "documents": retrieval_result.get(
                "documents",
                [],
            ),
            "document_count": retrieval_result.get(
                "document_count",
                0,
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
        Return pipeline health information.
        """

        logger.info(
            "Running health check..."
        )

        return {
            "status": "healthy",
            "retriever": self.retriever.get_retrieval_info(),
            "llm": self.llm.get_model_info(),
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

        question = "How can I reset my password?"

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
            start=1,
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

    except Exception:

        logger.exception(
            "RAG Pipeline execution failed."
        )

        raise
        
