"""
SQLAlchemy models for Complex Stories backend.
"""

from ..core.database import Base
from .academic import Paper, Coauthor
from .annotation_datasets import AcademicResearchGroups
from .auth import User, AnnotationHistory

__all__ = ["Base", "Paper", "Coauthor", "AcademicResearchGroups", "User", "AnnotationHistory"]