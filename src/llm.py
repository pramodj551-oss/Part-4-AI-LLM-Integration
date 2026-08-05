"""
==========================================================
Incident Knowledge Assistant (RAG)

llm.py

Author : Pramod Prakash Jadhav
==========================================================

Production-ready LLM Engine using Ollama.
"""

import requests

from src.logger import get_logger
from src.config import (
    OLLAMA_BASE_URL,
    OLLAMA_MODEL,
    REQUEST_TIMEOUT,
    SYSTEM_PROMPT,
    USER_PROMPT_TEMPLATE,
    TEMPERATURE,
    TOP_P,
    TOP_K,
    MAX_TOKENS,
    REPEAT_PENALTY,
)

logger = get_logger()


class LLMEngine:
    """
    Production-ready Ollama LLM Engine.
    """

    def __init__(self):
        """
        Initialize LLM configuration.
        """

        logger.info("=" * 60)
        logger.info("Initializing LLM Engine")
        logger.info("=" * 60)

        self.base_url = OLLAMA_BASE_URL

        self.model = OLLAMA_MODEL

        self.timeout = REQUEST_TIMEOUT

        self.loaded = False

    # ======================================================
    # Load Model
    # ======================================================

    def load_model(self):
        """
        Verify Ollama server and model availability.

        Returns
        -------
        bool
        """

        logger.info(
            "Checking Ollama server..."
        )

        try:

            response = requests.get(
                f"{self.base_url}/api/tags",
                timeout=self.timeout,
            )

            response.raise_for_status()

            models = response.json().get(
                "models",
                []
            )

            available_models = [
                model.get("name", "")
                for model in models
            ]

            if self.model not in available_models:

                raise RuntimeError(
                    f"Model '{self.model}' "
                    "is not available in Ollama."
                )

            self.loaded = True

            logger.info(
                f"Model loaded: {self.model}"
            )

            return True

        except Exception as error:

            logger.exception(
                "Unable to initialize Ollama."
            )

            raise RuntimeError(
                f"Unable to connect to Ollama: {error}"
            ) from error
                # ======================================================
    # Build Prompt
    # ======================================================

    def build_prompt(
        self,
        question: str,
        context: str,
    ) -> str:
        """
        Build the final prompt for the LLM.

        Parameters
        ----------
        question : str
            User question.

        context : str
            Retrieved context.

        Returns
        -------
        str
            Complete prompt.
        """

        logger.info(
            "Building prompt..."
        )

        if not question.strip():

            raise ValueError(
                "Question cannot be empty."
            )

        if context is None:

            context = ""

        prompt = (
            SYSTEM_PROMPT.strip()
            + "\n\n"
            + USER_PROMPT_TEMPLATE.format(
                context=context.strip(),
                question=question.strip(),
            )
        )

        logger.info(
            f"Prompt length: {len(prompt)} characters"
        )

        return prompt
            # ======================================================
    # Ask LLM
    # ======================================================

    def ask(
        self,
        question: str,
        context: str,
    ) -> str:
        """
        Generate an answer using Ollama.

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

        if not self.loaded:

            self.load_model()

        prompt = self.build_prompt(
            question=question,
            context=context,
        )

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": TEMPERATURE,
                "top_p": TOP_P,
                "top_k": TOP_K,
                "num_predict": MAX_TOKENS,
                "repeat_penalty": REPEAT_PENALTY,
            },
        }

        logger.info("=" * 60)
        logger.info("Sending request to Ollama")
        logger.info("=" * 60)

        try:

            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=self.timeout,
            )

            response.raise_for_status()

            result = response.json()

            answer = result.get(
                "response",
                "",
            ).strip()

            if not answer:

                logger.warning(
                    "LLM returned an empty response."
                )

                return (
                    "The language model returned "
                    "an empty response."
                )

            logger.info(
                "LLM response generated successfully."
            )

            return answer

        except requests.Timeout:

            logger.exception(
                "Ollama request timed out."
            )

            return (
                "The request to the language model "
                "timed out."
            )

        except requests.RequestException as error:

            logger.exception(
                "Failed to communicate with Ollama."
            )

            return (
                "Unable to communicate with the "
                f"language model: {error}"
            )

        except Exception as error:

            logger.exception(
                "Unexpected error during inference."
            )

            return (
                "An unexpected error occurred while "
                f"generating the response: {error}"
    )
                # ======================================================
    # Model Information
    # ======================================================

    def get_model_info(self):
        """
        Return information about the configured LLM.

        Returns
        -------
        dict
        """

        return {
            "provider": "Ollama",
            "model": self.model,
            "base_url": self.base_url,
            "timeout": self.timeout,
            "loaded": self.loaded,
        }


# ==========================================================
# Execution Check
# ==========================================================

if __name__ == "__main__":

    logger.info("=" * 60)
    logger.info("LLM Engine Demonstration")
    logger.info("=" * 60)

    try:

        engine = LLMEngine()

        engine.load_model()

        sample_question = (
            "How can I reset my password?"
        )

        sample_context = (
            "Users can reset their password "
            "using the self-service password "
            "reset portal available on the "
            "company intranet."
        )

        answer = engine.ask(
            question=sample_question,
            context=sample_context,
        )

        logger.info("=" * 60)
        logger.info("Question")
        logger.info(sample_question)

        logger.info("=" * 60)
        logger.info("Context")
        logger.info(sample_context)

        logger.info("=" * 60)
        logger.info("Answer")
        logger.info(answer)

        logger.info("=" * 60)
        logger.info("Model Information")
        logger.info(
            engine.get_model_info()
        )

        logger.info("=" * 60)
        logger.info(
            "llm.py executed successfully."
        )
        logger.info("=" * 60)

    except Exception:

        logger.exception(
            "LLM Engine execution failed."
        )

        raise
