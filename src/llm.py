"""
==========================================================
Incident Knowledge Assistant (RAG)

llm.py

Author : Pramod Prakash Jadhav
==========================================================

LLM Engine using Groq API.
"""

import streamlit as st

from groq import Groq

from src.logger import get_logger

from src.config import (
    GROQ_MODEL,
    REQUEST_TIMEOUT,
    TEMPERATURE,
    TOP_P,
    MAX_TOKENS,
    SYSTEM_PROMPT,
)

logger = get_logger()


class LLMEngine:
    """
    Production-ready Groq LLM Engine.
    """

    def __init__(self):

        logger.info("=" * 60)
        logger.info("Initializing Groq LLM Engine")
        logger.info("=" * 60)

        self.model = GROQ_MODEL

        self.timeout = REQUEST_TIMEOUT

        self.client = None

        self.loaded = False
            # ======================================================
    # Load Groq Model
    # ======================================================

    def load_model(self):
        """
        Initialize the Groq client.
        """

        logger.info("=" * 60)
        logger.info("Loading Groq Client")
        logger.info("=" * 60)

        try:

            api_key = st.secrets.get(
                "GROQ_API_KEY"
            )

            if not api_key:

                raise ValueError(
                    "GROQ_API_KEY not found in Streamlit Secrets."
                )

            self.client = Groq(
                api_key=api_key
            )

            self.loaded = True

            logger.info(
                f"Groq model loaded: {self.model}"
            )

            return True

        except Exception as error:

            logger.exception(
                "Failed to initialize Groq client."
            )

            raise RuntimeError(
                f"Unable to initialize Groq: {error}"
            ) from error

    # ======================================================
    # Model Information
    # ======================================================

    def get_model_info(self):
        """
        Return LLM information.
        """

        return {

            "provider": "Groq",

            "model": self.model,

            "loaded": self.loaded,

            "timeout": self.timeout,

    }
            # ======================================================
    # Ask LLM
    # ======================================================

    def ask(
        self,
        question: str,
        context: str
    ):
        """
        Generate answer using Groq LLM.

        Parameters
        ----------
        question : str
            User question.

        context : str
            Retrieved context.

        Returns
        -------
        str
            Generated answer.
        """

        if not self.loaded:

            self.load_model()

        if not question.strip():

            raise ValueError(
                "Question cannot be empty."
            )

        prompt = f"""
Context:
{context}

Question:
{question}

Answer:
"""

        logger.info(
            "Sending request to Groq..."
        )

        try:

            response = self.client.chat.completions.create(

                model=self.model,

                messages=[
                    {
                        "role": "system",
                        "content": SYSTEM_PROMPT,
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    },
                ],

                temperature=TEMPERATURE,

                top_p=TOP_P,

                max_completion_tokens=MAX_TOKENS,
            )

            answer = (
                response
                .choices[0]
                .message
                .content
                .strip()
            )

            logger.info(
                "Response generated successfully."
            )

            return answer

        except Exception as error:

            logger.exception(
                "Groq request failed."
            )

            raise RuntimeError(
                f"Groq API Error: {error}"
            ) from error
                # ======================================================
    # Health Check
    # ======================================================

    def health_check(self):
        """
        Check whether the LLM is ready.

        Returns
        -------
        dict
        """

        return {

            "provider": "Groq",

            "model": self.model,

            "loaded": self.loaded,

            "status": (
                "healthy"
                if self.loaded
                else "not_loaded"
            ),

        }


# ==========================================================
# Execution Check
# ==========================================================

if __name__ == "__main__":

    logger.info("=" * 60)
    logger.info("Groq LLM Demonstration")
    logger.info("=" * 60)

    try:

        llm = LLMEngine()

        llm.load_model()

        context = (
            "Password Reset: Users can reset their "
            "password using the self-service portal."
        )

        question = (
            "How do I reset my password?"
        )

        answer = llm.ask(
            question=question,
            context=context,
        )

        logger.info("=" * 60)
        logger.info("Question")
        logger.info(question)

        logger.info("=" * 60)
        logger.info("Answer")
        logger.info(answer)

        logger.info("=" * 60)
        logger.info("Model Information")

        logger.info(
            llm.get_model_info()
        )

        logger.info("=" * 60)
        logger.info("Health Check")

        logger.info(
            llm.health_check()
        )

        logger.info("=" * 60)
        logger.info(
            "llm.py executed successfully."
        )
        logger.info("=" * 60)

    except Exception as error:

        logger.exception(
            "LLM execution failed."
        )

        raise error
