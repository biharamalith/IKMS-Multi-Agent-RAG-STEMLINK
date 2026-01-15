"""Tools available to agents in the multi-agent RAG system."""

from langchain_core.tools import tool

from ..retrieval.vector_store import retrieve
from ..retrieval.serialization import (
    serialize_chunks,
    serialize_chunks_with_citations,
)


@tool(response_format="content_and_artifact")
def retrieval_tool(query: str):
    """Search the vector database for relevant document chunks.

    This tool retrieves the top 4 most relevant chunks from the Pinecone
    vector store based on the query. The chunks are formatted with page
    numbers and indices for easy reference.

    Args:
        query: The search query string to find relevant document chunks.

    Returns:
        Tuple of (serialized_content, artifact) where:
        - serialized_content: A formatted string containing the retrieved chunks
          with metadata. Format: "Chunk 1 (page=X): ...\n\nChunk 2 (page=Y): ..."
        - artifact: List of Document objects with full metadata for reference
    """
    # Retrieve documents from vector store
    docs = retrieve(query, k=4)

    # Serialize chunks with citations for Feature 4
    # Returns: (context_string_with_IDs, citation_map_dict)
    context, citations = serialize_chunks_with_citations(docs)

    # Return tuple: (serialized content with citations, artifact documents)
    # This follows LangChain's content_and_artifact response format
    # artifacts (docs) are used by agents.py to extract citations
    return context, docs
