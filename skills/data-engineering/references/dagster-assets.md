# Dagster Asset Patterns

This reference provides detailed patterns for writing Dagster assets in Complex Stories pipelines.

## Asset Basics

### Simple Asset
```python
from dagster import asset, AssetExecutionContext

@asset(
    key_prefix=["project"],  # Namespace assets by project
    compute_kind="duckdb",   # Tag for UI grouping
    group_name="import"      # Logical grouping (import/transform/export)
)
def my_asset(
    context: AssetExecutionContext,
    duckdb_resource: DuckDBResource
) -> None:
    """Asset docstring appears in Dagster UI"""

    context.log.info("Starting asset execution")
    # Asset logic here
    context.log.info("Asset completed")
```

### Asset with Dependencies
```python
@asset(
    key_prefix=["project"],
    deps=["project/upstream_asset"],  # Explicit dependency
    compute_kind="duckdb",
    group_name="transform"
)
def dependent_asset(
    context: AssetExecutionContext,
    duckdb_resource: DuckDBResource
) -> None:
    """This asset runs after upstream_asset"""
    pass
```

### Asset with Multiple Dependencies
```python
@asset(
    key_prefix=["project"],
    deps=[
        "project/asset_one",
        "project/asset_two",
        "project/asset_three"
    ],
    compute_kind="api",
    group_name="export"
)
def export_asset(context: AssetExecutionContext) -> None:
    """Runs after all dependencies complete"""
    pass
```

## Asset Groups

Organize assets into logical groups for UI clarity:

```python
@asset(group_name="import")    # External API fetching
@asset(group_name="transform")  # Data processing
@asset(group_name="export")     # PostgreSQL uploads
```

## Compute Kinds

Tag assets by computation type:

```python
@asset(compute_kind="duckdb")   # DuckDB SQL operations
@asset(compute_kind="api")      # External API calls
@asset(compute_kind="pandas")   # Pandas transformations
@asset(compute_kind="python")   # General Python code
```

## Asset Checks

Validate data quality:

```python
from dagster import asset_check, AssetCheckResult, AssetCheckSeverity

@asset_check(
    asset="project/raw_data",
    description="Verify raw data has records"
)
def check_raw_data_not_empty(
    context: AssetExecutionContext,
    duckdb_resource: DuckDBResource
) -> AssetCheckResult:
    """Asset checks validate data quality"""

    conn = duckdb_resource.get_connection()
    count = conn.execute(
        "SELECT COUNT(*) FROM project.raw.data"
    ).fetchone()[0]
    conn.close()

    passed = count > 0
    return AssetCheckResult(
        passed=passed,
        description=f"Found {count} records",
        severity=AssetCheckSeverity.ERROR if not passed else None
    )
```

## Working with DuckDB

### Table Creation Pattern
```python
@asset(key_prefix=["project"], compute_kind="duckdb", group_name="import")
def raw_table(
    context: AssetExecutionContext,
    duckdb_resource: DuckDBResource
) -> None:
    """Create and populate raw data table"""

    conn = duckdb_resource.get_connection()

    # Create table (idempotent)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS project.raw.data (
            id VARCHAR PRIMARY KEY,
            field1 VARCHAR,
            field2 INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Insert/update data
    data = [("id1", "value1", 100), ("id2", "value2", 200)]
    conn.executemany(
        "INSERT OR REPLACE INTO project.raw.data (id, field1, field2) VALUES (?, ?, ?)",
        data
    )

    # Log progress
    row_count = conn.execute("SELECT COUNT(*) FROM project.raw.data").fetchone()[0]
    context.log.info(f"Table has {row_count} rows")

    conn.close()
```

