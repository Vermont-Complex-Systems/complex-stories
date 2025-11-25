# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "marimo>=0.17.0",
#     "pyzmq",
# ]
# ///

import marimo

__generated_with = "0.18.0"
app = marimo.App()


@app.cell
def _():
    import marimo as mo
    import altair as alt
    return alt, mo


@app.cell
def _(mo):
    _df = mo.sql(
        f"""
        INSTALL ducklake;
        ATTACH 'ducklake:postgres:dbname=complex_stories host=localhost user=jstonge1' AS scisciDB 
            (DATA_PATH '/netfiles/compethicslab/scisciDB/');
        """
    )
    return


@app.cell
def _(mo):
    _df = mo.sql(
        f"""
        SHOW ALL TABLES;
        """
    )
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## Lets look at `s2_papers`

    This is a big table
    """)
    return


@app.cell
def _(mo):
    _df = mo.sql(
        f"""
        SELECT ROUND(SUM(file_size_bytes) / 1e9, 2) as file_size_gigabytes
        FROM __ducklake_metadata_scisciDB.ducklake_data_file 
        WHERE table_id = 2;
        """
    )
    return


@app.cell
def _(mo):
    mo.md(r"""
    If we count the total number of papers:
    """)
    return


@app.cell
def _(mo):
    _df = mo.sql(
        f"""
        SELECT COUNT(*) as total_papers FROM scisciDB.s2_papers;
        """
    )
    return


@app.cell
def _(mo):
    mo.md(r"""
    We can describe it using `DESCRIBE`
    """)
    return


@app.cell
def _(mo):
    _df = mo.sql(
        f"""
        DESCRIBE SELECT * FROM scisciDB.s2_papers;
        """
    )
    return


@app.cell
def _(mo):
    _df = mo.sql(
        f"""
        SELECT * FROM scisciDB.s2_papers LIMIT 5;
        """
    )
    return


@app.cell
def _(mo):
    mo.md(r"""
    Now, say that we want to count number of papers by year
    """)
    return


@app.cell
def _(mo):
    _df = mo.sql(
        f"""
        SELECT 
            COUNT(*) as n, year 
            FROM scisciDB.s2_papers 
            WHERE 
                year IS NOT NULL AND year > 1900
            GROUP BY year;
        """
    )
    return


@app.cell
def _(alt, mo):
    count_df = mo.sql("""
    SELECT 
        COUNT(*) as n, year 
        FROM scisciDB.s2_papers 
        WHERE 
            year IS NOT NULL AND year > 1900
        GROUP BY year;
    """)

    alt.Chart(count_df).mark_bar().encode(
        x=alt.X('year:O', 
                axis=alt.Axis(labelAngle=-45, 
                             values=list(count_df['year'][::5]))),  # Show every 5th year
        y=alt.Y('n:Q', title='Count'),
        tooltip=['year:O', 'n:Q']
    ).properties(
        width=700,
        height=200
    ).configure_axis(
        grid=True,
        gridOpacity=0.3
    )
    return


@app.cell
def _(mo):
    mo.md(r"""
    Huzzay. I cannot overemphasize enough how it used to be more messy than that to do this count.

    How many of those have parsed text? Here we use symlog because there are years for which $n=0$
    """)
    return


@app.cell
def _(alt, mo):
    fulltext_df = mo.sql("""
    SELECT 
        year,
        COUNT(*) as total_papers,
        COUNT(*) FILTER (WHERE has_fulltext) as papers_with_fulltext,
        COUNT(*) FILTER (WHERE NOT has_fulltext) as papers_without_fulltext
    FROM scisciDB.s2_papers 
    WHERE year IS NOT NULL AND year > 1900
    GROUP BY year
    ORDER BY year;
    """).to_pandas()  

    # Create base chart
    base = alt.Chart(fulltext_df).encode(
        x=alt.X('year:Q',
                axis=alt.Axis(labelAngle=-45, values=list(fulltext_df['year'][::5])),
                title='Year')
    )

    # Bottom bar (total) - orange
    bottom = base.mark_bar(color='orange', opacity=0.8).encode(
        y=alt.Y('total_papers:Q',
                scale=alt.Scale(type='symlog'),
                title='Number of Papers'),
        tooltip=['year', 'total_papers']
    )

    # Top bar (with fulltext) - blue
    top = base.mark_bar(color='steelblue', opacity=0.8).encode(
        y=alt.Y('papers_with_fulltext:Q',
                scale=alt.Scale(type='symlog')),
        tooltip=['year', 'papers_with_fulltext']
    )

    (bottom + top).properties(
        width=800,
        height=300,
        title='Full Text Availability by Year'
    ).configure_axis(
        grid=True,
        gridOpacity=0.3
    )
    return


@app.cell
def _(mo):
    mo.md(r"""
    Duckdb is also nice because we can easly examine what's happening under the hood
    (we did need to do a little hack to see it nicely formated in html):
    """)
    return


@app.cell
def _(mo):
    plan = mo.sql("""
    EXPLAIN ANALYZE
    SELECT 
        year,
        COUNT(*) as total_papers,
        COUNT(*) FILTER (WHERE has_fulltext) as papers_with_fulltext,
        COUNT(*) FILTER (WHERE NOT has_fulltext) as papers_without_fulltext
    FROM scisciDB.s2_papers 
    WHERE year IS NOT NULL AND year > 1900
    GROUP BY year
    ORDER BY year;
    """).to_pandas()

    mo.Html(f"""
    <div style="
        font-family: 'Courier New', monospace; 
        font-size: 12px; 
        white-space: pre-wrap;
        word-wrap: break-word;
        max-width: 600px;
        max-height: 600px; 
        overflow-x: auto; 
        overflow-y: auto; 
    ">
    {plan.iloc[0,1]}
    </div>
    """)

    return


@app.cell
def _(mo):
    _df = mo.sql(
        f"""

        """
    )
    return


if __name__ == "__main__":
    app.run()
