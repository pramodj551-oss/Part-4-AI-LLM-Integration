"""Deterministic evaluation utilities for RAG retrieval and grounding."""

import re
from collections.abc import Iterable


def _validate_retrieved(retrieved: Iterable):
    if retrieved is None:
        raise ValueError("retrieved results cannot be None.")
    results = list(retrieved)
    if any(not isinstance(item, dict) for item in results):
        raise TypeError("retrieved results must contain dictionaries.")
    return results


def retrieval_metrics(retrieved, relevant_indices, k=None):
    """Calculate Hit@K, Precision@K, Recall@K and MRR from document indices."""
    results = _validate_retrieved(retrieved)
    relevant = {int(index) for index in relevant_indices}
    if not relevant:
        raise ValueError("relevant_indices cannot be empty.")
    if k is None:
        k = len(results)
    if not isinstance(k, int) or isinstance(k, bool) or k < 1:
        raise ValueError("k must be a positive integer.")

    top = results[:k]
    hits = [item.get("index") in relevant for item in top]
    first_rank = next((rank for rank, hit in enumerate(hits, start=1) if hit), None)
    return {
        "k": k,
        "hit_rate": float(any(hits)),
        "precision_at_k": sum(hits) / len(top) if top else 0.0,
        "recall_at_k": sum(hits) / len(relevant),
        "mrr": 1.0 / first_rank if first_rank else 0.0,
    }


def _tokens(text):
    return set(re.findall(r"[a-z0-9]+", str(text).lower()))


def grounding_score(answer, context):
    """Return token-level answer grounding as overlap with retrieved context."""
    answer_tokens = _tokens(answer)
    context_tokens = _tokens(context)
    if not answer_tokens:
        return 0.0
    return len(answer_tokens & context_tokens) / len(answer_tokens)


def evaluate_grounding(answer, context, threshold=0.5):
    """Evaluate whether an answer has sufficient lexical support in context."""
    if not isinstance(threshold, (int, float)) or isinstance(threshold, bool):
        raise ValueError("threshold must be numeric.")
    if not 0 <= threshold <= 1:
        raise ValueError("threshold must be between 0 and 1.")
    score = grounding_score(answer, context)
    return {"grounding_score": score, "grounded": score >= threshold}
