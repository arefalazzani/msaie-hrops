# Vendelligent HR RAG Corpus — Milestone 2

A reviewed, minimally corrected ingestion-ready version of the original synthetic policy suite, ready for the Quantic project. **No new HR policies were added.**

## Contents

- `policy_corpus/` — 19 documents for ingestion: 18 Markdown + one PDF, with unique document IDs.
- `corpus_manifest.json` — document titles, IDs, formats, version, effective date, checksums.
- `REVIEW_AND_CORRECTIONS.md` — exactly what was changed and why.
- `MILESTONE_2_SETUP.md` — these instructions; intentionally named to avoid overwriting your existing project README.

## How to add to your existing GitHub repo

1. Extract this ZIP into the **root** of your Python project.
2. Add a `policy_corpus/` directory to your project root containing the 19 files.
3. Keep the manifest and review notes in the project root (or move them to `docs/`).
4. Run `python -m pytest -v` to ensure Milestone 1 still works. Do not overwrite your existing root `README.md`.
5. Commit the files:

    git add policy_corpus corpus_manifest.json REVIEW_AND_CORRECTIONS.md MILESTONE_2_SETUP.md
    git commit -m "Milestone 2: Add reviewed synthetic HR policy corpus"
    git push

The ingestion and vector indexing implementation comes later in Milestone 4. There is **no need to install a PDF parser or LangChain yet** to complete this milestone.

## Policy scope

These documents are synthetic and are **not** intended as legal or real-company HR advice.
