# Milestone 5 — Policy Retrieval Service

## Prerequisites
- Milestones 1–4 completed, with existing `chroma_db/` index built from the 19-policy corpus.
- Activate your Python environment. The Milestone 4 dependencies are sufficient.
- Extract the ZIP **into the repository root**. It adds files; it does not overwrite `rag/index.py` or your existing corpus.

## 1. Run fast tests (does not load embeddings)

```powershell
python -m pytest tests/test_policy_retrieval.py -v
```

## 2. Query the existing vector database

```powershell
python -m scripts.search_policies --query "How many annual leave days do employees receive?" --k 5
python -m scripts.search_policies --query "Can I work abroad for six weeks?" --k 5
```

## 3. Test metadata filtering

```powershell
python -m scripts.search_policies --query "How do I request PTO?" --document-id VND-SOP-103 --k 3
python -m scripts.search_policies --query "What are the rules for international remote work?" --document-type Policy --k 5
python -m scripts.search_policies --query "HR policy document register" --format pdf --k 2
```

## 4. Optional source diversification for a cross-document question

```powershell
python -m scripts.search_policies --query "What policy and procedure apply to PTO requests?" --k 5 --max-per-document 2
```

This caps the returned passages at 2 from any single document so that more documents may be represented; it is **not learned reranking**.

## 5. Review machine-readable citations for future MCP use

```powershell
python -m scripts.search_policies --query "annual leave" --k 2 --json
```

## 6. Run a small retrieval baseline / K ablation

```powershell
python -m scripts.evaluate_retrieval
```

It reports document recall@K, any-gold-found@K, and measured retrieval latency for `K=3` and `K=5`, saving details to `reports/milestone5_retrieval_baseline.json`. These **are retrieval metrics**, not groundedness or final answer quality metrics. Confirm the manually authored gold document labels against your corpus and investigate poor retrieval cases.

## 7. Run the entire test suite

```powershell
python -m pytest -v
```

## 8. Commit changes (do not commit secrets or index files)

```powershell
git status
git add rag/retrieval.py scripts/search_policies.py scripts/evaluate_retrieval.py tests/test_policy_retrieval.py evaluation/retrieval_gold.json MILESTONE_5_SETUP.md reports/milestone5_retrieval_baseline.json
git commit -m "Milestone 5: Reusable HR policy retrieval and evaluation"
git push
```

## Design notes
- Milestone 4 remains source of truth for corpus parsing, embeddings, chunking and index.
- `rag/retrieval.py` is the reusable API consumed by answer generation (Milestone 6) and policy MCP tools (Milestone 7).
- `k=5` is the initial default; no arbitrary similarity threshold is claimed to be calibrated.
- Metadata filters restrict retrieval to matched `document_id`, `document_type` or `format`.
- Chroma *distance* is not a calibrated confidence percentage.
- No LLM calls / query rewriting or reranking in this milestone. These are optional in the Quantic brief; filtering meets that optional enhancement, and query rewriting may be reconsidered after evaluation.
- PostgreSQL stays independent and will be used via structured MCP tools, not blended into the vector index.
- Local `.env`, database credentials and `chroma_db/` should remain untracked.
