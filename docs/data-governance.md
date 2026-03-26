# Data Governance Roadmap

> Design notes toward improving cross-group discoverability and data interoperability
> for the Storywrangler / VCSI data platform.

---

## Context

Storywrangler is not a single company's data platform. It is infrastructure for a
**ragtag collection of academic groups** — each with their own goals, tools, storage,
and timelines. Students come and go. Labs have independent agendas. Collaboration
happens opportunistically, not by mandate.

This shapes every governance decision. Unity Catalog is the right reference point for
best practices, but its assumptions (single org, managed cloud storage, dedicated
platform team) do not hold here. We borrow its ideas selectively.

**The platform does not host data, run pipelines, or guarantee dataset availability.**
Groups own their pipelines and storage. The registry is a discovery layer only.

### Urgency

The window to capture institutional knowledge is narrow. Every cohort that graduates
takes with them the provenance of the datasets they built — which dump, which mapping,
why that partition scheme. The registry is most valuable if populated *before* each
departure, not after.

### Beyond FAIR

Funding agencies now require FAIR-compliant data management plans. This platform
satisfies FAIR, but FAIR is passive — it describes properties a dataset should have,
not mechanisms to enforce them. What we add on top:

- **Enforcement at registration**: canonical identifiers are validated by the SDK, not
  just recommended. A dataset with malformed ORCIDs is rejected before it reaches Silver.
- **Provenance as a first-class field**: `derived_from` and `produced_by` turn the
  methods section of a paper into a machine-readable dependency graph.
- **Succession**: ownership fields and a transfer endpoint mean a dataset can outlive
  the student who built it — something FAIR says nothing about.

Registration here is not a compliance checkbox. It is the citation infrastructure that
lets a dataset survive its author.

---

## Current Architecture

### What the registry does today

The registry is a **metadata catalog** — it stores pointers to data, not data itself.

```
External group (babynames/, wikipedia-parsing/, ...)
  └── owns data on netfiles or their own storage
  └── runs submit.py → POST /admin/registry/register
        └── stores in PostgreSQL: domain, dataset_id, data_location,
            data_format, tables_metadata, entity_mapping, sources, endpoint_schemas

Platform API (FastAPI)
  └── GET /registry/              → list all datasets
  └── GET /registry/{d}/{id}      → metadata for one dataset
  └── GET /registry/{d}/{id}/adapter → query entity_mappings PostgreSQL table (wikimedia still reads parquet)
  └── GET /registry/{d}/{id}/validate-sources → check source URL reachability
```

Data formats supported: `parquet_hive` | `ducklake` | `duckdb`

The `endpoint_schemas` field is the intended catalog-instrument contract — it declares
what query types a registered dataset supports (e.g. `"types-counts"` with
`time_dimension: "date"`, `entity_dimensions: ["country"]`). Instruments should use
this field to determine compatibility at query time rather than hardcoding dataset logic.

### Key design principle (must preserve)

**Platform down → data still accessible.**

Data lives on institutionally-managed storage (netfiles, shared object storage). The
registry is a discovery layer, not a gateway. If the API is unreachable, groups can
still query their data directly via DuckDB + `data_location`. This is non-negotiable
for an academic setting.

### Medallion tiers (implicit, currently untracked)

Industry terminology (Bronze/Silver/Gold) maps to Palmer's ETL framing, which is more
intuitive for academics who don't have a data engineering background:

| Tier   | Palmer (ETL book) | What it is | Currently tracked? |
|--------|-------------------|------------|-------------------|
| Bronze | Raw integration | Raw dumps, external source files | No |
| Silver | Filtered / cleansed / augmented | Standardized, entity-mapped datasets | Yes (registry) |
| Gold   | Business-level aggregates | Task-specific, analysis-ready, ML-ready | No |

The Palmer framing describes *operations* rather than abstract labels, which helps
academic submitters understand which tier their work belongs to.

**Concrete example — wikigrams + MLOps:**

```
Bronze:  Raw Wikipedia enterprise HTML snapshots
           dumps.wikimedia.org → /netfiles/compethicslab/wikimedia/dumps/
           (referenced only as source URLs in the registry, not registered as datasets)

Silver:  wikipedia-parsing transforms Bronze → standardized, entity-mapped outputs
           wikimedia/ngrams     — n-gram frequencies by date/country (daily/weekly/monthly)
           wikimedia/revisions  — article revision histories partitioned by identifier
           babynames/ngrams     — baby name counts by year, location, sex
           (registered in the registry, served via the API)

Gold:    A CS/ML group wants to classify ngrams into topic buckets.
         They consume Silver and produce new artifacts:

           wikimedia/article-embeddings   ← embed article text from revisions
                                            (derived_from: wikimedia/revisions)

           wikimedia/topic-classifier     ← trained model: ngram → topic label
                                            (derived_from: wikimedia/article-embeddings)

           wikimedia/ngram-topics         ← predictions: (ngram, date, country, topic, confidence)
                                            (derived_from: wikimedia/ngrams + wikimedia/topic-classifier)
         (none of these are registered today)
```

Key clarification: the wikigrams pipeline IS the Bronze→Silver transformation.
Silver is what gets registered and served. Gold is everything built on top of Silver,
potentially by a completely different group.

The registry only sees Silver. Bronze sources exist in the `sources` field (URL only).
Gold artifacts have no registry entry and no lineage back to Silver.

