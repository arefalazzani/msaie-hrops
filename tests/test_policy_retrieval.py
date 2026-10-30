"""Fast unit tests; no vector store, internet or embedding download required."""
from types import SimpleNamespace

import pytest

from rag.retrieval import PolicyRetriever, build_metadata_filter
from scripts.evaluate_retrieval import evaluate


def doc(document_id, chunk, section="Leave", text="Sample policy evidence"):
    return SimpleNamespace(page_content=text, metadata={
        "document_id": document_id,
        "title": f"Policy {document_id}",
        "source": f"policy_corpus/{document_id}.md",
        "section": section,
        "chunk_id": chunk,
        "source_snippet": text,
        "version": "2.1",
        "document_type": "Policy",
        "format": "md",
    })


class FakeStore:
    def __init__(self, pairs):
        self.pairs = pairs
        self.calls = []

    def similarity_search_with_score(self, query, *, k, filter):
        self.calls.append((query, k, filter))
        return self.pairs[:k]


def test_multi_filter_chroma_syntax():
    assert build_metadata_filter(document_ids=["VND-HR-004", "VND-HR-005"],
        document_type="Policy", source_format="md") == {"$and": [
            {"document_id": {"$in": ["VND-HR-004", "VND-HR-005"]}},
            {"document_type": "Policy"},
            {"format": "md"},
        ]}
    assert build_metadata_filter() is None
    assert build_metadata_filter(document_ids=["VND-HR-004"]) == {"document_id": "VND-HR-004"}


def test_returns_top_k_with_real_citation_fields():
    store = FakeStore([(doc("VND-HR-004", "id-1"), 0.15),
                       (doc("VND-SOP-103", "id-2"), 0.23),
                       (doc("VND-HR-005", "id-3"), 0.25)])
    result = PolicyRetriever(store).search(" PTO? ", k=2)
    assert result["result_count"] == 2
    assert store.calls[0] == ("PTO?", 2, None)
    assert result["results"][0]["citation"] == "VND-HR-004 — Leave"
    assert result["results"][0]["source"] == "policy_corpus/VND-HR-004.md"
    assert result["results"][0]["distance"] == 0.15


def test_filtered_query_passes_filter_to_store():
    store = FakeStore([(doc("VND-HR-004", "id-1"), 0.10)])
    PolicyRetriever(store).search("leave", document_ids=["VND-HR-004"])
    assert store.calls[0][2] == {"document_id": "VND-HR-004"}


def test_diversification_cap_and_deduplicates_chunks():
    store = FakeStore([(doc("VND-HR-004", "id-1"), 0.10),
                       (doc("VND-HR-004", "id-1"), 0.10),
                       (doc("VND-HR-004", "id-2"), 0.12),
                       (doc("VND-HR-005", "id-3"), 0.20)])
    result = PolicyRetriever(store).search("leave", k=2, max_per_document=1)
    assert [r["document_id"] for r in result["results"]] == ["VND-HR-004", "VND-HR-005"]
    assert store.calls[0][1] > 2


@pytest.mark.parametrize("kwargs", [
    {"query": ""}, {"query": "hello", "k": 0},
    {"query": "hello", "k": 21},
    {"query": "hello", "source_format": "docx"},
    {"query": "hello", "max_per_document": 0},
])
def test_bad_inputs_rejected(kwargs):
    with pytest.raises(ValueError):
        PolicyRetriever(FakeStore([])).search(**kwargs)


def test_missing_citation_metadata_is_rejected():
    malformed = SimpleNamespace(page_content="text", metadata={"document_id": "X"})
    with pytest.raises(ValueError, match="citation metadata"):
        PolicyRetriever(FakeStore([(malformed, 0.1)])).search("hello")


def test_small_evaluation_is_repeatable_in_scoring():
    store = FakeStore([(doc("VND-HR-004", "id-1"), 0.1)])
    result = evaluate(PolicyRetriever(store), [
        {"id": "T1", "query": "PTO", "expected_document_ids": ["VND-HR-004"]}
    ], k_values=(1,))
    assert result["comparisons"][0]["mean_document_recall_at_k"] == 1.0
