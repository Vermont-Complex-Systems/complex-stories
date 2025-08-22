import numpy as np
import dagster as dg
from dagster import MaterializeResult, MetadataValue
from dagster_duckdb import DuckDBResource
import umap


@dg.asset(
    deps=["embeddings"],
    description="🌐 Apply UMAP dimensionality reduction to embeddings from DuckDB",
)
def umap_embeddings(duckdb: DuckDBResource):
    """Apply UMAP dimensionality reduction to all embeddings using DuckDB."""

    with duckdb.get_connection() as conn:

        embeddings_df = conn.execute(
            """
            SELECT doi, abstract, fieldsOfStudy, s2FieldsOfStudy, embedding
            FROM oa.raw.embeddings
            WHERE status = 'success' AND embedding IS NOT NULL
        """
        ).df()

        embeddings_matrix = np.vstack(embeddings_df["embedding"].values)

        umap_model = umap.UMAP(
            n_components=2,
            n_neighbors=15,
            min_dist=0.1,
            metric="euclidean",
            random_state=42,
        )

        print("🧮 Fitting UMAP model...")
        umap_result = umap_model.fit_transform(embeddings_matrix)

        # Create results DataFrame (copy without embeddings to save space)
        results_df = embeddings_df.drop("embedding", axis=1).copy()

        # Add UMAP coordinates
        results_df[f"umap_1"] = umap_result[:, 0]
        results_df[f"umap_2"] = umap_result[:, 1]

        # Save results
        conn.execute(
            """
            CREATE OR REPLACE TABLE oa.transform.umap_embeddings AS 
            SELECT * FROM results_df
        """
        )

    return MaterializeResult(
        metadata={
            "input_source": MetadataValue.text("DuckDB oa.raw.embeddings table"),
            "total_embeddings": MetadataValue.int(len(results_df))
        }
    )