---

## What Is Missing (Gap Analysis)

### 1. Lineage

The registry knows where data lives but not where it came from or what depends on it.

Missing:
- `derived_from`: list of `domain/dataset_id` references this dataset was built from
- `produced_by`: pipeline or script that generated this dataset
- `consumers`: opt-in array of known downstream users (stories, tools, partner groups)
  that depend on this dataset. Dataset-to-dataset dependencies are computable by
  inverting `derived_from`; `consumers` covers non-dataset dependents (stories, scripts)
  that would otherwise be invisible. Opt-in keeps it low-friction — the value is
  blast-radius estimation and eventually a change-notification list for partners.

Without lineage, a schema change in `wikimedia/ngrams` has unknown blast radius.

### 2. Ownership and succession

When a student leaves, their dataset registration persists but institutional knowledge
is lost. There is no mechanism for the institute to take custody and hand off to a new
student.

Missing fields on `Dataset`:
- `owner_group`: lab or research group (e.g. `"compethicslab"`, `"VCSI"`)
- `contact`: email or identifier of current maintainer
- `status`: `active` | `needs_successor` | `archived`
- `storage_risk`: durability signal, not an access tier. Values indicate how likely the
  data is to survive without intervention:
  `managed` (platform warehouse — strongest guarantee) |
  `institutional` (netfiles — durable, low risk) |
  `cloud` (medium risk — depends on account/billing) |
  `personal` (high risk — disappears when student leaves)

  `personal` and `cloud` datasets are not API-servable. They are registered anyway
  because knowing a dataset *exists* and is at risk is more useful than not knowing.
  Either value should automatically prompt `status: needs_successor`. Think of it as
  pre-succession registration: declaring the schema and provenance before the data is
  on proper storage, so that migration can happen before the author leaves — not after.

Policy (not technically enforced): datasets intended to be served via the API must have
`storage_risk: institutional` or `storage_risk: managed`.

### 3. Identifier enforcement (data contract gap)

The Storywrangler-Specification defines canonical entity namespaces and the SDK
implements format validators. But the registry accepts any string in
`entity_mapping.entity_id_column` without checking conformance.

Comparison with industry practice:
- **Unity Catalog** (open source and Databricks): does NOT enforce identifier content.
  Knows a column exists and is type STRING; does not validate that it contains a valid
  ORCID. Enforcement is left to dbt tests, data contracts, or convention.
- **dbt tests**: the most common real-world approach — regex tests at build time,
  run by the producer before data lands in Silver. Validates at transformation stage.
- **Data contracts** (emerging): formal YAML spec with per-column format constraints,
  validated by tools like Soda or Great Expectations.

The Storywrangler-Specification IS a data contract. Calling the SDK validators at
`POST /admin/registry/register` would make the platform enforce identifier conformance
at registration time — more rigorous than UC out of the box.

Missing:
- Spec conformance check at registration: call `storywrangler-sdk` validators on
  `entity_mapping.entity_id_column` values (format validation = hard reject;
  existence check against live registries = optional warning)
- Cross-dataset join documentation for submitters

### 4. Catalog-instrument boundary (endpoint_schemas not enforced)

The `endpoint_schemas` field records what query types a dataset supports:

```json
{"type": "types-counts", "time_dimension": "date", "entity_dimensions": ["country"]}
```

This is the intended contract between the catalog and instruments (allotaxonometer,
wordshift, etc.). An instrument should consult a dataset's `endpoint_schemas` and know
whether it can serve that dataset — without hardcoding dataset-specific logic.

In practice, the current `storywrangler.py` allotax endpoint fuses three concerns:
- Catalog lookup (registry `SELECT`)
- Data loading (`_load_ngrams` via DuckDB directly on netfiles)
- Computation (Rust allotax algorithm)

`endpoint_schemas` is populated but not validated or enforced at query time. The
contract exists in the model but is not operationally active. Moving instruments to
`storywrangler-api` (see Project boundaries) is the opportunity to enforce it: an
instrument requesting a dataset whose `endpoint_schemas` does not include the required
type should get a clean error, not a runtime failure deep in data loading.

### 5. Cross-group interoperability

For Group A (e.g. ecology) and Group B (e.g. CS/ML) to collaborate, their datasets
must share a **canonical entity namespace**. Without this, Group B's model predictions
cannot be joined back to Group A's observations even if both are registered.

**This is already solved at the specification level.** The `Storywrangler-Specification`
repo defines the canonical entity namespace for the ecosystem (v0.0.1, Nov 2025):

| Entity type | Primary identifier | Fallback |
|---|---|---|
| People / researchers | `orcid:...` | `wikidata:Q...` |
| Research organizations | `ror:...` | `ipeds:...` → `wikidata:Q...` |
| Published works | `doi:...` | `isbn:...` → `wikidata:Q...` |
| Places, concepts, events | `wikidata:Q...` | — |
| Fields / subjects | `wikidata:Q...`, `arxiv:...`, `mag:...` | `local:corpus:id` |

The `storywrangler` SDK implements format validation and checksum verification for all
of these. Cross-taxonomy mapping (arXiv → Wikidata, MAG → Wikidata) is handled by
Storywrangler internally; adapters are not required to provide it.

