"""
==========================================================
Incident Knowledge Assistant (RAG)

llm.py

Author : Pramod Prakash Jadhav
==========================================================

LLM Engine using Ollama.
"""

import requests

from src.config import (
    OLLAMA_BASE_URL,
    OLLAMA_MODEL,
    TEMPERATURE,
    MAX_TOKENS,
)

from src.logger import get_logger

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
        logger.info("Initializing Ollama LLM")
        logger.info("=" * 60)

        self.base_url = OLLAMA_BASE_URL

        self.model = OLLAMA_MODEL

        self.temperature = TEMPERATURE

        self.max_tokens = MAX_TOKENS

        self.generate_url = (
            f"{self.base_url}/api/generate"
        )

        logger.info(
            f"Model : {self.model}"
        )

        logger.info(
            "LLM initialized successfully."
        )

    # ======================================================
    # Check Ollama Server
    # ======================================================

    def load_model(self):
        """
        Verify that the Ollama server is reachable.
        """

        try:

            response = requests.get(
                self.base_url,
                timeout=5,
            )

            logger.info(
                "Ollama server is reachable."
            )

            return response.status_code == 200

        except Exception as error:

            logger.exception(
                "Unable to connect to Ollama."
            )

            raise ConnectionError(
                "Ollama server is not running."
            ) from error
              # ======================================================
    # Build Prompt
    # ======================================================

    def build_prompt(
        self,
        question: str,
        context: str
    ):
        """
        Build prompt for Ollama.
        """

        logger.info(
            "Building LLM prompt..."
        )

        prompt = f"""
You are an AI Incident Response Assistant.

Answer ONLY using the information provided in the context.

If the answer is not available in the context,
reply:

"I could not find the answer in the knowledge base."

Keep the answer concise, professional and factual.

==================================================
CONTEXT
==================================================

{context}

==================================================
QUESTION
==================================================

{question}

==================================================
ANSWER
==================================================
"""

        return prompt.strip()

    # ======================================================
    # Generate Response
    # ======================================================

    def generate_response(
        self,
        prompt: str
    ):
        """
        Generate response using Ollama.
        """

        logger.info(
            "Generating response..."
        )

        payload = {

            "model": self.model,

            "prompt": prompt,

            "stream": False,

            "options": {

                "temperature": self.temperature,

                "num_predict": self.max_tokens

            }

        }

        try:

            response = requests.post(

                self.generate_url,

                json=payload,

                timeout=300

            )

            response.raise_for_status()

            data = response.json()

            answer = data.get(
                "response",
                ""
            ).strip()

            logger.info(
                "Response generated successfully."
            )

            return answer

        except requests.exceptions.RequestException as error:

            logger.exception(
                "LLM request failed."
            )

            raise RuntimeError(
                "Failed to generate response from Ollama."
            ) from error
              # ======================================================
    # Ask LLM
    # ======================================================

    def ask(
        self,
        question: str,
        context: str
    ):
        """
        Generate answer using retrieved context.
        """

        logger.info("=" * 60)
        logger.info("Processing user query")
        logger.info("=" * 60)

        if not question.strip():

            raise ValueError(
                "Question cannot be empty."
            )

        prompt = self.build_prompt(
            question=question,
            context=context
        )

        answer = self.generate_response(
            prompt
        )

        logger.info(
            "Answer generated successfully."
        )

        return answer

    # ======================================================
    # Model Information
    # ======================================================

    def get_model_info(self):
        """
        Return LLM configuration.
        """

        return {

            "provider": "Ollama",

            "model": self.model,

            "base_url": self.base_url,

            "temperature": self.temperature,

            "max_tokens": self.max_tokens,

        }


# ==========================================================
# Execution Check
# ==========================================================

if __name__ == "__main__":

    logger.info("=" * 60)
    logger.info("LLM Demonstration")
    logger.info("=" * 60)

    try:

        engine = LLMEngine()

        engine.load_model()

        sample_context = """
Password Reset:

Users can reset their password using
the company self-service portal.

VPN Access:

VPN requires Multi-Factor Authentication.

Incident Severity:

P1 incidents must be escalated immediately.
"""

        sample_question = (
            "How can I reset my password?"
        )

        answer = engine.ask(

            question=sample_question,

            context=sample_context

        )

        logger.info("=" * 60)
        logger.info("Question")

        logger.info(sample_question)

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

    except Exception as error:

        logger.exception(
            "LLM execution failed."
        )

        raise error
