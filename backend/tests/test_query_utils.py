"""Tests for core/query_utils — load_system and resolve_flat_path.

No running backend, database, or allotax module required.
dataset_obj is mocked with SimpleNamespace; parquet files are written
into pytest's tmp_path using an in-process DuckDB connection.

Three time cases under test:
  1. No time axis    (parquet, no time_dimension)       — VT-Atlas-PDP style
  2. Time column     (parquet, time_dimension)          — babynames style
  3. Hive-partitioned time (parquet_hive, granularities) — ngrams style

Run from the backend directory:
    pytest tests/test_query_utils.py -v
"""
from types import SimpleNamespace

import duckdb
import pytest
from fastapi import HTTPException

from app.core.query_utils import load_system, resolve_flat_path


# ── helpers ───────────────────────────────────────────────────────────────────


def _ds(data_format, data_location, endpoint_schema, entity_mapping=None, format_config=None):
    """Minimal dataset_obj mock — mirrors what SQLAlchemy returns."""
    return SimpleNamespace(
        data_format=data_format,
        data_location=data_location,
        endpoint_schema=endpoint_schema,
        entity_mapping=entity_mapping,
        format_config=format_config,
    )


def _conn():
    return duckdb.connect()


# ── resolve_flat_path ─────────────────────────────────────────────────────────


class TestResolveFlatPath:
    def test_parquet_returns_quoted_location(self):
        ds = _ds("parquet", "/data/foo.parquet", {})
        assert resolve_flat_path(ds) == "'/data/foo.parquet'"

    def test_ducklake_single_file(self):
        ds = _ds("ducklake", "/data", {}, format_config={
            "tables_metadata": {"data": ["/data/file.parquet"]}
        })
        assert resolve_flat_path(ds) == "'/data/file.parquet'"

    def test_ducklake_multi_file(self):
        ds = _ds("ducklake", "/data", {}, format_config={
            "tables_metadata": {"data": ["/a.parquet", "/b.parquet"]}
        })
        assert resolve_flat_path(ds) == "['/a.parquet', '/b.parquet']"

    def test_ducklake_skips_adapter_key(self):
        # 'adapter' key should be ignored; 'data' key should be picked
        ds = _ds("ducklake", "/data", {}, format_config={
            "tables_metadata": {
                "adapter": ["/adapter.parquet"],
                "data":    ["/data.parquet"],
            }
        })
        assert resolve_flat_path(ds) == "'/data.parquet'"

    def test_parquet_hive_raises_400(self):
        ds = _ds("parquet_hive", "/data", {})
        with pytest.raises(HTTPException) as exc_info:
            resolve_flat_path(ds)
        assert exc_info.value.status_code == 400


# ── load_system ───────────────────────────────────────────────────────────────


class TestLoadSystemFlat:
    """Case 1 & 2: flat parquet (parquet / ducklake), WHERE-based filtering."""

    def test_no_entity_no_time(self, tmp_path):
        """No filters at all — full scan. VT-Atlas-PDP style."""
        path = str(tmp_path / "data.parquet")
        conn = _conn()
        conn.execute(f"""
            COPY (
                SELECT 'apple' AS types, 10 AS counts UNION ALL
                SELECT 'banana',          5            UNION ALL
                SELECT 'cherry',          3
            ) TO '{path}' (FORMAT PARQUET)
        """)
        ds = _ds("parquet", path, {"type": "types-counts"})
        result = load_system(conn, ds, local_id=None, dates=None,
                             filter_vals={}, granularity=None, limit=100)
        assert result["types"] == ["apple", "banana", "cherry"]
        assert result["counts"] == [10.0, 5.0, 3.0]

    def test_entity_filter(self, tmp_path):
        """Entity column filters out rows from other entities."""
        path = str(tmp_path / "data.parquet")
        conn = _conn()
        conn.execute(f"""
            COPY (
                SELECT 'apple' AS types, 10 AS counts, 'US' AS geo UNION ALL
                SELECT 'banana',          5, 'US'                   UNION ALL
                SELECT 'cherry',         20, 'CA'
            ) TO '{path}' (FORMAT PARQUET)
        """)
        ds = _ds("parquet", path, {"type": "types-counts"},
                 entity_mapping={"local_id_column": "geo"})
        result = load_system(conn, ds, local_id="US", dates=None,
                             filter_vals={}, granularity=None, limit=100)
        assert result["types"] == ["apple", "banana"]
        assert "cherry" not in result["types"]

    def test_time_dimension(self, tmp_path):
        """WHERE year BETWEEN ... filters out out-of-range rows. Babynames style."""
        path = str(tmp_path / "data.parquet")
        conn = _conn()
        conn.execute(f"""
            COPY (
                SELECT 'Alice' AS types, 100 AS counts, 'US' AS geo, 2020 AS year UNION ALL
                SELECT 'Bob',             50, 'US', 2020                           UNION ALL
                SELECT 'Carol',          200, 'US', 2019
            ) TO '{path}' (FORMAT PARQUET)
        """)
        ds = _ds("parquet", path,
                 {"type": "types-counts", "time_dimension": "year"},
                 entity_mapping={"local_id_column": "geo"})
        result = load_system(conn, ds, local_id="US", dates=["2020", "2020"],
                             filter_vals={}, granularity=None, limit=100)
        assert result["types"] == ["Alice", "Bob"]
        assert "Carol" not in result["types"]

    def test_filter_dimension(self, tmp_path):
        """Extra categorical filter (sex=F). Babynames filter_dimensions style."""
        path = str(tmp_path / "data.parquet")
        conn = _conn()
        conn.execute(f"""
            COPY (
                SELECT 'Alice' AS types, 100 AS counts, 'US' AS geo, 'F' AS sex UNION ALL
                SELECT 'Bob',             50, 'US', 'M'                          UNION ALL
                SELECT 'Carol',          200, 'US', 'F'
            ) TO '{path}' (FORMAT PARQUET)
        """)
        ds = _ds("parquet", path,
                 {"type": "types-counts", "filter_dimensions": ["sex"]},
                 entity_mapping={"local_id_column": "geo"})
        result = load_system(conn, ds, local_id="US", dates=None,
                             filter_vals={"sex": "F"}, granularity=None, limit=100)
        assert result["types"] == ["Carol", "Alice"]
        assert "Bob" not in result["types"]

    def test_custom_column_names(self, tmp_path):
        """type_column / count_column overrides — legacy ngrams column names."""
        path = str(tmp_path / "data.parquet")
        conn = _conn()
        conn.execute(f"""
            COPY (
                SELECT 'the' AS ngram, 1000 AS pv_count UNION ALL
                SELECT 'cat',           500
            ) TO '{path}' (FORMAT PARQUET)
        """)
        ds = _ds("parquet", path,
                 {"type": "types-counts", "type_column": "ngram", "count_column": "pv_count"})
        result = load_system(conn, ds, local_id=None, dates=None,
                             filter_vals={}, granularity=None, limit=100)
        assert result["types"] == ["the", "cat"]
        assert result["counts"] == [1000.0, 500.0]

    def test_limit(self, tmp_path):
        """LIMIT is respected."""
        path = str(tmp_path / "data.parquet")
        conn = _conn()
        conn.execute(f"""
            COPY (
                SELECT 'a' AS types, 3 AS counts UNION ALL
                SELECT 'b', 2 UNION ALL
                SELECT 'c', 1
            ) TO '{path}' (FORMAT PARQUET)
        """)
        ds = _ds("parquet", path, {"type": "types-counts"})
        result = load_system(conn, ds, local_id=None, dates=None,
                             filter_vals={}, granularity=None, limit=2)
        assert len(result["types"]) == 2
        assert result["types"] == ["a", "b"]

    def test_returns_float_counts(self, tmp_path):
        """counts list contains floats (required by allotax)."""
        path = str(tmp_path / "data.parquet")
        conn = _conn()
        conn.execute(f"""
            COPY (SELECT 'x' AS types, 7 AS counts) TO '{path}' (FORMAT PARQUET)
        """)
        ds = _ds("parquet", path, {"type": "types-counts"})
        result = load_system(conn, ds, local_id=None, dates=None,
                             filter_vals={}, granularity=None, limit=100)
        assert all(isinstance(c, float) for c in result["counts"])


