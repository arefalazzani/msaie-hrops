"""Milestone 5: reusable, LLM-free policy evidence retrieval.

Uses the SAME Chroma collection and MiniLM embedding model as Milestone 4.
Does not access employee PostgreSQL data; that belongs to MCP tools later.
"""
from __future__ import annotations

from functools import lru_cache
from time import perf_counter
from typing import Any

from rag.settings import COLLECTION, INDEX_DIR


VALID_TYPES = {"Policy", "SOP", "Register"}
VALID_FORMATS = {"md", "pdf"}


def build_metadata_filter(
    *,
    document_ids: list[str] | None = None,
    document_type: str | None = None,
    source_format: str | None = None,
) -> dict[str, Any] | None:
    """Construct valid Chroma metadata filters, even with several constraints."""
    clauses: list[dict[str, Any]] = []
    if document_ids is not None:
        if not document_ids or len(document_ids) > 25 or any(not x.strip() for x in document_ids):
            raise ValueError("document_ids must contain 1–25 nonempty IDs")
        ids = list(dict.fromkeys(doc_id.strip() for doc_id in document_ids))
        clauses.append({"document_id": ids[0]} if len(ids) == 1
                       else {"document_id": {"$in": ids}})
    if document_type is not None:
        if document_type not in VALID_TYPES:
            raise ValueError(f"document_type must be one of {sorted(VALID_TYPES)}")
        clauses.append({"document_type": document_type})
    if source_format is not None:
        if source_format not in VALID_FORMATS:
            raise ValueError(f"source_format must be one of {sorted(VALID_FORMATS)}")
        clauses.append({"format": source_format})
    return None if not clauses else clauses[0] if len(clauses) == 1 else {"$and": clauses}


def _evidence(document: Any, distance: float, rank: int) -> dict[str, Any]:
    metadata = document.metadata
    mandatory = ("document_id", "title", "source", "section", "chunk_id")
    missing = [key for key in mandatory if not metadata.get(key)]
    if missing:
        raise ValueError(f"Retrieved chunk lacks citation metadata: {missing}")
    passage = document.page_content
    return {
        "rank": rank,
        "document_id": metadata["document_id"],
        "title": metadata["title"],
        "section": metadata["section"],
        "page": metadata.get("page"),
        "source": metadata["source"],
        "version": metadata.get("version"),
        "document_type": metadata.get("document_type"),
        "format": metadata.get("format"),
        "chunk_id": metadata["chunk_id"],
        "citation": f"{metadata['document_id']} — {metadata['section']}",
        "source_snippet": metadata.get("source_snippet") or " ".join(passage.split())[:240],
        "text": passage,
        # Chroma's score here is a DISTANCE (lower is closer), not confidence.
        "distance": round(float(distance), 6),
    }


class PolicyRetriever:
    """Use an injected Chroma-compatible store; easy to test with a fake store."""

    def __init__(self, vectorstore: Any) -> None:
        self.vectorstore = vectorstore

    def search(
        self,
        query: str,
        *,
        k: int = 5,
        document_ids: list[str] | None = None,
        document_type: str | None = None,
        source_format: str | None = None,
        max_per_document: int | None = None,
    ) -> dict[str, Any]:
        """Top-K dense similarity search, optionally scoped or diversified.

        max_per_document is a simple source-diversification option. It is NOT a
        learned reranker and does not change the embedding model.
        """
        if not isinstance(query, str) or not query.strip():
            raise ValueError("query must be nonempty")
        if len(query) > 2000:
            raise ValueError("query must be 2000 characters or fewer")
        if not isinstance(k, int) or isinstance(k, bool) or not 1 <= k <= 20:
            raise ValueError("k must be an integer from 1 to 20")
        if max_per_document is not None and (
            not isinstance(max_per_document, int) or isinstance(max_per_document, bool)
            or not 1 <= max_per_document <= 20
        ):
            raise ValueError("max_per_document must be an integer from 1 to 20")

        filter_expression = build_metadata_filter(
            document_ids=document_ids,
            document_type=document_type,
            source_format=source_format,
        )
        candidate_k = k if max_per_document is None else max(40, k * 10)
        start = perf_counter()
        pairs = self.vectorstore.similarity_search_with_score(
            query.strip(), k=candidate_k, filter=filter_expression,
        )
        results: list[dict[str, Any]] = []
        per_document: dict[str, int] = {}
        seen_chunk_ids: set[str] = set()
        for document, distance in pairs:
            doc_id = document.metadata.get("document_id")
            chunk_id = document.metadata.get("chunk_id")
            if chunk_id in seen_chunk_ids:
                continue
            if max_per_document is not None and per_document.get(doc_id, 0) >= max_per_document:
                continue
            results.append(_evidence(document, distance, len(results) + 1))
            seen_chunk_ids.add(chunk_id)
            per_document[doc_id] = per_document.get(doc_id, 0) + 1
            if len(results) >= k:
                break
        return {
            "query": query.strip(),
            "requested_k": k,
            "filter": filter_expression,
            "max_per_document": max_per_document,
            "result_count": len(results),
            "latency_ms": round((perf_counter() - start) * 1000, 2),
            "results": results,
        }


@lru_cache(maxsize=1)
def open_policy_retriever() -> PolicyRetriever:
    """Open Milestone 4's persistent index, rather than creating a new one.

    Cache the embedding model and database client within one process.
    """
    if not INDEX_DIR.is_dir():
        raise FileNotFoundError(
            f"Chroma index not found at {INDEX_DIR}. Run 'python -m scripts.index_policies' first."
        )
    import chromadb
    from langchain_chroma import Chroma
    from rag.embeddings import MiniLMEmbeddings

    client = chromadb.PersistentClient(path=str(INDEX_DIR))
    collections = {item if isinstance(item, str) else item.name
                   for item in client.list_collections()}
    if COLLECTION not in collections:
        raise RuntimeError(
            f"Chroma collection '{COLLECTION}' is missing. "
            "Check RAG_CHROMA_DIR / RAG_COLLECTION or rebuild the index."
        )
    if client.get_collection(COLLECTION).count() == 0:
        raise RuntimeError(f"Chroma collection '{COLLECTION}' is empty")
    store = Chroma(client=client, collection_name=COLLECTION,
                   embedding_function=MiniLMEmbeddings())
    return PolicyRetriever(store)