The gap is not curation — it is **enforcement at registration time**. The registry
currently accepts any string in `entity_mapping.entity_id_column` without checking
conformance to the specification. Validating against the SDK at `POST /admin/registry/register`
would close this.

### 6. Catalog resilience

If PostgreSQL is down, `GET /registry/` is unreachable. Groups lose discoverability
even though their data is physically accessible. The catalog itself needs a durable
fallback artifact.

Proposed: periodically export the registry to a parquet snapshot at a known path:

```
/netfiles/compethicslab/registry/
  snapshots/date=YYYY-MM-DD/registry.parquet
  latest.parquet
```

Groups can then query the catalog directly:
```python
duckdb.sql("SELECT * FROM read_parquet('/netfiles/compethicslab/registry/latest.parquet')")
```

### 7. Column-level metadata

`data_schema` is `{column: type}` only. No descriptions, no PII/sensitivity flags,
no tags. Limits discoverability for researchers who don't know what `rank` or `cnt`
means in the ngrams schema.

### 8. Gold layer invisibility

Derived datasets and ML artifacts are unregistered. There is no way to know:
- That the `open-academic-analytics` training dataset was derived from OpenAlex Silver data
- Which version of `wikimedia/ngrams` was used to produce a given embedding
- What stories depend on what Gold artifacts

---

## Design Decisions

### Federation, not ingestion

Data stays with the submitter. The platform never copies data. This preserves data
sovereignty, avoids duplication of TB-scale datasets, and keeps the platform lightweight.

The tradeoff: the platform cannot guarantee data freshness or availability. A dataset
registered as `active` may have a stale or unreachable `data_location`.

### Storage format for submitters: no single recommendation

Groups using DuckLake for their own data get schema, file paths, and snapshots for free
from the catalog — `submit.py` for DuckLake datasets (`babynames`) is significantly
simpler than for raw `parquet_hive` datasets (`wikipedia-parsing`), which must manually
scan and compute partition statistics.

However, maintaining a lakehouse requires operational expertise that not all groups have.
DuckLake is a reasonable choice for groups comfortable with it; `parquet_hive` remains
valid for groups that just want to drop files on netfiles. The registry accommodates both.

The goal is not to prescribe format but to ensure the adapter (`submit.py`) produces
accurate metadata regardless of format choice.

Note: DuckLake for the **registry store itself** (the PostgreSQL tables holding dataset
metadata) was considered and rejected — see the "Storage format and schema evolution"
section under Design Decisions.

### Namespace: 2-level today, 3-level eventually

The current registry uses a 2-level namespace: `domain/dataset_id`
(e.g. `wikimedia/ngrams`, `babynames/babynames`).

Unity Catalog open source uses 3 levels: `catalog.schema.table`. The third level
(catalog) answers **who produced/owns this**, not just what it is. This distinction
becomes meaningful the moment two groups produce datasets in the same domain:

```
2-level (today):
  wikimedia/ngrams           ← who made this? unclear
  wikimedia/ngram-topics     ← same domain, different group? unclear

3-level (partially done — catalog field added, babynames/ngrams uses catalog: "vcsi"):
  vcsi.wikimedia.ngrams                ← wikigrams team, Silver
  some-ml-group.wikimedia.ngram-topics ← CS/ML group, Gold derived from above
```

The catalog level also maps naturally to Bronze/Silver/Gold tiers as an alternative:

```
  silver.wikimedia.ngrams
  gold.wikimedia.ngram-topics
```

Changing the primary key from `(domain, dataset_id)` to `(catalog, domain, dataset_id)`
is a breaking schema migration. It should be done before groups outside VCSI start
registering, not after. The current `owner_group` field (P1) is a partial workaround
but does not provide namespace isolation.

**Status:** `catalog` column added to `Dataset` model, defaulting to `"vcsi"`.
`babynames/ngrams` already uses `catalog: "vcsi"` in submit.py. Wikimedia datasets
do not yet. Full enforcement (make it part of the PK) deferred until migration to
storywrangler-api (Phase 1).

### What lives in this repo vs external

The `backend/projects/` directory conflates platform infrastructure with research group
pipelines and should eventually be removed. All datasets — including those currently
produced by `open-academic-analytics` and `data-luminosity` — should be registered via
the registry API, following the same pattern as `babynames/` and `wikipedia-parsing/`.

The backend owns:
- Registry API and model
- FastAPI serving endpoints for frontend stories
- Authentication and admin tooling

External groups own:
- Their pipelines and tooling (Dagster, make, scripts)
- Their data on institutional storage
- Their `submit.py` to register datasets

`open-academic-analytics` was built as a demo of the full stack. It should migrate to
an external repo. Its Silver outputs (coauthor networks, training datasets) should be
registered in the registry; its Gold artifacts (UMAP embeddings) should be registered
with `derived_from` pointing to the Silver inputs.

### External vs. managed hosting

Borrowed from Unity Catalog's managed/external table distinction (itself from Hive/Spark):

| | External (default) | Managed (opt-in) |
|---|---|---|
| Storage | Group's own netfiles path | Platform warehouse path |
| Lifecycle | Group controls | Platform controls |
| `DROP` behavior | Removes registration only; files untouched | Removes registration + files |
| API-down fallback | ✓ DuckDB reads directly | Depends on storage choice (see below) |
| Trigger | Registration via `submit.py` | Succession or explicit group request |

