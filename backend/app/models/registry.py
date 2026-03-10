"""
Generic dataset registry.

A Dataset is any external data backend registered with the platform.

Supported formats:
  - ducklake     : DuckLake catalog (tabular, versioned, schema-aware)
  - parquet_hive : Hive-partitioned parquet tree (tabular, file-based)
  - duckdb       : Plain DuckDB database file (no tables/schema metadata needed)

Primary key is (domain, dataset_id) so the same logical name (e.g. "ngrams") can
exist in multiple domains without collision.

Common fields (all formats):
  domain, dataset_id, data_location, data_format, description,
  entity_mapping, sources, created_at, updated_at.

Structured-data fields (ducklake, parquet_hive):
  tables_metadata, partitioning.

DuckLake-specific:
  ducklake_data_path, data_schema.
"""

from sqlalchemy import Column, String, DateTime, Text, JSON, ForeignKeyConstraint
from sqlalchemy.sql import func
from ..core.database import Base


class Dataset(Base):
    """Registry of available datasets across all supported backends."""

    __tablename__ = "datasets"

    domain = Column(String, primary_key=True)        # owning domain: wikimedia | storywrangler | ...
    dataset_id = Column(String, primary_key=True)    # name within domain: ngrams | revisions | ...
    data_location = Column(String, nullable=False)   # base path or connection string
    data_format = Column(String, nullable=False)     # ducklake | parquet_hive | duckdb
    description = Column(Text)

    # Structured/tabular formats (ducklake, parquet_hive)
    tables_metadata = Column(JSON)   # table_name -> [file_paths] or version info
    partitioning = Column(JSON)      # partitioning keys and scheme

    # DuckLake-specific
    ducklake_data_path = Column(String)  # path to ducklake catalog (.duckdb file)
    data_schema = Column(JSON)           # column_name -> type, for query reference

    # Shared optional metadata
    entity_mapping = Column(JSON)     # {path, local_id_column, entity_id_column}
    sources = Column(JSON)            # source URLs for validation
    endpoint_schemas = Column(JSON)   # [{type, time_dimension, entity_dimensions, filter_dimensions}]

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<Dataset(domain='{self.domain}', id='{self.dataset_id}', format='{self.data_format}')>"


class EntityMapping(Base):
    """Entity mappings for datasets."""

    __tablename__ = "entity_mappings"
    __table_args__ = (
        ForeignKeyConstraint(
            ["domain", "dataset_id"],
            ["datasets.domain", "datasets.dataset_id"],
        ),
    )

    id = Column(String, primary_key=True)  # domain:dataset_id:local_id
    domain = Column(String, nullable=False)
    dataset_id = Column(String, nullable=False)
    local_id = Column(String, nullable=False)
    entity_id = Column(String, nullable=False)  # standardized identifier
    entity_name = Column(String, nullable=False)
    entity_ids = Column(JSON)  # alternate identifiers
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<EntityMapping(local='{self.local_id}', entity='{self.entity_id}')>"
