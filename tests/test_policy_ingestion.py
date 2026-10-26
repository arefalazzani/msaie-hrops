"""Offline tests: parsing and chunking do not require an API key or model download."""
import hashlib
from pathlib import Path

import pytest
from langchain_core.documents import Document

from rag.corpus import policy_sections, load_policy_documents, chunk_policy_documents
from rag.settings import CORPUS_DIR, MANIFEST_PATH


def test_parses_all_manifest_documents():
    docs = load_policy_documents(CORPUS_DIR, MANIFEST_PATH)
    ids = {doc.metadata["document_id"] for doc in docs}
    assert len(ids) == 19
    assert {doc.metadata["format"] for doc in docs} == {"md", "pdf"}
    assert any(doc.metadata["document_id"] == "VND-HR-004" for doc in docs)
    assert all(doc.page_content.strip() for doc in docs)


def test_preserves_heading_hierarchy():
    sections = policy_sections("# Example\nIntro\n## 5. Leave\nDetails\n### 5.1 Rules\nRules")
    assert sections[0][0] == "Document overview"
    assert sections[1][0] == "5. Leave"
    assert sections[2][0] == "5. Leave / 5.1 Rules"


def test_chunk_ids_and_metadata_are_repeatable():
    docs = [Document(page_content="## 5. PTO\n" + ("This is the rule. " * 180),
                     metadata={"document_id": "TEST-01", "title": "Test Policy",
                               "section": "5. PTO", "source": "policy_corpus/test.md",
                               "format": "md"})]
    a = chunk_policy_documents(docs, chunk_size=250, chunk_overlap=40)
    b = chunk_policy_documents(docs, chunk_size=250, chunk_overlap=40)
    assert len(a) > 1
    assert [d.page_content for d in a] == [d.page_content for d in b]
    assert [d.metadata["chunk_id"] for d in a] == [d.metadata["chunk_id"] for d in b]
    assert all(d.metadata["section"] == "5. PTO" for d in a)


def test_manifest_hash_mismatch_is_detected(tmp_path):
    import json
    corpus = tmp_path / "policy_corpus"
    corpus.mkdir()
    (corpus / "T.md").write_text("# Policy\n## 1. Rule\nOriginal", encoding="utf-8")
    manifest = tmp_path / "corpus_manifest.json"
    manifest.write_text(json.dumps({"document_count": 1, "documents": [{
        "document_id": "T", "filename": "T.md", "format": "md", "title": "Policy",
        "version": "1", "effective_date": "2026-01-01", "document_type": "Policy",
        "sha256": "not_the_real_hash"
    }]}), encoding="utf-8")
    with pytest.raises(ValueError, match="Checksum mismatch"):
        load_policy_documents(corpus, manifest)
