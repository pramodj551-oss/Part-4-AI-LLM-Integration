"""Production RAG orchestration with safe validation and error handling."""

from src.llm import LLMEngine
from src.logger import get_logger
from src.retriever import Retriever
from src.security import validate_context, validate_query, validate_top_k

logger = get_logger()


class RAGPipeline:
    """Orchestrate retrieval and generation without leaking internal errors."""

    def __init__(self):
        try:
            self.retriever = Retriever()
            self.llm = LLMEngine()
            self.llm.load_model()
            logger.info("RAG Pipeline initialized successfully.")
        except Exception:
            logger.exception("Pipeline initialization failed.")
            raise RuntimeError("Unable to initialize the AI Assistant.") from None

    def retrieve(self, question: str, top_k=None):
        question = validate_query(question)
        if top_k is None:
            return self.retriever.retrieve_context(query=question)
        return self.retriever.retrieve_context(
            query=question,
            top_k=validate_top_k(top_k),
        )

    def generate_answer(self, question: str, context: str, conversation_history=None):
        question = validate_query(question)
        if not isinstance(context, str) or not context.strip():
            return "I could not find any relevant information in the knowledge base."
        context = validate_context(context)
        try:
            answer = self.llm.ask(
                question=question,
                context=context,
                conversation_history=conversation_history,
            )
            return answer or "The language model did not return a response."
        except Exception:
            logger.exception("LLM generation failed.")
            return "An error occurred while generating the answer."

    def ask(self, question: str, top_k=None, conversation_history=None):
        question = validate_query(question)
        retrieval_result = self.retrieve(question=question, top_k=top_k)
        context = retrieval_result.get("context", "")
        answer = self.generate_answer(
            question=question,
            context=context,
            conversation_history=conversation_history,
        )
        return {
            "question": question,
            "answer": answer,
            "context": context,
            "documents": retrieval_result.get("documents", []),
            "document_count": retrieval_result.get("document_count", 0),
        }

    def health_check(self):
        return {
            "status": "healthy",
            "retriever": self.retriever.get_retrieval_info(),
            "llm": self.llm.get_model_info(),
        }

    def get_pipeline_info(self):
        return {
            "pipeline": "Retrieval Augmented Generation",
            "version": "1.0",
            "retriever": type(self.retriever).__name__,
            "llm": type(self.llm).__name__,
        }


if __name__ == "__main__":
    logger.info("RAG Pipeline module loaded successfully.")
