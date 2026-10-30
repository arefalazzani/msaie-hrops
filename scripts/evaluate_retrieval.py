"""Milestone 5 baseline: evaluate document-level retrieval for K=3 and K=5.

This is intentionally NOT the complete 20–30-item system evaluation required
later by Quantic. Relevance labels are human-reviewed starting hypotheses.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
from statistics import mean

from rag.retrieval import open_policy_retriever
from rag.settings import ROOT

GOLD = ROOT / "evaluation" / "retrieval_gold.json"
DEFAULT_REPORT = ROOT / "reports" / "milestone5_retrieval_baseline.json"


def evaluate(retriever, cases: list[dict], k_values=(3, 5)) -> dict:
    results = []
    for k in k_values:
        rows = []
        for case in cases:
            response = retriever.search(case["query"], k=k)
            ids = [hit["document_id"] for hit in response["results"]]
            expected = set(case["expected_document_ids"])
            retrieved = set(ids)
            matched = sorted(expected & retrieved)
            rows.append({
                "id": case["id"],
                "query": case["query"],
                "gold_document_ids": sorted(expected),
                "retrieved_document_ids": ids,
                "matched_document_ids": matched,
                "document_recall": len(matched) / len(expected),
                "any_gold_found": bool(matched),
                "latency_ms": response["latency_ms"],
            })
        results.append({
            "k": k,
            "case_count": len(rows),
            "mean_document_recall_at_k": round(mean(r["document_recall"] for r in rows), 4),
            "any_gold_found_rate": round(mean(r["any_gold_found"] for r in rows), 4),
            "mean_retrieval_latency_ms": round(mean(r["latency_ms"] for r in rows), 2),
            "cases": rows,
        })
    return {"evaluated_at_utc": datetime.now(timezone.utc).isoformat(),
            "description": "Document-level retrieval baseline; no generated answers evaluated.",
            "gold_file": "evaluation/retrieval_gold.json", "comparisons": results}


def main() -> None:
    parser = argparse.ArgumentParser(description="Run K=3 vs K=5 retrieval comparison")
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    args = parser.parse_args()
    cases = json.loads(GOLD.read_text(encoding="utf-8"))
    report = evaluate(open_policy_retriever(), cases)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    for group in report["comparisons"]:
        print(f"K={group['k']} | document recall@K={group['mean_document_recall_at_k']:.1%} | "
              f"any-gold@K={group['any_gold_found_rate']:.1%} | "
              f"mean retrieval time={group['mean_retrieval_latency_ms']:.0f} ms")
    print(f"Saved detailed evaluation: {args.report}")
    print("Review failures and gold labels manually; these scores are not answer quality scores.")


if __name__ == "__main__":
    main()
