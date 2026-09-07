"""P0 configuration and vector-store safety tests."""
import json

import numpy as np
import pytest

from src import config
from src.vector_store import VectorStore


def test_config_uses_groq_and_has_no_stale_ollama_settings():
    assert config.GROQ_MODEL == "llama-3.1-8b-instant"
    assert not hasattr(config, "OLLAMA_BASE_URL")
    assert not hasattr(config, "OLLAMA_MODEL")
    assert config.DATASET_PATH.name == "incidents.csv"
    assert config.DOCUMENTS_PATH.name == "documents.json"


def test_config_execution_imports_cleanly():
    source = config.__loader__.get_source(config.__name__)
    namespace = {
        "__name__": config.__name__,
        "__file__": str(config.__file__),
        "__package__": config.__package__,
    }
    exec(compile(source, str(config.__file__), "exec"), namespace)
    assert namespace["GROQ_MODEL"] == config.GROQ_MODEL
    assert namespace["DATASET_PATH"].name == "incidents.csv"
    assert namespace["DOCUMENTS_PATH"].name == "documents.json"


def test_vector_store_round_trip_uses_json(tmp_path, monkeypatch):
    index_path = tmp_path / "faiss.index"
    documents_path = tmp_path / "documents.json"
    monkeypatch.setattr("src.vector_store.FAISS_INDEX_PATH", index_path)
    monkeypatch.setattr("src.vector_store.DOCUMENTS_PATH", documents_path)

    documents = ["password reset procedure", "vpn access procedure"]
    embeddings = np.asarray([[1.0, 0.0], [0.0, 1.0]], dtype=np.float32)

    store = VectorStore().build_index(embeddings, documents)
    store.save()

    assert documents_path.exists()
    assert json.loads(documents_path.read_text(encoding="utf-8")) == documents
    assert not (tmp_path / "documents.pkl").exists()

    loaded = VectorStore().load()
    assert loaded.documents == documents
    assert loaded.get_index_info()["vectors"] == 2


def test_vector_store_rejects_index_document_mismatch(tmp_path, monkeypatch):
    index_path = tmp_path / "faiss.index"
    documents_path = tmp_path / "documents.json"
    monkeypatch.setattr("src.vector_store.FAISS_INDEX_PATH", index_path)
    monkeypatch.setattr("src.vector_store.DOCUMENTS_PATH", documents_path)

    VectorStore().build_index(np.asarray([[1.0, 0.0]], dtype=np.float32), ["one"]).save()
    documents_path.write_text(json.dumps(["one", "two"]), encoding="utf-8")

    with pytest.raises(ValueError, match="inconsistent"):
        VectorStore().load()


def test_vector_store_rejects_non_string_documents():
    with pytest.raises(TypeError, match="strings"):
        VectorStore().build_index(np.asarray([[1.0, 0.0]], dtype=np.float32), [123])
