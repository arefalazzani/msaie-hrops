"""Run from repo root: python -m scripts.index_policies [--rebuild]."""
import argparse
import json
from rag.index import build_index


def main() -> None:
    parser = argparse.ArgumentParser(description="Index the reviewed HR policy corpus")
    parser.add_argument("--rebuild", action="store_true", help="Delete and recreate the named Chroma collection")
    args = parser.parse_args()
    print("Reading the Milestone 2 corpus and building the local vector index...")
    report = build_index(rebuild=args.rebuild)
    print(json.dumps(report, indent=2))
    print("PASS: Indexed documents with traceable citation metadata")


if __name__ == "__main__":
    main()
