from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, default="annotator")  # admin, annotator, faculty
    payroll_name = Column(String(255), nullable=True, index=True)  # Links to AcademicResearchGroups.payroll_name
    orcid_id = Column(String(19), nullable=True, index=True)  # ORCID identifier (e.g., 0000-0002-1825-0097)
    openalex_id = Column(String(20), nullable=True, index=True)  # OpenAlex identifier (e.g., A5017712502)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)

    # Relationship to annotation history
    annotation_changes = relationship("AnnotationHistory", back_populates="user")


class AnnotationHistory(Base):
    __tablename__ = "annotation_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    record_id = Column(Integer, nullable=False)  # ID of the academic research group record
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    field_name = Column(String(50), nullable=False)
    old_value = Column(Text, nullable=True)
    new_value = Column(Text, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship to user
    user = relationship("User", back_populates="annotation_changes")