"""Production Groq LLM engine with input and error hardening."""

import streamlit as st
from groq import Groq

from src.config import (
    GROQ_MODEL,
    REQUEST_TIMEOUT,
    TEMPERATURE,
    TOP_P,
    MAX_TOKENS,
    SYSTEM_PROMPT,
)
from src.logger import get_logger
from src.security import validate_context, validate_query

logger = get_logger()


class LLMEngine:
    """Groq-backed LLM engine with safe secret/error handling."""

    def __init__(self):
        self.model = GROQ_MODEL
        self.timeout = REQUEST_TIMEOUT
        self.client = None
        self.loaded = False

    def load_model(self):
        """Initialize the Groq client without exposing the API secret."""
        try:
            api_key = st.secrets.get("GROQ_API_KEY")
            if not api_key:
                raise ValueError("GROQ_API_KEY is not configured.")
            self.client = Groq(api_key=api_key)
            self.loaded = True
            logger.info("Groq client initialized successfully.")
            return True
        except Exception:
            self.loaded = False
            logger.exception("Failed to initialize Groq client.")
            raise RuntimeError("Unable to initialize the language model.") from None

    def get_model_info(self):
        """Return non-sensitive LLM metadata."""
        return {
            "provider": "Groq",
            "model": self.model,
            "loaded": self.loaded,
            "timeout": self.timeout,
        }

    def ask(self, question: str, context: str):
        """Generate an answer using validated question and retrieved context."""
        question = validate_query(question)
        context = validate_context(context)

        if not self.loaded:
            self.load_model()

        prompt = f"Context:\n{context}\n\nQuestion:\n{question}\n\nAnswer:\n"
        logger.info("Sending validated request to Groq.")

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                temperature=TEMPERATURE,
                top_p=TOP_P,
                max_completion_tokens=MAX_TOKENS,
            )
            answer = response.choices[0].message.content
            if not isinstance(answer, str) or not answer.strip():
                raise RuntimeError("Empty model response.")
            logger.info("Response generated successfully.")
            return answer.strip()
        except Exception:
            logger.exception("Groq request failed.")
            raise RuntimeError("The language model request could not be completed.") from None

    def health_check(self):
        return {
            "provider": "Groq",
            "model": self.model,
            "loaded": self.loaded,
            "status": "healthy" if self.loaded else "not_loaded",
        }


if __name__ == "__main__":
    logger.info("Groq LLM module loaded successfully.")
