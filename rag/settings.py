"""Deterministic and environment-configurable settings for the index."""
from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CORPUS_DIR = ROOT / "policy_corpus"
MANIFEST_PATH = ROOT / "corpus_manifest.json"
INDEX_DIR = Path(os.getenv("RAG_CHROMA_DIR", str(ROOT / "chroma_db"))).resolve()
COLLECTION = os.getenv("RAG_COLLECTION", "vendelligent_hr_policies")
CHUNK_SIZE = 850
CHUNK_OVERLAP = 130
