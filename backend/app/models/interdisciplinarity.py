from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, UniqueConstraint, CheckConstraint, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from ..core.database import Base


class PaperAnnotation(Base):
    """
    Track interdisciplinarity annotations for papers.

    Supports dual auth: users can annotate anonymously (fingerprint) or logged in (user_id).
    Priority: user_id > fingerprint (logged-in annotations are more trusted).
    """
    __tablename__ = "paper_annotations"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Paper being annotated
    # Note: papers table has composite PK (id, ego_author_id), so we can't use FK
    # We validate paper existence in the API instead
    paper_id = Column(String, nullable=False, index=True)

    # Dual auth: either user_id (logged in) OR fingerprint (anonymous)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    fingerprint = Column(String(255), nullable=True, index=True)

    # The annotation: 1 (not interdisciplinary) to 5 (very interdisciplinary)
    interdisciplinarity_rating = Column(
        Integer,
        nullable=False,
        # Constraint to ensure rating is between 1 and 5
    )

    # Optional: confidence in the rating (1-5)
    confidence = Column(Integer, nullable=True)

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    # Relationship to user (if logged in)
    user = relationship("User", foreign_keys=[user_id])

    # Constraints
    __table_args__ = (
        # One annotation per paper per user/fingerprint
        # Note: This allows NULL user_id and NULL fingerprint, but prevents duplicate combinations
        UniqueConstraint(
            'paper_id', 'user_id', 'fingerprint',
            name='unique_paper_annotation',
            postgresql_nulls_not_distinct=True  # Treat NULLs as equal for uniqueness
        ),
        # Ensure rating is 1-5
        CheckConstraint(
            'interdisciplinarity_rating >= 1 AND interdisciplinarity_rating <= 5',
            name='valid_interdisciplinarity_rating'
        ),
        # Ensure confidence is 1-5 if provided
        CheckConstraint(
            'confidence IS NULL OR (confidence >= 1 AND confidence <= 5)',
            name='valid_confidence_rating'
        ),
        # Ensure either user_id OR fingerprint is provided (not both null)
        CheckConstraint(
            'user_id IS NOT NULL OR fingerprint IS NOT NULL',
            name='require_user_or_fingerprint'
        ),
        # Composite index for efficient queries
        Index('idx_paper_user', 'paper_id', 'user_id'),
        Index('idx_paper_fingerprint', 'paper_id', 'fingerprint'),
    )


# Pydantic models for API requests/responses

class AnnotationRequest(BaseModel):
    """Request to create or update an annotation."""
    paper_id: str = Field(..., description="OpenAlex paper ID (e.g., 'W2741809807')")
    interdisciplinarity_rating: int = Field(..., ge=1, le=5, description="Rating from 1 (not interdisciplinary) to 5 (very interdisciplinary)")
    confidence: Optional[int] = Field(None, ge=1, le=5, description="Confidence in rating (1-5)")
    fingerprint: Optional[str] = Field(None, description="Browser fingerprint (for anonymous users)")


class AnnotationResponse(BaseModel):
    """Response after creating/updating an annotation."""
    id: int
    paper_id: str
    user_id: Optional[int] = None
    fingerprint: Optional[str] = None
    interdisciplinarity_rating: int
    confidence: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserAnnotationsResponse(BaseModel):
    """List of annotations for a specific user/fingerprint."""
    annotations: list[AnnotationResponse]
    total: int