**When managed makes sense:** small or stable datasets (historical babynames, survey snapshots, completed study outputs) where the group cannot guarantee long-term maintenance, or where a student has left and VCSI has taken custody.

**Three ingestion paths for managed datasets:**

1. **Static clone** — copy parquet files to `/netfiles/vcsi/warehouse/{domain}/{dataset_id}/`. No pipeline changes. Right for historical, stable datasets that don't update. Update `data_location` in registry, `storage_risk → managed`.

2. **Pipeline adoption** — clone the source repo, adapt output path to platform warehouse, schedule via cron or Dagster. DuckDB reads files at the new location. Right for active datasets where the pipeline is reproducible and small enough to run on platform infrastructure.

3. **Ingest to PostgreSQL** — for very small, highly-queried datasets. Adapter writes rows directly. `data_format: postgresql`. DuckDB can still query via the PostgreSQL scanner extension, preserving the query model. Right when file overhead is not worth it (< a few GB).

**The VM-vs-netfiles tradeoff for managed storage:**

- **Managed on netfiles** (`/netfiles/vcsi/warehouse/`): preserves the API-down → DuckDB fallback. Researchers can still read directly. Preferred.
- **Managed on VM local storage**: only accessible through the API. The federation guarantee breaks. Acceptable for very small datasets where operational simplicity outweighs the loss of direct access — but this should be an explicit, documented decision per dataset.

**Succession as the natural on-ramp:**

When `status` transitions to `needs_successor`, VCSI can choose to promote the dataset to managed rather than finding a new student owner. The process: assess size and pipeline reproducibility → choose ingestion path → clone/ingest → update `data_location`, `storage_risk: managed`, `owner_group: vcsi` → notify original group → decommission original path after a grace period.

For now, all datasets are expected to be external. Managed hosting is a future capability, relevant primarily for internal VCSI datasets that outlive their student maintainers.

### Project boundaries: storywrangler vs complex-stories

**Decision: complex-stories-dev becomes a pure SvelteKit frontend. The registry and
instruments migrate to `storywrangler/packages/api/`.**

Target layout:

```
storywrangler/
  packages/api/     ← registry + instruments + auth (FastAPI)
  packages/sdk/     ← DatasetCreate, validators, register()
  packages/text/    ← text processing utilities

complex-stories-dev/
  frontend/         ← pure SvelteKit, remote functions → storywrangler-api
  (no separate FastAPI process)
```

Complex-stories becomes a first-party consumer of storywrangler — calling it the same
way any external group would, with no special privileges. The SvelteKit Node server
handles story-specific writes (surveys) via server actions against its own PostgreSQL
instance; it does not need a separate FastAPI process for this.

The two projects serve different audiences:

| Project | Audience | Purpose |
|---|---|---|
| storywrangler-api | Researchers/admins | Register datasets, manage catalog, run instruments |
| complex-stories | General/academic readers | Read-only story platform consuming registered data |

Auth follows from this split:
- **storywrangler-api**: JWT tokens for researchers who register or manage datasets.
  Scopes: `registry:read`, `registry:write`, `admin`.
- **complex-stories**: no auth needed for public stories. The SvelteKit server holds the
  API key as an env var. Story-admin operations (editing `stories.csv`) can use a simple
  env-var API key rather than a full auth system.

`storywrangler/packages/api/` already exists as a standalone FastAPI app (`storywrangler-api`),
encoding this intent. A governance browser UI (browse catalog, view lineage, manage
ownership) could be added to storywrangler later; this is distinct from complex-stories,
which is a narrative platform, not a data management interface.

### Write paths: survey and annotation (out of scope for registry)

The registry model (submit snapshot → register) fits batch/pipeline data. Two types of
story components don't fit this pattern:

**Survey** (dark-data-survey): data collection instrument. Lifecycle:
1. Active collection → project-local DB (SQLite, Turso, or similar)
2. Periodically export snapshot → register as Gold dataset via `submit.py`
3. Complex-stories story reads from registered snapshot (read-only)

The survey project owns the write path. Storywrangler never sees live writes.

**Annotation** (interdisciplinarity): collaborative, iterative, ongoing. Right model:
Label Studio-style — own service, own DB, CRUD while active, export to Silver/Gold at
milestones. Complex-stories consumes the annotation API directly during active work;
on milestone, snapshot is registered.

Both cases converge on the same principle: **live writes stay in the project that owns
the data; the registry only sees snapshots.** Storywrangler-api is not a write endpoint
for collaborative tooling. Annotation-specific auth and CRUD API are out of scope for
this registry design.

### Entity mapping: from parquet file pointer to inline registration

**Decision: eliminate `entity_mapping.path` / `entity_mapping.table` (file pointers);
store entities in the `entity_mappings` PostgreSQL table; submit entities inline in
`register()`.**

#### What the adapter is (and is not)

The entity mapping covers **filter-dimension entities** — things a caller can GROUP BY
or FILTER ON in an instrument query. For `wikimedia/ngrams` that is geographic entities
(countries, language communities). For `babynames/babynames` it is the two territories
where birth records are collected. For `open-academic-analytics` it would be the ~800
UVM faculty ego-authors.

It is NOT the measured values. Person names are the content of babynames, not its
dimensions. Wikipedia article titles are the content of ngrams, not dimensions.
Adapter vocabularies are always bounded by entity type:

| Entity type | Typical count |
|---|---|
| Countries / territories | 11–200 |
| Researchers / ORCID holders in a dataset | hundreds to tens of thousands |
| Topics / fields (controlled vocabulary) | hundreds |
| Wikipedia articles, person names | millions — never an adapter vocabulary |

#### Current state

- `Dataset.entity_mapping` stores `{path, table, local_id_column, entity_id_column}` — a
  file pointer to a parquet file at an absolute path on disk.
- `GET /registry/{domain}/{dataset_id}/adapter` reads that parquet via DuckDB.
- An `EntityMapping` PostgreSQL table already exists (`entity_mappings`, with `domain`,
  `dataset_id`, `local_id`, `entity_id`, `entity_name`, `entity_ids`) but is wired to
  nothing — no endpoint writes to it and no endpoint reads from it.

#### New design

`Dataset.entity_mapping` becomes a schema declaration only:

```json
{"entity_type": "geo_country", "local_id_column": "country"}
```

No file path. No table name. Just what kind of entity and which column holds the
dataset-local identifier.

Entities are submitted inline in `register()`:

```python
register({
    ...,
    "entity_mapping": {
        "entity_type": "geo_country",
        "local_id_column": "country",
        "entities": [
            {"local_id": "united_states", "entity_id": "wikidata:Q30",
             "entity_name": "United States", "entity_ids": ["iso:US"]},
            {"local_id": "quebec", "entity_id": "wikidata:Q176",
             "entity_name": "Quebec", "entity_ids": ["iso:CA-QC"]},
        ]
    }
})
```

The SDK splits this into two API calls:
1. Dataset upsert — `POST /admin/registry/register` (without the `entities` list)
2. Entity batch upsert — `POST /admin/registry/{domain}/{dataset_id}/entities`
   (chunked at ~2000 rows per request for large vocabularies)

The `/adapter` endpoint becomes:

```sql
SELECT * FROM entity_mappings WHERE domain = ? AND dataset_id = ?
```

No DuckDB. No parquet. No path to go stale.

Spec validation happens in the SDK before any network call — malformed `entity_id`
values (bad ORCID format, wrong Wikidata prefix) are rejected locally with a clear
error message before anything reaches the server.

#### Rationale

- **Operational simplicity**: adapter parquet files are separate artifacts to manage,
  version, and keep in sync. A stale path breaks the `/adapter` endpoint silently.
  Inline submission eliminates the file entirely.
- **Infrastructure already exists**: `EntityMapping` is already in the schema, correctly
  indexed. It just needs to be wired up.
- **Single source of truth**: submitters declare everything in `submit.py`. Nothing
  split across code and a separate file on netfiles.
- **Early validation**: the SDK validates entity identifiers against the
  Storywrangler-Specification before the POST. The server is never the first line of
  defense against malformed IDs.

#### Scale

For 149K coauthors (the full `open-academic-analytics` coauthor table): PostgreSQL
handles this trivially with the `(domain, dataset_id, local_id)` index. SDK batches
the upsert in chunks of ~2000. Whether all coauthors belong in the adapter depends on
the instrument use case — if no instrument will filter or cross-join by individual
coauthor, only the ~800 ego-authors need to be registered.

#### Migration note

`entity_mapping.path` and `entity_mapping.table` fields in `DatasetCreate` are
deprecated. Remove them when migrating to storywrangler-api (Phase 1 of the migration
sequence). During the transition, the existing wikimedia adapter.parquet and babynames
adapter data should be submitted as inline entities via a one-time migration script.

---

### Storage format and schema evolution: PostgreSQL + Alembic (not DuckLake)

**Decision: keep the registry in PostgreSQL with Alembic managing schema migrations.**

The registry is a mutable operational store — rows are frequently updated (ownership
transfer, status changes, metadata enrichment). DuckLake's time-travel is cheap because
parquet files are immutable; frequent small updates fight against this model. The registry
is the wrong shape for a lakehouse.

Schema evolution (adding `owner_group`, `contact`, `status`, `derived_from`, etc.) is
straightforward with Alembic — all proposed additions are nullable columns:

```python
def upgrade():
    op.add_column('datasets', sa.Column('owner_group', sa.String))
    op.add_column('datasets', sa.Column('contact', sa.String))
    op.add_column('datasets', sa.Column('status', sa.String))
    op.add_column('datasets', sa.Column('derived_from', postgresql.JSON))
```

Tracked in git, reversible, backward compatible with existing rows. The migration to
storywrangler-api is the right moment to set up Alembic properly (it is configured but
dormant in `backend/`).

The resilience benefit DuckLake would provide (catalog queryable without the API) is
covered by the parquet snapshot export (Gap 6 / P3). Revisit DuckLake only if the
registry needs analytical-scale lineage graph traversal over thousands of datasets.

---

## Proposed Additions (Prioritized)

### P1 — Ownership and succession fields

**Done** — added as `ownership` JSON column to `Dataset` model and `DatasetCreate` SDK schema.
Sub-fields: `owner_group`, `contact`, `status`, `storage_risk`.

Remaining: `PATCH /admin/registry/{domain}/{dataset_id}/transfer` endpoint to change owner
and update status. Enables institute to take custody when a student leaves.

### P2 — Lineage fields

**Done** — added as `lineage` JSON column to `Dataset` model and `DatasetCreate` SDK schema.
Sub-fields: `derived_from`, `produced_by`, `consumers`.