### Query and Transform Pattern
```python
@asset(
    key_prefix=["project"],
    deps=["project/raw_table"],
    compute_kind="duckdb",
    group_name="transform"
)
def transformed_table(
    context: AssetExecutionContext,
    duckdb_resource: DuckDBResource
) -> None:
    """Transform raw data with SQL"""

    conn = duckdb_resource.get_connection()

    # Complex SQL transformation
    conn.execute("""
        CREATE OR REPLACE TABLE project.transform.aggregated AS
        SELECT
            field1,
            COUNT(*) as count,
            AVG(field2) as avg_field2,
            SUM(field2) as sum_field2,
            MIN(created_at) as first_seen,
            MAX(created_at) as last_seen
        FROM project.raw.data
        WHERE field2 > 0
        GROUP BY field1
        ORDER BY count DESC
    """)

    result = conn.execute("SELECT COUNT(*) FROM project.transform.aggregated").fetchone()
    context.log.info(f"Generated {result[0]} aggregated rows")

    conn.close()
```

### DuckDB to DataFrame Pattern
```python
@asset(key_prefix=["project"], deps=["project/transformed_table"], compute_kind="pandas", group_name="export")
def export_to_api(
    context: AssetExecutionContext,
    duckdb_resource: DuckDBResource,
    api_client: ComplexStoriesAPIClient
) -> None:
    """Export DuckDB data via pandas to API"""

    conn = duckdb_resource.get_connection()

    # Query to DataFrame
    df = conn.execute("""
        SELECT field1, count, avg_field2
        FROM project.transform.aggregated
    """).df()

    conn.close()

    # Pandas transformations
    df['field1_clean'] = df['field1'].str.strip().str.lower()
    df['created_at'] = pd.Timestamp.now().strftime('%Y-%m-%dT%H:%M:%S')

    # Upload
    records = df.to_dict('records')
    api_client.bulk_upload("project/data/bulk", records, batch_size=5000)
    context.log.info(f"Uploaded {len(records)} records")
```

## Working with External APIs

### Basic API Fetch Pattern
```python
@asset(key_prefix=["project"], compute_kind="api", group_name="import")
def fetch_external_data(
    context: AssetExecutionContext,
    duckdb_resource: DuckDBResource,
    api_client: ExternalAPIResource
) -> None:
    """Fetch data from external API"""

    conn = duckdb_resource.get_connection()

    # Create staging table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS project.raw.external_data (
            id VARCHAR PRIMARY KEY,
            data JSON,
            fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Fetch from API
    entities = ["entity1", "entity2", "entity3"]
    for entity in entities:
        data = api_client.fetch(entity)
        conn.execute(
            "INSERT OR REPLACE INTO project.raw.external_data (id, data) VALUES (?, ?)",
            [entity, json.dumps(data)]
        )
        context.log.info(f"Fetched data for {entity}")

    conn.close()
```

### Paginated API Fetch Pattern
```python
@asset(key_prefix=["project"], compute_kind="api", group_name="import")
def fetch_paginated_data(
    context: AssetExecutionContext,
    duckdb_resource: DuckDBResource,
    api_client: ExternalAPIResource
) -> None:
    """Fetch all pages from paginated API"""

    conn = duckdb_resource.get_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS project.raw.paginated_data (
            id VARCHAR PRIMARY KEY,
            field1 VARCHAR,
            field2 INTEGER
        )
    """)

    page = 1
    total_records = 0

    while True:
        response = api_client.fetch_page(page)

        if not response['results']:
            break

        # Batch insert
        records = [
            (r['id'], r['field1'], r['field2'])
            for r in response['results']
        ]

        conn.executemany(
            "INSERT OR REPLACE INTO project.raw.paginated_data VALUES (?, ?, ?)",
            records
        )

        total_records += len(records)
        context.log.info(f"Page {page}: {len(records)} records (total: {total_records})")

        if not response['has_next']:
            break

        page += 1

    conn.close()
```

## Incremental Processing

