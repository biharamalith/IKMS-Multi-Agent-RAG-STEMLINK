"""Utilities for serializing retrieved document chunks."""

from typing import List, Tuple

from langchain_core.documents import Document


def serialize_chunks(docs: List[Document]) -> str:
    """Serialize a list of Document objects into a formatted CONTEXT string.

    Formats chunks with indices and page numbers as specified in the PRD:
    - Chunks are numbered (Chunk 1, Chunk 2, etc.)
    - Page numbers are included in the format "page=X"
    - Produces a clean CONTEXT section for agent consumption

    Args:
        docs: List of Document objects with metadata.

    Returns:
        Formatted string with all chunks serialized.
    """
    context_parts = []

    for idx, doc in enumerate(docs, start=1):
        # Extract page number from metadata
        page_num = doc.metadata.get("page") or doc.metadata.get(
            "page_number", "unknown"
        )

        # Format chunk with index and page number
        chunk_header = f"Chunk {idx} (page={page_num}):"
        chunk_content = doc.page_content.strip()

        context_parts.append(f"{chunk_header}\n{chunk_content}")

    return "\n\n".join(context_parts)


def serialize_chunks_with_citations(
    docs: List[Document],
) -> Tuple[str, dict]:
    """Serialize document chunks with stable citation IDs and return citation mapping.

    Enhancement for Feature 4 (Evidence-Aware Answers):
    - Generates stable chunk IDs (C1, C2, C3, etc.)
    - Creates a citation mapping for later reference
    - Formats context with citation IDs for agent consumption

    Args:
        docs: List of Document objects with metadata.

    Returns:
        Tuple of:
        - context_str: Formatted context string with citation IDs [C1], [C2], etc.
        - citation_map: Dict mapping chunk IDs to metadata
                       {
                           "C1": {
                               "page": 5,
                               "snippet": "First 100 chars of content...",
                               "source": "filename.pdf"
                           },
                           ...
                       }
    """
    context_parts = []
    citation_map = {}

    for idx, doc in enumerate(docs, start=1):
        chunk_id = f"C{idx}"
        page_num = doc.metadata.get("page") or doc.metadata.get(
            "page_number", "unknown"
        )
        source = doc.metadata.get("source", "unknown")
        content = doc.page_content.strip()

        # Create citation map entry with metadata
        citation_map[chunk_id] = {
            "page": page_num,
            "snippet": content[:100] + "..." if len(content) > 100 else content,
            "source": source,
            "full_content": content,
        }

        # Format chunk with citation ID
        chunk_header = f"[{chunk_id}] Chunk from page {page_num}:"
        context_parts.append(f"{chunk_header}\n{content}")

    context_str = "\n\n".join(context_parts)

    return context_str, citation_map
