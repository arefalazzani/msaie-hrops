"""Lightweight retrieval diagnostic, not an LLM answer generator.

python -m scripts.inspect_index --query "How much PTO do employees receive?" --k 3
"""
import argparse

from rag.embeddings import MiniLMEmbeddings
from rag.settings import COLLECTION, INDEX_DIR


def main() -> None:
    parser = argparse.ArgumentParser(description="Preview chunks retrieved from Chroma")
    parser.add_argument("--query", default="How much annual leave does an employee receive?")
    parser.add_argument("--k", type=int, default=3)
    parser.add_argument("--document-id", help="Optional policy ID filter, e.g. VND-HR-004")
    args = parser.parse_args()
    if args.k < 1:
        parser.error("--k must be positive")
    if not INDEX_DIR.exists():
        parser.error("Index missing. First run: python -m scripts.index_policies")

    import chromadb
    from langchain_chroma import Chroma
    client = chromadb.PersistentClient(path=str(INDEX_DIR))
    if COLLECTION not in {col if isinstance(col, str) else col.name for col in client.list_collections()}:
        parser.error("Collection missing. First run: python -m scripts.index_policies")
    vectorstore = Chroma(
        client=client, collection_name=COLLECTION,
        embedding_function=MiniLMEmbeddings(),
    )
    kwargs = {"filter": {"document_id": args.document_id}} if args.document_id else {}
    results = vectorstore.similarity_search_with_score(args.query, k=args.k, **kwargs)
    print(f"Query: {args.query}\n")
    for i, (document, distance) in enumerate(results, 1):
        metadata = document.metadata
        print(f"{i}. {metadata['document_id']} | {metadata['section']}")
        print(f"   Source: {metadata['source']} | chunk: {metadata['chunk_id']}")
        print(f"   Distance: {distance:.4f} (lower is generally closer; NOT a confidence percentage)")
        print(f"   Snippet: {' '.join(document.page_content.split())[:300]}...\n")
    if not results:
        print("No matching chunks. Check the document ID filter and index contents.")


if __name__ == "__main__":
    main()