### Sync Status Tracking
```python
@asset(key_prefix=["project"], compute_kind="duckdb", group_name="import")
def incremental_sync(
    context: AssetExecutionContext,
    duckdb_resource: DuckDBResource,
    api_client: ExternalAPIResource
) -> None:
    """Incrementally sync data using status tracking"""

    conn = duckdb_resource.get_connection()

    # Create sync status table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS project.cache.sync_status (
            entity_id VARCHAR PRIMARY KEY,
            last_synced_at TIMESTAMP,
            records_count INTEGER
        )
    """)

    # Get entities to sync
    entities = ["entity1", "entity2", "entity3"]

    for entity_id in entities:
        # Check sync status
        status = conn.execute(
            "SELECT last_synced_at FROM project.cache.sync_status WHERE entity_id = ?",
            [entity_id]
        ).fetchone()

        if status:
            last_sync = status[0]
            context.log.info(f"{entity_id}: Last synced at {last_sync}")
            # Fetch only new data
            data = api_client.fetch_since(entity_id, since=last_sync)
        else:
            context.log.info(f"{entity_id}: First sync")
            # Fetch all data
            data = api_client.fetch_all(entity_id)

        # Store data (implementation specific)
        # ...

        # Update sync status
        conn.execute("""
            INSERT OR REPLACE INTO project.cache.sync_status (entity_id, last_synced_at, records_count)
            VALUES (?, CURRENT_TIMESTAMP, ?)
        """, [entity_id, len(data)])

    conn.close()
```

## Error Handling

### Robust Asset Pattern
```python
@asset(key_prefix=["project"], compute_kind="api", group_name="import")
def robust_fetch(
    context: AssetExecutionContext,
    duckdb_resource: DuckDBResource,
    api_client: ExternalAPIResource
) -> None:
    """Fetch with error handling and retries"""

    conn = duckdb_resource.get_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS project.raw.data (
            id VARCHAR PRIMARY KEY,
            data JSON,
            fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS project.cache.fetch_errors (
            entity_id VARCHAR,
            error_message VARCHAR,
            attempted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    entities = ["entity1", "entity2", "entity3"]
    success_count = 0
    error_count = 0

    for entity in entities:
        try:
            data = api_client.fetch(entity)
            conn.execute(
                "INSERT OR REPLACE INTO project.raw.data (id, data) VALUES (?, ?)",
                [entity, json.dumps(data)]
            )
            success_count += 1

        except Exception as e:
            error_msg = str(e)
            context.log.warning(f"Failed to fetch {entity}: {error_msg}")

            conn.execute(
                "INSERT INTO project.cache.fetch_errors (entity_id, error_message) VALUES (?, ?)",
                [entity, error_msg]
            )
            error_count += 1

    context.log.info(f"Completed: {success_count} success, {error_count} errors")
    conn.close()
```

## Performance Optimization

### Batch Insert Pattern
```python
# Efficient: Single executemany call
records = [(id1, val1), (id2, val2), ..., (id1000, val1000)]
conn.executemany("INSERT INTO table VALUES (?, ?)", records)

# Inefficient: Multiple execute calls
for id, val in records:
    conn.execute("INSERT INTO table VALUES (?, ?)", [id, val])
```

### Query Optimization Pattern
```python
# Use indexes for lookup tables
conn.execute("CREATE INDEX IF NOT EXISTS idx_entity ON project.raw.data(entity_id)")

# Use views for complex queries used multiple times
conn.execute("""
    CREATE OR REPLACE VIEW project.transform.active_entities AS
    SELECT * FROM project.raw.data
    WHERE status = 'active' AND last_updated > CURRENT_DATE - INTERVAL 30 DAY
""")

# Use EXPLAIN to analyze queries
plan = conn.execute("EXPLAIN SELECT * FROM project.raw.data WHERE entity_id = 'x'").fetchall()
```

## Asset Return Values

### Materializing Data
Assets can return data for downstream consumption:

```python
from dagster import asset, Output

@asset(key_prefix=["project"], compute_kind="python")
def computed_value(context: AssetExecutionContext) -> Output[int]:
    """Asset that returns a value"""
    value = 42
    return Output(value, metadata={"computed_value": value})

@asset(key_prefix=["project"], deps=["project/computed_value"])
def use_computed_value(
    context: AssetExecutionContext,
    computed_value: int  # Automatically passed
) -> None:
    """Use returned value from upstream asset"""
    context.log.info(f"Received value: {computed_value}")
```

However, for Complex Stories pipelines, **prefer storing data in DuckDB** rather than passing as return values. This provides:
- Persistence across runs
- Ability to query/inspect intermediate results
- Clear data lineage in database schemas
