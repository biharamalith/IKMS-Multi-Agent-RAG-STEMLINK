from pydantic import BaseModel


class QuestionRequest(BaseModel):
    """Request body for the `/qa` endpoint.

    The PRD specifies a single field named `question` that contains
    the user's natural language question about the vector databases paper.
    """

    question: str


class QAResponse(BaseModel):
    """Response body for the `/qa` endpoint.

    From the API consumer's perspective we expose the final, verified answer
    plus context snippets and citation information.

    Enhancement for Feature 4 (Evidence-Aware Answers):
    - `citations`: Maps chunk IDs (C1, C2, etc.) to metadata for traceable sources
    """

    answer: str
    context: str
    citations: dict[str, dict] | None = None
