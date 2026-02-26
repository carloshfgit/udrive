"""
Review Schemas

Esquemas Pydantic para validação de responses de avaliações.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class InstructorReviewResponse(BaseModel):
    """Schema de resposta para uma avaliação de instrutor."""
    id: UUID
    rating: int
    comment: str | None = None
    student_name: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class InstructorReviewsListResponse(BaseModel):
    """Schema de resposta para lista de avaliações do instrutor."""
    rating: float
    total_reviews: int
    reviews: list[InstructorReviewResponse]

    model_config = ConfigDict(from_attributes=True)
