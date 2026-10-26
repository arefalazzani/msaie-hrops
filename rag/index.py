"""Reproducible Chroma indexing, with safe rebuild and a JSON audit report."""
from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path

from rag.corpus import load_policy_documents, chunk_policy_documents, corpus_summary
from rag.embeddings import MiniLMEmbeddings, MODEL_NAME
from rag.settings import (
    ROOT, CORPUS_DIR, MANIFEST_PATH, INDEX_DIR, COLLECTION,
    CHUNK_SIZE, CHUNK_OVERLAP,
)


def build_index(*, rebuild: bool = False) -> dict:
    """Index exactly the manifest-listed corpus; refuse duplicate indexing by default."""
    import chromadb
    from langchain_chroma import Chroma

    sections = load_policy_documents(CORPUS_DIR, MANIFEST_PATH)
    chunks = chunk_policy_documents(sections, CHUNK_SIZE, CHUNK_OVERLAP)
    if not chunks:
        raise ValueError("Corpus produced zero text chunks")
    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(INDEX_DIR))
    names = {item if isinstance(item, str) else item.name
             for item in client.list_collections()}
    if COLLECTION in names:
        if not rebuild:
            raise RuntimeError(
                f"Collection '{COLLECTION}' already exists. "
                "Use --rebuild to replace it, or run inspect_index.py."
            )
        client.delete_collection(name=COLLECTION)

    embeddings = MiniLMEmbeddings()
    vectorstore = Chroma(
        client=client,
        collection_name=COLLECTION,
        embedding_function=embeddings,
    )
    # Small batches reduce peak memory requirements for resource-constrained hosts.
    for offset in range(0, len(chunks), 16):
        batch = chunks[offset:offset + 16]
        vectorstore.add_documents(
            batch,
            ids=[doc.metadata["chunk_id"] for doc in batch],
        )
    count = client.get_collection(COLLECTION).count()
    if count != len(chunks):
        raise RuntimeError(f"Chroma contains {count} chunks, expected {len(chunks)}")

    report = {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "collection": COLLECTION,
        "embedding_model": MODEL_NAME,
        "embedding_dimensions": 384,
        "chunk_size_characters": CHUNK_SIZE,
        "chunk_overlap_characters": CHUNK_OVERLAP,
        "policy_sections_or_pages_parsed": len(sections),
        **corpus_summary(chunks),
        "sample_citation": {
            k: chunks[0].metadata[k]
            for k in ("document_id", "title", "section", "source", "chunk_id")
        },
    }
    report_path = ROOT / "reports" / "milestone4_index_report.json"
    report_path.parent.mkdir(exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report