class TestLoadSystemHive:
    """Case 3: parquet_hive — path-based entity + time filtering. Ngrams style."""

    def _write_hive(self, tmp_path, country, date, rows):
        """Create country=X/date=Y/data_0.parquet under tmp_path/data/daily/."""
        part_dir = tmp_path / "data" / "daily" / f"country={country}" / f"date={date}"
        part_dir.mkdir(parents=True, exist_ok=True)
        conn = duckdb.connect()
        vals = " UNION ALL ".join(
            f"SELECT '{t}' AS ngram, {c} AS pv_count" for t, c in rows
        )
        conn.execute(f"COPY ({vals}) TO '{part_dir}/data_0.parquet' (FORMAT PARQUET)")
        conn.close()

    def _ds(self, tmp_path):
        return _ds(
            "parquet_hive",
            str(tmp_path / "data"),
            {
                "type": "types-counts",
                "type_column": "ngram",
                "count_column": "pv_count",
                "granularities": {"daily": "date"},
            },
            entity_mapping={"local_id_column": "country"},
        )

    def test_aggregates_across_dates(self, tmp_path):
        """SUM(pv_count) aggregates across multiple date partitions."""
        self._write_hive(tmp_path, "US", "2024-01-01", [("the", 100), ("cat", 50)])
        self._write_hive(tmp_path, "US", "2024-01-02", [("the", 100), ("cat", 50)])
        # noise: different country, should not appear
        self._write_hive(tmp_path, "CA", "2024-01-01", [("eh", 999)])

        conn = _conn()
        result = load_system(conn, self._ds(tmp_path), local_id="US",
                             dates=["2024-01-01", "2024-01-02"],
                             filter_vals={}, granularity="daily", limit=100)
        assert result["types"] == ["the", "cat"]
        assert result["counts"] == [200.0, 100.0]
        assert "eh" not in result["types"]

    def test_date_range_excludes_outside_dates(self, tmp_path):
        """Dates outside the range are excluded by the WHERE clause."""
        self._write_hive(tmp_path, "US", "2024-01-01", [("inside", 10)])
        self._write_hive(tmp_path, "US", "2024-01-05", [("outside", 99)])

        conn = _conn()
        result = load_system(conn, self._ds(tmp_path), local_id="US",
                             dates=["2024-01-01", "2024-01-03"],
                             filter_vals={}, granularity="daily", limit=100)
        assert result["types"] == ["inside"]
        assert "outside" not in result["types"]

    def test_wildcard_entity(self, tmp_path):
        """local_id=None → glob uses '*', returning all entities."""
        self._write_hive(tmp_path, "US", "2024-01-01", [("the", 10)])
        self._write_hive(tmp_path, "CA", "2024-01-01", [("le",  20)])

        conn = _conn()
        result = load_system(conn, self._ds(tmp_path), local_id=None,
                             dates=["2024-01-01", "2024-01-01"],
                             filter_vals={}, granularity="daily", limit=100)
        assert set(result["types"]) == {"the", "le"}
