"""
SQLAlchemy models for Complex Stories backend.
"""

from ..core.database import Base
from .academic import Paper, Coauthor

__all__ = ["Base", "Paper", "Coauthor"]