"""
Tests for datalakes API endpoints and helper functions.
"""

import pytest
from datetime import datetime, timedelta
from ..routers.datalakes import parse_partition_values, find_overlapping_partitions


class TestPartitionHelpers:
    """Test helper functions for partition parsing and filtering."""

    def test_parse_partition_values_weekly(self):
        """Test parsing week partition values from Hive-style paths."""
        file_paths = [
            "geo=United States/week=2025-03-03/data_0.parquet",
            "geo=United States/week=2025-03-10/data_0.parquet",
            "geo=Canada/week=2025-03-03/data_0.parquet",
            "geo=Canada/week=2025-03-10/data_0.parquet",
        ]

        result = parse_partition_values(file_paths, "week")

        assert result == ["2025-03-03", "2025-03-10"]
        assert len(result) == 2  # Should deduplicate

    def test_parse_partition_values_monthly(self):
        """Test parsing month partition values."""
        file_paths = [
            "geo=United States/month=2025-01-01/data_0.parquet",
            "geo=United States/month=2025-02-01/data_0.parquet",
            "geo=United States/month=2025-03-01/data_0.parquet",
        ]

        result = parse_partition_values(file_paths, "month")

        assert result == ["2025-01-01", "2025-02-01", "2025-03-01"]

    def test_parse_partition_values_daily(self):
        """Test parsing date partition values."""
        file_paths = [
            "geo=United States/date=2025-03-05/data_0.parquet",
            "geo=United States/date=2025-03-06/data_0.parquet",
        ]

        result = parse_partition_values(file_paths, "date")

        assert result == ["2025-03-05", "2025-03-06"]

    def test_parse_partition_values_empty(self):
        """Test with no matching partitions."""
        file_paths = ["geo=United States/data_0.parquet"]

        result = parse_partition_values(file_paths, "week")

        assert result == []

    def test_find_overlapping_partitions_daily(self):
        """Test finding overlapping daily partitions."""
        available = ["2025-03-05", "2025-03-06", "2025-03-07", "2025-03-10"]

        result = find_overlapping_partitions(
            "2025-03-05", "2025-03-07", available, "daily"
        )

        assert result == ["2025-03-05", "2025-03-06", "2025-03-07"]
        assert "2025-03-10" not in result

    def test_find_overlapping_partitions_weekly_exact_match(self):
        """Test weekly partitions with exact week boundary match."""
        # Week starts on Monday 2025-03-03, ends Sunday 2025-03-09
        available = ["2025-03-03", "2025-03-10", "2025-03-17"]

        # User requests data from Wed to next Wed (spans 2 weeks)
        result = find_overlapping_partitions(
            "2025-03-05", "2025-03-12", available, "weekly"
        )

        assert result == ["2025-03-03", "2025-03-10"]

    def test_find_overlapping_partitions_weekly_partial(self):
        """Test weekly partitions with partial week overlap."""
        available = ["2025-03-03", "2025-03-10", "2025-03-17"]

        # User requests just 2 days within first week
        result = find_overlapping_partitions(
            "2025-03-05", "2025-03-06", available, "weekly"
        )

        # Should still include the week since it overlaps
        assert result == ["2025-03-03"]

    def test_find_overlapping_partitions_monthly(self):
        """Test monthly partitions."""
        available = ["2025-01-01", "2025-02-01", "2025-03-01"]

        # Request spans February
        result = find_overlapping_partitions(
            "2025-02-10", "2025-02-20", available, "monthly"
        )

        assert result == ["2025-02-01"]

    def test_find_overlapping_partitions_monthly_span_multiple(self):
        """Test monthly partitions spanning multiple months."""
        available = ["2025-01-01", "2025-02-01", "2025-03-01"]

        # Request spans Jan 15 to Mar 15 (3 months)
        result = find_overlapping_partitions(
            "2025-01-15", "2025-03-15", available, "monthly"
        )

        assert result == ["2025-01-01", "2025-02-01", "2025-03-01"]

    def test_find_overlapping_partitions_no_overlap(self):
        """Test when no partitions overlap with date range."""
        available = ["2025-01-01", "2025-02-01"]

        result = find_overlapping_partitions(
            "2025-03-10", "2025-03-20", available, "monthly"
        )

        assert result == []

    def test_find_overlapping_partitions_december_boundary(self):
        """Test monthly partition calculation across year boundary."""
        available = ["2024-12-01", "2025-01-01"]

        # Request spans December
        result = find_overlapping_partitions(
            "2024-12-15", "2024-12-25", available, "monthly"
        )

        assert result == ["2024-12-01"]
        assert "2025-01-01" not in result


# FastAPI endpoint tests would go here
# These require TestClient and mocked database/duckdb connections
# Example structure:
#
# from fastapi.testclient import TestClient
# from ..main import app
#
# client = TestClient(app)
#
# class TestWikigramsEndpoint:
#     def test_wikigrams_daily_granularity(self):
#         """Test querying with daily granularity."""
#         response = client.get(
#             "/wikigrams/top-ngrams",
#             params={
#                 "dates": "2025-03-05,2025-03-06",
#                 "granularity": "daily",
#                 "locations": "wikidata:Q30"
#             }
#         )
#         assert response.status_code == 200
#         data = response.json()
#         assert "metadata" in data
#         assert data["metadata"]["granularity"] == "daily"
