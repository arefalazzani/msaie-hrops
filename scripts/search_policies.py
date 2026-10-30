"""Search policy evidence in existing ChromaDB index (no LLM required)."""
from __future__ import annotations

import argparse
import json

from rag.retrieval import open_policy_retriever


def main() -> None:
    parser = argparse.ArgumentParser(description="Search Vendelligent's HR policy index")
    parser.add_argument("--query", required=True, help="Employee's policy question")
    parser.add_argument("--k", type=int, default=5, help="Top-K chunks (1-20)")
    parser.add_argument("--document-id", action="append", dest="document_ids",
                        help="Filter by policy ID; repeat for multiple IDs")
    parser.add_argument("--document-type", choices=["Policy", "SOP", "Register"])
    parser.add_argument("--format", dest="source_format", choices=["md", "pdf"])
    parser.add_argument("--max-per-document", type=int, default=None,
                        help="Optional cap per source document (source diversification)")
    parser.add_argument("--json", action="store_true", dest="as_json",
                        help="Output machine-readable JSON, including full evidence text")
    args = parser.parse_args()

    try:
        report = open_policy_retriever().search(
            args.query, k=args.k, document_ids=args.document_ids,
            document_type=args.document_type, source_format=args.source_format,
            max_per_document=args.max_per_document,
        )
    except (ValueError, RuntimeError, FileNotFoundError) as exc:
        parser.error(str(exc))

    if args.as_json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return
    print(f"Query: {report['query']}")
    print(f"Returned: {report['result_count']}/{report['requested_k']} chunks | "
          f"Latency: {report['latency_ms']} ms")
    print("Chroma distance is NOT a confidence percentage. Lower is generally closer.\n")
    for item in report["results"]:
        print(f"{item['rank']}. {item['citation']} | distance={item['distance']}")
        print(f"   Title: {item['title']}")
        print(f"   Source: {item['source']} | chunk: {item['chunk_id']}")
        print(f"   Snippet: {item['source_snippet']}\n")
    if not report["results"]:
        print("No matching passages found. This is not evidence that a policy does not exist.")


if __name__ == "__main__":
    main()