No graph database needed. Simple list of `domain/dataset_id` strings is sufficient to
traverse dependencies for a catalog of this scale.

Dataset-to-dataset downstream lineage is computable by inverting `derived_from` across
the registry (see `GET /registry/{domain}/{dataset_id}/dependents`). `consumers` covers
what that query cannot see: stories, scripts, and partner tools that read a dataset but
never register their own output. It is opt-in and free-form — no validation, just
contact surface for blast-radius assessment and future schema-change notifications.

### P3 — Catalog parquet snapshot export

Scheduled job (or admin endpoint) that exports the registry to a parquet file on
netfiles. Makes the catalog resilient to API downtime and directly queryable with DuckDB.

### P4 — Column descriptions

Extend `data_schema` from `{column: type}` to:

```json
{
  "rank": {"type": "BIGINT", "description": "Frequency rank of the n-gram on this date"},
  "cnt":  {"type": "BIGINT", "description": "Raw occurrence count"},
  "freq": {"type": "DOUBLE", "description": "Normalized frequency (cnt / total tokens)"}
}
```

Low effort, high discoverability value.

### P5 — Gold layer registration

Register derived datasets and ML artifacts using the same registry, with `derived_from`
pointing to their Silver inputs. No separate model registry needed at this scale.

The wikigrams+MLOps case shows three distinct Gold asset types:

| Asset | `data_format` | `derived_from` | Notes |
|---|---|---|---|
| `wikimedia/article-embeddings` | `parquet_hive` | `["wikimedia/revisions"]` | vectors on disk |
| `wikimedia/topic-classifier` | `duckdb` or path | `["wikimedia/article-embeddings"]` | serialized model weights |
| `wikimedia/ngram-topics` | `parquet_hive` | `["wikimedia/ngrams", "wikimedia/topic-classifier"]` | prediction outputs |

The trained model (`topic-classifier`) is just another registered dataset with a
`data_location` pointing to model weights on netfiles. MLflow is not needed at this
scale; the registry is sufficient. If model versioning becomes critical, that is when
to reconsider.

For the cross-group scenario: the CS/ML group registers their Gold outputs with
`derived_from` pointing to the wikigrams Silver datasets. The wikigrams group can
then see who is consuming their data via a downstream lineage query — even if the
two groups never coordinated directly.

---

## Adoption Strategy

### The framing problem

Academic groups don't think in terms of "upstream/downstream consumers," "data products,"
or "SLAs." Framing governance as compliance overhead will be ignored. The right framing
is **attribution infrastructure** — something academics already care about deeply.

| Avoid saying | Say instead |
|---|---|
| Downstream consumers | Future collaborators |
| Data governance | FAIR principles for your dataset |
| Schema stability | Can someone reproduce your results in 5 years? |
| SLA / data contract | Your data surviving your PhD |
| Lineage graph | The citation trail for your dataset |
| Business-level aggregates | Analysis-ready data / what goes in your methods section |

### The adapter as a machine-readable methods section

When you write a methods section you already describe:
1. Where the raw data came from → `sources` (URL + snapshot date + checksum)
2. How you processed it → `produced_by` (git SHA of the code that ran)
3. What derived variables you computed → `derived_from` (which Silver datasets you built on)

Every `submit.py` automates what goes in the methods section. The payoff: a machine can
traverse the full dependency graph and tell you in 2027 exactly which Wikipedia dump a
2024 paper's topic classifications came from. That's reproducibility, not governance.

### The `derived_from` field as a data citation

When a CS/ML group registers Gold outputs with `derived_from: ["wikimedia/ngrams"]`,
the registry records a machine-readable citation. The wikigrams team gains visibility
into who is building on their work — evidence of impact for grant applications — without
the two groups ever needing to coordinate directly.

This is the concrete return on investment for submitters: **registration = being cited**.

### The minimum ask

For a research group, onboarding is:
1. `uv add storywrangler-sdk` (or `pip install storywrangler-sdk`)
2. Write a `submit.py` — typically 50–100 lines; see `babynames/adapter/submit.py` or
   `wikipedia-parsing/adapter/submit.py` as templates
3. Run `python submit.py` once per data update (registration is an upsert — safe to re-run)

The registry never touches the data. Groups keep full control of their pipelines and
storage. The only thing that changes is that the dataset is now discoverable.

### Repo organization

The adapter (`submit.py`) is the boundary, not the repo. A monorepo with clearly
separated Silver and Gold `submit.py` files is equivalent to separate repos from the
registry's perspective.

Heuristic: if you'd write a separate paper, consider a separate repo. The Silver dataset
paper and the Gold analysis paper are different contributions with different authors.

Monorepo structure that preserves the boundary:
```
wikipedia-parsing/
  adapter/submit.py        # registers Silver: wikimedia/ngrams, wikimedia/revisions
  gold/
    embeddings/submit.py   # registers Gold: wikimedia/article-embeddings
    topics/submit.py       # registers Gold: wikimedia/ngram-topics
```

Risk of monorepo: the temptation to add Gold columns directly to Silver tables, making
Silver task-specific and breaking other consumers.

---

## Open Questions

- **Should stories be registered assets?** A story consuming `wikimedia/ngrams` is a
  downstream dependency. Tracking it would complete the lineage picture. But stories
  are frontend code, not data — the boundary is unclear.

