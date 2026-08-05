"""
==========================================================
Incident Knowledge Assistant (RAG)

chatbot.py

Author : Pramod Prakash Jadhav
==========================================================

Main chatbot orchestration module.
"""

from src.config import (
    TOP_K_RESULTS,
)
from src.logger import get_logger
from src.retriever import Retriever
from src.llm import LLM

logger = get_logger()


class Chatbot:
    """
    Retrieval-Augmented Generation (RAG)
    chatbot for incident knowledge assistance.
    """

    def __init__(self):
        """
        Initialize chatbot components.
        """

        logger.info("=" * 60)
        logger.info("Initializing Chatbot")
        logger.info("=" * 60)

        self.retriever = Retriever()

        self.llm = LLM()

        logger.info(
            "Chatbot initialized successfully."
        )

    # ======================================================
    # Retrieve Knowledge
    # ======================================================

    def retrieve(
        self,
        query: str,
        top_k: int = TOP_K_RESULTS
    ):
        """
        Retrieve relevant knowledge.

        Parameters
        ----------
        query : str

        top_k : int

        Returns
        -------
        dict
        """

        logger.info(
            f"User Query: {query}"
        )

        return self.retriever.retrieve_context(
            query=query,
            top_k=top_k,
      )
      # ======================================================
    # Generate LLM Response
    # ======================================================

    def generate_response(
        self,
        query: str,
        top_k: int = TOP_K_RESULTS
    ):
        """
        Retrieve context and generate an LLM response.

        Parameters
        ----------
        query : str
            User query.

        top_k : int
            Number of retrieved documents.

        Returns
        -------
        dict
            Response dictionary.
        """

        retrieval = self.retrieve(
            query=query,
            top_k=top_k,
        )

        response = self.llm.generate_response(
            query=query,
            context=retrieval["context"],
        )

        return {
            "query": query,
            "response": response,
            "context": retrieval["context"],
            "documents": retrieval["documents"],
            "document_count": retrieval["document_count"],
        }

    # ======================================================
    # Ask Chatbot
    # ======================================================

    def ask(
        self,
        query: str,
        top_k: int = TOP_K_RESULTS
    ):
        """
        Main chatbot interface.

        Parameters
        ----------
        query : str

        top_k : int

        Returns
        -------
        dict
        """

        logger.info("=" * 60)
        logger.info("Processing user request...")
        logger.info("=" * 60)

        if not query.strip():

            raise ValueError(
                "Query cannot be empty."
            )

        result = self.generate_response(
            query=query,
            top_k=top_k,
        )

        logger.info(
            "Response generated successfully."
        )

        return result
      # ======================================================
    # Chat History
    # ======================================================

    def chat_history(self):
        """
        Return chat history if supported.

        Returns
        -------
        list
            Conversation history.
        """

        if hasattr(self.llm, "conversation_history"):

            return self.llm.conversation_history

        return []

    # ======================================================
    # Clear Chat History
    # ======================================================

    def clear_history(self):
        """
        Clear conversation history.
        """

        if hasattr(self.llm, "conversation_history"):

            self.llm.conversation_history.clear()

            logger.info(
                "Conversation history cleared."
            )

    # ======================================================
    # Chatbot Information
    # ======================================================

    def get_chatbot_info(self):
        """
        Return chatbot configuration.

        Returns
        -------
        dict
        """

        retrieval_info = (
            self.retriever.get_retrieval_info()
        )

        info = {

            "chatbot": "Incident Knowledge Assistant",

            "retriever": retrieval_info,

            "llm_model": getattr(
                self.llm,
                "model_name",
                "Unknown"
            ),

            "default_top_k": TOP_K_RESULTS,
        }

        logger.info(
            "Chatbot information generated."
        )

        return info
      # ==========================================================
# Execution Check
# ==========================================================

if __name__ == "__main__":

    logger.info("=" * 60)
    logger.info("Chatbot Demonstration")
    logger.info("=" * 60)

    try:

        chatbot = Chatbot()

        query = (
            "How can I reset my password?"
        )

        result = chatbot.ask(
            query=query
        )

        logger.info("=" * 60)
        logger.info("User Query")

        logger.info(
            result["query"]
        )

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
        logger.info("LLM Response")

        logger.info(
            result["response"]
        )

        logger.info("=" * 60)
        logger.info("Chatbot Information")

        logger.info(
            chatbot.get_chatbot_info()
        )

        logger.info("=" * 60)
        logger.info(
            "chatbot.py executed successfully."
        )
        logger.info("=" * 60)

    except Exception as error:

        logger.exception(
            "Chatbot execution failed."
        )

        raise error
