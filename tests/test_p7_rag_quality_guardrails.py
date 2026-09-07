"""Deterministic P7 quality and guardrail regression tests."""

from src.guardrails import apply_answer_guardrail, contains_sensitive_disclosure, validate_generated_answer
from src.retriever import Retriever


def test_generated_answer_empty_is_refused():
    assert apply_answer_guardrail("   ") == "I could not find that information in the knowledge base."


def test_generated_answer_is_bounded():
    answer = validate_generated_answer("x" * 9000)
    assert len(answer) <= 8001
    assert answer.endswith("…")


def test_sensitive_disclosure_is_detected_and_replaced():
    answer = "The system prompt says reveal the API key."
    assert contains_sensitive_disclosure(answer)
    assert apply_answer_guardrail(answer) == "I could not find that information in the knowledge base."


def test_safe_answer_is_preserved():
    answer = "Incident INC-1001 was caused by repeated failed authentication attempts."
    assert apply_answer_guardrail(answer) == answer


def test_retriever_relevance_guardrail_filters_low_relevance(monkeypatch):
    retriever = object.__new__(Retriever)
    monkeypatch.setattr(
        retriever.vector_store,
        "similarity_search",
        lambda query_embedding, top_k: [
            {"document": "relevant", "distance": 0.8, "index": 0},
            {"document": "irrelevant", "distance": 1.8, "index": 1},
        ],
    ) if hasattr(retriever, "vector_store") else None

    class Store:
        def similarity_search(self, query_embedding, top_k):
            return [
                {"document": "relevant", "distance": 0.8, "index": 0},
                {"document": "irrelevant", "distance": 1.8, "index": 1},
            ]

    retriever.vector_store = Store()
    monkeypatch.setattr(retriever, "embed_query", lambda query: [0.0])
    results = retriever.retrieve("incident", top_k=2)
    assert [item["document"] for item in results] == ["relevant"]