- **Storage class enforcement?** Should the platform reject registration of `personal`
  storage, or only warn? Hard enforcement risks friction; soft warning may be ignored.

- **`open-academic-analytics` migration**: move to external repo and register its
  Silver outputs via `submit.py`. Timing TBD.

- **Spec enforcement strictness**: format validation (regex + checksum) should be a hard
  reject at registration. Existence checks (live ORCID registry, Wikidata SPARQL) are
  expensive and should be warnings only. The spec already makes this distinction (MUST
  vs SHOULD).

- **Who governs the registry?** The succession mechanism exists (P1 fields + transfer
  endpoint) but the policy is unresolved: who approves new registrations, who holds
  admin access, who can archive or transfer a dataset when a student leaves without
  handing off? This needs a named role or committee before external groups onboard.

- **PII and data sensitivity?** `storage_risk` covers data durability but not sensitivity.
  Some datasets contain or are derived from identified individuals (survey fingerprints,
  researcher publication records). Does the registry need a `sensitivity` field?
  Who determines classification, and does it gate access to `data_location`?

---

## Migration Strategy

### Principle: parallel, not big-bang

Complex-stories backend stays fully operational until the migration is complete. Each
endpoint moves to storywrangler-api independently; complex-stories remote functions
are updated one at a time. No cutover until everything is verified.

### Sequence

```
Phase 1 — storywrangler-api foundation
  Set up Alembic in storywrangler/packages/api/
  Add P1 ownership fields + P2 lineage fields as nullable columns
  Migrate registry router + Dataset model
  Migrate instrument endpoints (allotax, babynames, wikimedia)

Phase 2 — complex-stories rewire
  Update remote functions to call storywrangler-api
  Keep complex-stories FastAPI running in parallel during this phase
  Verify each story works against storywrangler-api before removing old endpoint

Phase 3 — complex-stories cleanup
  Remove complex-stories FastAPI process
  Survey/annotation endpoints: evaluate per project
    → own micro-service (project-local DB + API), or
    → SvelteKit server actions writing directly to complex-stories PostgreSQL

Phase 4 — external project migrations
  open-academic-analytics → external repo, registers Silver + Gold via submit.py
  dark-data-survey → own project, registers snapshot via submit.py when ready
```

### Network cost of the split

Instrument endpoints (allotax, babynames) return large JSON payloads (up to 10k
ranked items). If storywrangler-api runs on the same VM, the SvelteKit → API hop is
loopback (essentially free). If on a separate VM on the same UVM network, latency adds
~1–2 ms per request — imperceptible, and these endpoints are called only on user action
(mount + explicit "Update" click), not continuously.

### Open operational question

Before starting Phase 1: decide whether storywrangler-api gets its own subdomain
(`api.storywrangler.uvm.edu`) or is proxied through the existing `api.complexstories.uvm.edu`.
Coordinate with IT. This determines the `API_BASE` env var in complex-stories remote
functions and affects external submitters' `submit.py` configs.

---

## TODO

Items are ordered roughly by dependency and impact. Items marked `[design]` need more
discussion before implementation. Items marked `[impl]` are ready to build.

### Registry model changes

- [x] `[impl]` **P1 — Ownership fields**: added as `ownership` JSON column to `Dataset`
  model and `DatasetCreate` schema. Sub-fields: `owner_group`, `contact`, `status`,
  `storage_risk`. Transfer endpoint (`PATCH /admin/registry/.../transfer`) not yet built.
- [x] `[impl]` **P2 — Lineage fields**: added as `lineage` JSON column to `Dataset`
  model and `DatasetCreate` schema. Sub-fields: `derived_from`, `produced_by`, `consumers`.
  Traversal API (`GET /registry/.../dependents`) not yet built.
- [ ] `[impl]` **P4 — Richer `data_schema`**: change from `{col: type}` to
  `{col: {type, description}}` — backward compatible if old format is detected and
  migrated on read
- [x] `[design]` **3-level namespace**: `catalog` column added to `Dataset`, defaulting
  to `"vcsi"`. All registered datasets (babynames/ngrams, wikimedia/ngrams,
  wikimedia/revisions) now populate `catalog: "vcsi"`. Making it part of the composite
  PK is deferred to Phase 1 of the storywrangler-api migration.

### Entity mapping migration

- [x] `[impl]` **Wire `EntityMapping` table to `/adapter` endpoint**: done — registry
  adapter endpoint queries `entity_mappings` PostgreSQL table. Wikimedia domain routers
  still use adapter parquet at query time (separate from the /adapter listing endpoint).
- [x] `[impl]` **Add entity batch upsert endpoint**: done — entities submitted inline
  in `register()`, SDK routes to `POST /admin/registry/{domain}/{dataset_id}/entities`.
- [x] `[impl]` **Update `DatasetCreate` schema**: done — `entities` list accepted
  inline at top level of `register()` payload.
- [x] `[impl]` **Reduce `entity_mapping` JSON field to schema declaration**: done for
  all registered datasets. wikimedia/ngrams uses `{"entity_type": "wikidata",
  "local_id_column": "country"}`; wikimedia/revisions has no `entity_mapping` (articles
  are content, not filter dimensions — article index stored in
  `format_config.tables_metadata["article_index"]`).
