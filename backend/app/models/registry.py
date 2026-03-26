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
  entity_mapping, sources, endpoint_schema, format_config,
  catalog, ownership, lineage, created_at, updated_at.

format_config groups all storage-format-specific fields to avoid column churn:
  parquet_hive: {tables_metadata, partitioning, availability}
  ducklake:     {ducklake_data_path, data_schema, availability}
  duckdb:       {}
"""

from sqlalchemy import Column, String, DateTime, Text, JSON, ForeignKeyConstraint
from sqlalchemy.sql import func
from ..core.database import Base


class Dataset(Base):
    """Registry of available datasets across all supported backends."""

    __tablename__ = "datasets"

    # Namespace / producer identity
    catalog = Column(String, default="vcsi")         # producing org; catalog.domain.dataset_id
    domain = Column(String, primary_key=True)        # owning domain: wikimedia | storywrangler | ...
    dataset_id = Column(String, primary_key=True)    # name within domain: ngrams | revisions | ...
    
    data_location = Column(String, nullable=False)   # base path or connection string
    data_format = Column(String, nullable=False)     # ducklake | parquet_hive | duckdb
    description = Column(Text)

    # Format-specific config
    format_config = Column(JSON)     # parquet_hive: {tables_metadata, partitioning, availability}
                                     # ducklake:     {ducklake_data_path, data_schema, availability}

    # Shared optional metadata
    entity_mapping = Column(JSON)     # {path, local_id_column, entity_id_column}
    sources = Column(JSON)            # source URLs for validation
    endpoint_schema = Column("endpoint_schemas", JSON)   # {type, time_dimension?, granularities?, filter_dimensions?}

    # Ownership and succession
    ownership = Column(JSON)   # {owner_group, contact, status, storage_risk}

    # Lineage
    lineage = Column(JSON)     # {derived_from, produced_by, consumers}

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
    entity_ids = Column(JSON)  # alternate identifiers, list[str] e.g. ['iso:US', 'local:babynames:united_states']
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<EntityMapping(local='{self.local_id}', entity='{self.entity_id}')>"
