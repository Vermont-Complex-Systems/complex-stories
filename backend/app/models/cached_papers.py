from sqlalchemy import Column, Integer, String, DateTime, JSON, Boolean
from sqlalchemy.sql import func
from ..core.database import Base


class CachedPaper(Base):
    """
    Cache for OpenAlex paper data to reduce API calls.

    Stores simplified paper metadata for interdisciplinarity annotation.
    Papers are cached on first fetch and served from cache on subsequent requests.
    """
    __tablename__ = "cached_papers"

    id = Column(String, primary_key=True)  # OpenAlex work ID (e.g., "W2118557509")
    title = Column(String, nullable=False)
    year = Column(Integer, nullable=True)
    abstract = Column(String, nullable=True)  # Full abstract text
    authors = Column(JSON, nullable=True)  # List of author names
    topics = Column(JSON, nullable=True)  # List of topic objects with id, display_name, score
    doi = Column(String, nullable=True)
    is_open_access = Column(Boolean, default=False)

    # Cache metadata
    cached_at = Column(DateTime(timezone=True), server_default=func.now())

    def to_dict(self):
        """Convert to dictionary format matching OpenAlex API response."""
        return {
            "id": self.id,
            "title": self.title,
            "year": self.year,
            "abstract": self.abstract,
            "authors": self.authors,
            "topics": self.topics,
            "doi": self.doi,
            "is_open_access": self.is_open_access
        }