- [x] `[impl]` **Migrate existing adapter data**: done — migration script ran for both
  wikimedia/ngrams (11 rows) and babynames/ngrams (2 rows).
- [ ] `[impl]` **SDK spec validation before POST**: call `storywrangler-sdk` format
  validators on each `entity_id` in the entities list before making any network call.
  Hard reject locally on format failure.
- [x] `[impl]` **Migrate wikimedia.py to DB pre-resolution**: done — `/top-ngrams2`
  and `/search-terms2` resolve `entity_id → local_id` via `EntityMapping` DB;
  `/revisions` reads article index from `format_config.tables_metadata["article_index"]`.

### New API endpoints

- [ ] `[impl]` **`PATCH /admin/registry/{domain}/{dataset_id}/transfer`**: change
  `owner_group`, `contact`, `status`. Succession workflow for departing students.
- [ ] `[impl]` **`GET /registry/{domain}/{dataset_id}/dependents`**: list all datasets
  that declare `derived_from` containing this dataset. Enables impact analysis before
  schema changes.
- [ ] `[impl]` **`GET /admin/registry/export`**: dump full registry to parquet and
  write to `/netfiles/compethicslab/registry/snapshots/date=.../registry.parquet` +
  update `latest.parquet` symlink. Can be triggered manually or on a schedule.

### Identifier enforcement

- [ ] `[impl]` **Spec validation at registration**: at `POST /admin/registry/register`,
  if `entity_mapping` is present, call `storywrangler-sdk` format validators on a
  sample of `entity_id` values. Hard reject on format failure; warn on existence check
  failure.

### Adapter updates (external, not this repo)

- [ ] `[design]` **Enrich `sources` field**: add `snapshot_date` and `checksum` to
  source entries in `submit.py` adapters. Closes the Bronze provenance gap.
- [ ] `[design]` **`produced_by` convention**: settle on a format (git SHA, script
  path, Dagster asset key) and document it so all adapters use it consistently.
- [ ] `[design]` **Gold registration pattern**: document how a Gold `submit.py` should
  look, including snapshot references in `derived_from`. Use wikigrams embeddings as the
  worked example.
- [ ] `[design]` **Dimension catalog for wikimedia/revisions**: the `/adapter` endpoint
  covers filter-dimension entities (countries, locations — bounded vocabularies). But
  `wikimedia/revisions` article titles / page identifiers are the content dimensions
  themselves (millions of items — never an adapter vocabulary). Frontend selectors that
  let users pick an article need a separate, searchable catalog endpoint (e.g.
  `GET /wikimedia/revisions/articles?q=...`). Decide: is this a new endpoint type in
  `endpoint_schemas`, a search-index sidecar, or something else? Distinct from entity
  mapping; the entity here is the article, not a geographic or researcher entity.

### Structural / organizational

- [ ] `[design]` **Managed hosting ingestion process**: define the formal process for
  promoting a dataset from external to managed — criteria (size, stability, succession
  trigger), ingestion path (static clone vs pipeline adoption vs PostgreSQL ingest),
  storage location (netfiles warehouse vs VM), grace period before decommissioning
  original path, and group notification workflow.
- [ ] `[design]` **`backend/projects/` exit plan**: decide timeline for migrating
  `open-academic-analytics` to an external repo. Register its Silver outputs and Gold
  artifacts via the registry.
- [ ] `[design]` **Stories as registered assets?**: decide whether frontend stories
  should be registered as downstream dependencies. Simplest form: a `consumers` field
  on `Dataset` listing story slugs that use it.

### Legacy cleanup (pre-migration)

- [ ] `[impl]` **Remove `datalakes.py` router**: all routes are `deprecated=True` and
  the router is broken (accesses `datalake.tables_metadata` which is no longer a mapped
  model column). Safe to remove once confirmed no client is calling these endpoints.
  After removal, drop the legacy flat DB columns (`tables_metadata`, `partitioning`,
  `ducklake_data_path`, `data_schema`) from the `datasets` table via Alembic.
- [x] `[impl]` **Migrate `wikimedia.py` to DB pre-resolution** (see Entity mapping section).

### Migration to storywrangler-api

- [ ] `[design]` **Subdomain decision**: `api.storywrangler.uvm.edu` vs proxy through
  `api.complexstories.uvm.edu`. Coordinate with IT before Phase 1.
- [ ] `[impl]` **Alembic setup**: initialize `alembic/` in `storywrangler/packages/api/`,
  write initial migration capturing current `datasets` + `entity_mappings` schema.
- [ ] `[impl]` **Migrate registry router + model**: move `backend/app/routers/registry.py`
  and `backend/app/models/registry.py` to `storywrangler/packages/api/`.
- [ ] `[impl]` **Migrate instrument endpoints**: move `storywrangler.py` (allotax),
  `babynames.py`, `wikimedia.py` routers to `storywrangler/packages/api/routers/`.
- [ ] `[impl]` **Update complex-stories remote functions**: point to storywrangler-api.
  Keep complex-stories backend running in parallel until all remote functions verified.
- [ ] `[design]` **Survey/annotation write paths**: evaluate `dark_data_survey.py` and
  `annotations.py` — migrate to own project or convert to SvelteKit server actions.
- [ ] `[impl]` **Remove complex-stories FastAPI process**: once all remote functions
  point to storywrangler-api and survey/annotation paths are resolved.
