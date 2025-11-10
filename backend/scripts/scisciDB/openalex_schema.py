works_columns = {
    # --- Scalar fields ---
    "id": "VARCHAR",
    "doi": "VARCHAR",
    "title": "VARCHAR",
    "display_name": "VARCHAR",
    "publication_year": "INTEGER",
    "publication_date": "DATE",
    "created_date": "TIMESTAMP",
    "updated_date": "TIMESTAMP",
    "language": "VARCHAR",
    "type": "VARCHAR",
    "type_crossref": "VARCHAR",
    "is_retracted": "BOOLEAN",
    "is_paratext": "BOOLEAN",
    "has_fulltext": "BOOLEAN",
    "fulltext_origin": "VARCHAR",
    "license": "VARCHAR",
    "fwci": "DOUBLE",
    "cited_by_count": "INTEGER",
    "countries_distinct_count": "INTEGER",
    "institutions_distinct_count": "INTEGER",
    "locations_count": "INTEGER",

    # --- Arrays of simple values ---
    "corresponding_author_ids": "VARCHAR[]",
    "corresponding_institution_ids": "VARCHAR[]",
    "referenced_works": "VARCHAR[]",
    "related_works": "VARCHAR[]",

    # --- Structured objects ---
    "biblio": "STRUCT(volume VARCHAR, issue VARCHAR, first_page VARCHAR, last_page VARCHAR)",
    "apc_list": "STRUCT(value DOUBLE, currency VARCHAR, provenance VARCHAR, value_usd DOUBLE)",
    "apc_paid": "STRUCT(value DOUBLE, currency VARCHAR, provenance VARCHAR, value_usd DOUBLE)",
    "citation_normalized_percentile": "STRUCT(value DOUBLE, is_in_top_1_percent BOOLEAN, is_in_top_10_percent BOOLEAN)",
    "counts_by_year": "STRUCT(year INTEGER, cited_by_count INTEGER)[]",

    # --- Nested complex arrays ---
    "authorships": "STRUCT(author_position VARCHAR, author STRUCT(id VARCHAR, display_name VARCHAR, orcid VARCHAR), institutions STRUCT(id VARCHAR, display_name VARCHAR, country_code VARCHAR, ror VARCHAR)[], is_corresponding BOOLEAN)[]",

    "concepts": "STRUCT(id VARCHAR, wikidata VARCHAR, display_name VARCHAR, level INTEGER, score DOUBLE)[]",

    "topics": "STRUCT(id VARCHAR, display_name VARCHAR, subfield STRUCT(id VARCHAR, display_name VARCHAR), field STRUCT(id VARCHAR, display_name VARCHAR), domain STRUCT(id VARCHAR, display_name VARCHAR))[]",

    "keywords": "STRUCT(keyword VARCHAR, score DOUBLE)[]",

    "mesh": "STRUCT(descriptor_ui VARCHAR, descriptor_name VARCHAR, qualifier_ui VARCHAR, qualifier_name VARCHAR, is_major_topic BOOLEAN)[]",

    "grants": "STRUCT(funder VARCHAR, funder_display_name VARCHAR, award_id VARCHAR)[]",

    "sustainable_development_goals": "STRUCT(id VARCHAR, display_name VARCHAR, score DOUBLE)[]",

    "locations": "STRUCT(is_oa BOOLEAN, landing_page_url VARCHAR, pdf_url VARCHAR, source STRUCT(id VARCHAR, display_name VARCHAR, issn_l VARCHAR, is_oa BOOLEAN, type VARCHAR))[]",

    # --- Other JSON objects (simpler) ---
    "primary_location": "STRUCT(id VARCHAR, display_name VARCHAR, landing_page_url VARCHAR, pdf_url VARCHAR)",
    "best_oa_location": "STRUCT(id VARCHAR, display_name VARCHAR, landing_page_url VARCHAR, pdf_url VARCHAR)",
    "open_access": "STRUCT(is_oa BOOLEAN, oa_status VARCHAR, oa_url VARCHAR)",

    # --- Text-heavy ---
    "abstract_inverted_index": "VARCHAR"
}

sources_columns = {
    # --- Scalar fields ---
    "id": "VARCHAR",
    "display_name": "VARCHAR",
    "abbreviated_title": "VARCHAR",
    "apc_usd": "INTEGER",
    "cited_by_count": "INTEGER",
    "country_code": "VARCHAR",
    "created_date": "TIMESTAMP",
    "updated_date": "TIMESTAMP",
    "homepage_url": "VARCHAR",
    "host_organization": "VARCHAR",
    "host_organization_name": "VARCHAR",
    "is_core": "BOOLEAN",
    "is_in_doaj": "BOOLEAN",
    "is_oa": "BOOLEAN",
    "issn_l": "VARCHAR",
    "type": "VARCHAR",
    "works_api_url": "VARCHAR",
    "works_count": "INTEGER",

    # --- Arrays of simple values ---
    "alternate_titles": "VARCHAR[]",
    "host_organization_lineage": "VARCHAR[]",
    "issn": "VARCHAR[]",

    # --- Structured objects ---
    "apc_prices": "STRUCT(price INTEGER, currency VARCHAR)[]",
    "counts_by_year": "STRUCT(year INTEGER, works_count INTEGER, cited_by_count INTEGER)[]",
    "ids": "STRUCT(fatcat VARCHAR, issn VARCHAR[], issn_l VARCHAR, mag INTEGER, openalex VARCHAR, wikidata VARCHAR)",
    "societies": "STRUCT(url VARCHAR, organization VARCHAR)[]",
    "summary_stats": "STRUCT(2yr_mean_citedness DOUBLE, h_index INTEGER, i10_index INTEGER)",
    "x_concepts": "STRUCT(id VARCHAR, wikidata VARCHAR, display_name VARCHAR, level INTEGER, score DOUBLE)[]"
}

