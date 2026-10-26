"""Load the approved policy corpus, preserving exact source references.

Uses the Milestone 2 corpus_manifest.json as the authoritative allowlist.
No policy text is changed, rewritten, or generated during ingestion.
"""
from __future__ import annotations

from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import re

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

HEADING = re.compile(r"^(#{1,4})\s+(.+?)\s*$")


def policy_sections(markdown: str) -> list[tuple[str, str]]:
    """Return (section_path, verbatim-ish text) pairs from Markdown.

    Markdown headings are kept inside each section's text. The hierarchical
    section label (e.g. '5. Annual Leave / 5.1 Entitlement') is kept as metadata.
    """
    result: list[tuple[str, str]] = []
    headings: dict[int, str] = {}
    lines: list[str] = []
    section_label = "Document overview"

    def flush() -> None:
        content = "\n".join(lines).strip()
        if content:
            result.append((section_label, content))

    for line in markdown.replace("\r\n", "\n").split("\n"):
        matched = HEADING.match(line)
        if matched:
            flush()
            lines = [line]
            level = len(matched.group(1))
            headings[level] = matched.group(2)
            for previous in list(headings):
                if previous > level:
                    del headings[previous]
            if level == 1:
                section_label = "Document overview"
            else:
                section_label = " / ".join(
                    headings[n] for n in sorted(headings) if n > 1
                )
        else:
            lines.append(line)
    flush()
    return result


def _manifest_entries(manifest_path: Path) -> list[dict]:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
    records = manifest["documents"]
    if manifest.get("document_count") != len(records):
        raise ValueError("Manifest document_count disagrees with document list")
    ids = [r["document_id"] for r in records]
    names = [r["filename"] for r in records]
    if len(ids) != len(set(ids)) or len(names) != len(set(names)):
        raise ValueError("Duplicate document ID or filename in manifest")
    return records


def load_policy_documents(corpus_dir: Path, manifest_path: Path) -> list[Document]:
    """Parse Markdown by logical section, PDFs by page; validate source hashes."""
    corpus_dir = Path(corpus_dir)
    records = _manifest_entries(Path(manifest_path))
    documents: list[Document] = []
    for entry in records:
        filename = entry["filename"]
        path = corpus_dir / filename
        if Path(filename).name != filename:
            raise ValueError(f"Unsafe manifest filename: {filename}")
        if not path.is_file():
            raise FileNotFoundError(f"Manifest lists missing document: {path}")
        actual_hash = sha256(path.read_bytes()).hexdigest()
        if actual_hash != entry["sha256"]:
            raise ValueError(
                f"Checksum mismatch for {filename}. Restore the reviewed Milestone 2 "
                "corpus or update the manifest after an intentional revision."
            )
        metadata = {
            "document_id": entry["document_id"],
            "title": entry["title"],
            "source": f"policy_corpus/{filename}",
            "version": str(entry["version"]),
            "effective_date": entry["effective_date"],
            "document_type": entry["document_type"],
            "format": entry["format"],
        }
        if filename.lower().endswith(".md"):
            content = path.read_text(encoding="utf-8-sig")
            for section, text in policy_sections(content):
                documents.append(Document(
                    page_content=text,
                    metadata={**metadata, "section": section},
                ))
        elif filename.lower().endswith(".pdf"):
            import pymupdf  # lazy import: no PDF package needed for basic Markdown tests
            with pymupdf.open(path) as pdf:
                for page_number, page in enumerate(pdf, start=1):
                    text = page.get_text("text", sort=True).strip()
                    if not text:
                        continue
                    documents.append(Document(
                        page_content=text,
                        metadata={**metadata, "section": f"Page {page_number}", "page": page_number},
                    ))
        else:
            raise ValueError(f"Unexpected file type: {filename}")
    return documents


def chunk_policy_documents(
    documents: list[Document], chunk_size: int = 850, chunk_overlap: int = 130
) -> list[Document]:
    """Deterministic section-aware, overlap-preserving character chunking."""
    if not 0 <= chunk_overlap < chunk_size:
        raise ValueError("chunk_overlap must be smaller than chunk_size")
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
        length_function=len,
    )
    chunks: list[Document] = []
    per_doc: Counter[str] = Counter()
    for doc in documents:
        # Embed title and section path along with the policy text for context.
        prefix = f"{doc.metadata['title']}\n{doc.metadata['section']}\n"
        for passage in splitter.split_text(doc.page_content):
            doc_id = doc.metadata["document_id"]
            per_doc[doc_id] += 1
            chunk_num = per_doc[doc_id]
            chunks.append(Document(
                page_content=prefix + passage,
                metadata={**doc.metadata, "chunk_number": chunk_num,
                          "chunk_id": f"{doc_id}-{chunk_num:04d}",
                          "source_snippet": " ".join(passage.split())[:240]},
            ))
    return chunks


def corpus_summary(chunks: list[Document]) -> dict:
    return {
        "document_count": len(set(c.metadata["document_id"] for c in chunks)),
        "chunk_count": len(chunks),
        "chunks_per_document": dict(sorted(Counter(
            c.metadata["document_id"] for c in chunks
        ).items())),
        "formats": dict(sorted(Counter(
            c.metadata["format"] for c in chunks
        ).items())),
    }
