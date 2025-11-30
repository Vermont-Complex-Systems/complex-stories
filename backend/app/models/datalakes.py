"""
Datalake registry models for tracking available datalakes.
"""

from sqlalchemy import Column, String, DateTime, Text, JSON, ForeignKey
from sqlalchemy.sql import func
from ..core.database import Base


class Datalake(Base):
    """Registry of available datalakes."""

    __tablename__ = "datalakes"

    dataset_id = Column(String, primary_key=True)
    data_location = Column(String, nullable=False)
    data_format = Column(String, nullable=False, default="ducklake")
    description = Column(Text)
    tables_metadata = Column(JSON)  # Store ducklake table metadata for version control
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<Datalake(id='{self.dataset_id}', format='{self.data_format}', location='{self.data_location}')>"


class EntityMapping(Base):
    """Entity mappings for datalakes."""

    __tablename__ = "entity_mappings"

    id = Column(String, primary_key=True)  # dataset_id:local_id
    dataset_id = Column(String, ForeignKey("datalakes.dataset_id"), nullable=False)
    local_id = Column(String, nullable=False)
    entity_id = Column(String, nullable=False)  # standardized identifier
    entity_name = Column(String, nullable=False)
    entity_ids = Column(JSON)  # alternate identifiers
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<EntityMapping(local='{self.local_id}', entity='{self.entity_id}')>"