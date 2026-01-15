"""LangGraph state schema for the multi-agent QA flow."""

from typing import TypedDict


class QAState(TypedDict):
    """State schema for the linear multi-agent QA flow.

    The state flows through three agents:
    1. Retrieval Agent: populates `context` from `question`
    2. Summarization Agent: generates `draft_answer` from `question` + `context`
    3. Verification Agent: produces final `answer` from `question` + `context` + `draft_answer`
    
    Enhancement (Feature 4: Citations):
    - `citations`: Mapping of chunk IDs (C1, C2, etc.) to metadata
    - `raw_docs`: Original Document objects for citation extraction
    """

    question: str
    context: str | None
    draft_answer: str | None
    answer: str | None
    citations: dict[str, dict] | None
    raw_docs: list | None
