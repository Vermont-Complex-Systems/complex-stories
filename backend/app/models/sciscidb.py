"""
ScisciDB database models for PostgreSQL storage
"""
from sqlalchemy import Column, Integer, String, Index
from ..core.database import Base

class FieldMetric(Base):
    """Generic dimensional table for field-year-metric combinations"""
    __tablename__ = "field_metrics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    field = Column(String(100), nullable=False)
    year = Column(Integer, nullable=False)
    metric_type = Column(String(50), nullable=False)  # 'total', 'has_abstract', 'has_full_text', etc.
    count = Column(Integer, nullable=False)

    # Indexes for fast querying + unique constraint for upserts
    __table_args__ = (
        Index("ix_field_metrics_field", "field"),
        Index("ix_field_metrics_year", "year"),
        Index("ix_field_metrics_metric_type", "metric_type"),
        Index("ix_field_metrics_field_year_metric", "field", "year", "metric_type", unique=True),
    )

# Keep old table for backward compatibility during transition
class FieldYearCount(Base):
    """Legacy precomputed field-year counts - deprecated, use FieldMetric"""
    __tablename__ = "field_year_counts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    field = Column(String(100), nullable=False)
    year = Column(Integer, nullable=False)
    count = Column(Integer, nullable=False)

    __table_args__ = (
        Index("ix_field_year_counts_field", "field"),
        Index("ix_field_year_counts_year", "year"),
        Index("ix_field_year_counts_field_year", "field", "year", unique=True),
    )