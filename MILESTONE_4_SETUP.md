# Milestone 4 — Document Ingestion & Vector Indexing

## Scope

Ingest only the approved 19 policy documents listed in `corpus_manifest.json` (18 `.md` plus `VND-HR-REG.pdf`).
The Markdown corpus is processed by heading; the PDF is processed by physical page.
The Chroma index stores full source citations: document ID/title, section or PDF page, original relative file path, document version, effective date, and chunk ID.
**No employee data from Neon/PostgreSQL is embedded.** This milestone does not generate LLM answers.

## Installation (PowerShell, from repository root)

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-rag.txt
```

Merge the six lines in `requirements-rag.txt` into your existing `requirements.txt` before deploying to Render (do not remove existing FastAPI/PostgreSQL dependencies).

## Build the vector index

```powershell
python -m scripts.index_policies
```

The first run downloads the free `sentence-transformers/all-MiniLM-L6-v2` ONNX model (~90 MB) and can take longer. It does **not** require Groq or a database URL.
Run `python -m scripts.index_policies --rebuild` to intentionally replace the index after changing the corpus/chunking strategy.
The script **refuses** an accidental second build without `--rebuild` to avoid duplicates.

Expected outcomes:
- `document_count: 19`
- Nonzero `chunk_count`
- Both `md` and `pdf` in `formats`
- `chroma_db/` created locally
- `reports/milestone4_index_report.json` generated

The exact number of chunks depends on the fixed chunking settings and corpus content; use the generated report rather than expecting a hard-coded count.

## Inspect retrieved chunks

```powershell
python -m scripts.inspect_index --query "How many annual leave days do employees receive?" --k 3
python -m scripts.inspect_index --query "Can I work from another country?" --k 3
python -m scripts.inspect_index --query "What is the PTO approval process?" --document-id VND-SOP-103 --k 3
```

The retrieved document section, source path, chunk ID, and text snippet should be printed. The returned distance is **not** a probability/confidence score.

## Tests

```powershell
python -m pytest tests/test_policy_ingestion.py -v
python -m pytest -v
```

## Git

Ensure `.gitignore` contains `chroma_db/` and `.env`, and do not commit model caches or passwords.

```powershell
git add rag/ scripts/index_policies.py scripts/inspect_index.py tests/test_policy_ingestion.py requirements-rag.txt MILESTONE_4_SETUP.md reports/milestone4_index_report.json requirements.txt
git status
git commit -m "Milestone 4: Build citation-aware policy vector index"
git push
```

## Design choices to document

- Corpus manifest allowlist plus SHA-256 to detect unintended source changes.
- Section-aware Markdown extraction; PDF pages retain original page numbers.
- Recursive character chunking, 850 characters with 130-character overlap; deterministic with unchanged input.
- Local MiniLM-L6-v2 through FastEmbed/ONNX, 384 dimensions, no API key.
- Chroma as local persisted index, separate from the PostgreSQL employee database.
- Deliberate rebuild-only indexing, with fixed identifiers and per-document audit counts.

## Render note (future Milestone 12)

Render Free offers 512 MB RAM and ephemeral runtime filesystem. The local Chroma directory is **not persistent** on Render's free web service. At deployment, either prepare the small index as part of the build artifact or rebuild it as part of startup, then measure memory use and cold-start times. Don't depend on an index created once on the runtime filesystem surviving restarts.

## Troubleshooting

- `ModuleNotFoundError`: confirm the virtual environment is activated and run the pip install command.
- `Checksum mismatch`: restore the reviewed Milestone 2 policy file, or update the manifest intentionally after changing it.
- `Collection already exists`: use `inspect_index` or deliberately use `--rebuild`.
- Model download fails: verify the machine has internet access, then rerun.
- Index empty: check 19 corpus files and `corpus_manifest.json` in the root directory.
