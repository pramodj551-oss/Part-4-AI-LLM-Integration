"""P2 retrieval evaluation and observability regression tests."""

import logging

import pytest

from src.evaluation import evaluate_grounding, grounding_score, retrieval_metrics
from src.observability import RAGTelemetry


def test_retrieval_metrics_calculate_hit_precision_recall_and_mrr():
    results = [
        {"index": 4, "distance": 0.1},
        {"index": 2, "distance": 0.2},
        {"index": 9, "distance": 0.3},
    ]
    metrics = retrieval_metrics(results, relevant_indices={2, 9}, k=3)
    assert metrics == {
        "k": 3,
        "hit_rate": 1.0,
        "precision_at_k": pytest.approx(2 / 3),
        "recall_at_k": 1.0,
        "mrr": 0.5,
    }


def test_retrieval_metrics_handles_no_hit():
    metrics = retrieval_metrics([{"index": 7}], relevant_indices={2}, k=1)
    assert metrics["hit_rate"] == 0.0
    assert metrics["precision_at_k"] == 0.0
    assert metrics["recall_at_k"] == 0.0
    assert metrics["mrr"] == 0.0


def test_grounding_score_is_bounded_and_deterministic():
    score = grounding_score("Password reset uses MFA", "Password reset uses MFA for employees")
    assert 0 < score <= 1
    assert grounding_score("", "anything") == 0.0


def test_grounding_evaluation_rejects_invalid_threshold():
    with pytest.raises(ValueError):
        evaluate_grounding("answer", "context", threshold=2)


def test_telemetry_records_counters_without_query_content(caplog):
    telemetry = RAGTelemetry()
    query = "Sensitive employee incident query"
    with caplog.at_level(logging.INFO):
        telemetry.record_retrieval(query, document_count=2, latency_ms=12.5)
        telemetry.record_generation(grounded=True)
        telemetry.record_generation(grounded=False, error=True)

    snapshot = telemetry.snapshot()
    assert snapshot["retrieval_requests"] == 1
    assert snapshot["retrieved_documents"] == 2
    assert snapshot["generation_requests"] == 2
    assert snapshot["grounded_answers"] == 1
    assert snapshot["ungrounded_answers"] == 1
    assert snapshot["generation_errors"] == 1
    assert query not in caplog.text
