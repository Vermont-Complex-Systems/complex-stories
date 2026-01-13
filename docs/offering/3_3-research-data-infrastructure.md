# Section 3.3: Research Data Infrastructure

## The Knowledge Evaporation Problem

Bob, the ecology PhD student from Section 3.1, discovered Jacques' complementary work through the lab website. Excited to collaborate, Jacques sends Bob his human activity data: a 15GB MongoDB export with nested JSON, inconsistent field names (`location` vs `coordinates`), mixed timestamp formats (Unix epochs, ISO strings, "2023-03" without day precision).

Bob spends two weeks writing parsing code, aligning it with Sam's bird migration CSV. He discovers that Sam's cryptic column `loc_type_3` means "migration stopover site" only by reading through 500 lines of analysis code. The spatial join is complicated by different coordinate systems.

Bob gets it working. The combined analysis reveals exciting patterns about how human activity affects migration routes.

Then Alice mentions the state wildlife database—30 years of historical migration records, just became available. Bob realizes he's about to repeat the entire process: download yet another dataset in a new format, reverse-engineer schema, write custom joining logic, hope coordinate systems align. And when the next student joins, they'll reconstruct all three datasets from scratch.

**The pattern is universal:** Research teams build fragmented, isolated data infrastructure that doesn't survive personnel turnover. Student A builds a scraping pipeline storing data in custom CSV format. Student B can't figure out A's schema, rebuilds everything differently. Student C needs both datasets, gives up, starts from scratch.

## Why Groups Don't Solve This Themselves

Building centralized research data infrastructure requires: database design, API development, authentication systems, data pipeline orchestration, schema versioning, access control logic, and documentation practices. Done properly: 120-200 hours of specialized work.

**The alternative:** Let every student handle data their own way. Each builds scripts, stores locally, shares via Dropbox or email. Total coordination overhead and rebuilding across students over 3-5 years: 200-400 hours collectively. But it's distributed invisibly across individuals, so no one recognizes the cumulative cost.

Research incentive structures don't reward infrastructure work. A PhD student who spends three months building proper data infrastructure has delayed publications. The next cohort benefits, but the infrastructure builder doesn't get credit.

**The honest reality about when infrastructure is worth it:**

**You probably don't need this if:**
- Single researcher working independently
- One or two datasets, analysis completed within months
- No ongoing data collection or collaboration
- No plans to build on this work long-term

**You probably do need this if:**
- Multiple students/postdocs working on related projects
- Data collection spans multiple years
- Datasets need to be joined or compared
- External collaborators need access
- You're tired of answering "where's the data?" questions
- Next cohort should build on (not rebuild) current work

## Our Solution: Two-Tier Approach

We build centralized data systems for research teams—storage, pipelines, APIs, and access controls designed to persist beyond individual researchers. The key distinction is **complexity of workflows**.

### Tier 1: Basic Data Infrastructure ($6,400-9,600)

**Best for:** Research groups with multiple students working on related data, needing centralized access but without complex automation requirements

**What's included:**
- PostgreSQL database designed for your data types
- Documented schemas with data dictionaries (no more `loc_type_3` mysteries)
- Basic API endpoints for common queries (authenticated, role-based permissions)
- Data import scripts from common sources (Zotero, survey platforms, sensors)
- Version control and migration strategy
- First year hosting included (~$250-500)
- Timeline: 4-6 weeks

**Pricing:** $6,400-9,600 (40-60 hours @ $160/hr effective rate)

**What this enables:**
- Multiple team members query same data source (no "where's the latest version?")
- Consistent structure (new students don't rebuild schemas)
- Access control built in (undergrads see public data, postdocs see everything)
- Other applications can build on this (websites pull from same database—see Section 3.1)

**Example use cases:**
- Lab collecting survey data or experimental results over multiple years
- Team needing to join datasets from different sources
- Research group transitioning from individual scripts to shared systems
- Projects requiring basic data sharing with collaborators

**Workflow:**
1. Discovery meeting: Understand data types, existing formats, team structure
2. Schema design: Collaborate on standardized structure
3. Implementation: Set up PostgreSQL, create API endpoints
4. Team training: How to query, add data, maintain system
5. Documentation: Data dictionaries, API docs, maintenance guides
6. Deployment: Set up hosting, monitor initial usage

**You provide:** Description of data types, existing files/formats, team structure, access requirements

### Tier 2: Integrated Data Platform ($17,250-27,360)

**Best for:** Complex projects requiring automated pipelines, multiple data sources, MLOps workflows, or sophisticated orchestration

**What's included (everything from Tier 1, PLUS):**
- Automated data orchestration (Dagster pipelines)
- Multiple integrated sources (APIs, scrapers, sensors, surveys)
- MLOps workflows (model predictions → human review → refinement)
- Complex access control (project-based, time-based, attribute-based permissions)
- Data transformation pipelines (cleaning, aggregation, feature engineering)
- Multiple frontend applications (dashboards, exploratory tools)
- Monitoring and alerting (pipeline failures, data quality issues)

**Pricing:** $17,250-27,360 (6-8 weeks structured as initial sprint + iteration)

**Ongoing maintenance:** $2,273/month (20% FTE) or train team to maintain

**Timeline:** 8-12 weeks iterative development

**Example: Course Catalogs Research Platform**

A multi-year study analyzing faculty hiring patterns across higher education institutions demonstrates integrated infrastructure at scale.

**The challenge:** Data locked in inconsistent PDF course catalogs across hundreds of institutions. Extracting structured information requires scraping, parsing, and standardization—then making it queryable for multiple researchers.

**Architecture:**

**Upstream data production:**
- Dagster pipelines scrape PDFs from institutional websites
- LLM-augmented extraction converts PDFs to structured JSON
- Through iteration, team agreed on shared data schema
- PostgreSQL database stores standardized output with documented fields

**MLOps layer:**
- Models extract faculty hiring dates from catalogs (challenging due to variable institutional conventions)
- Feedback loop: model predictions → human review → pipeline refinement → improved extraction
- Dagster orchestrates this workflow (data ingestion, model runs, quality checks)
- Performance monitoring catches degradation early

**Downstream consumption:**
- New PhD student queries structured data through documented API
- Doesn't need to understand scraping or extraction—just uses clean data
- Can focus on analysis rather than data engineering

**Frontend component:**
- Dashboard for exploring hiring patterns (see Section 3.2 for exploratory dashboards)
- Connects to same API backend that researchers query

**The integrated approach enables collaboration:**
- Data engineer maintains scraping infrastructure
- ML researcher improves extraction models
- Domain expert (faculty hiring) validates output and poses questions
- Data analyst queries results
- RSE builds visualization interfaces

Each contributes their strength. Infrastructure coordinates their work.

**Best for:**
- Research centers with multiple ongoing projects
- Multi-year studies with evolving requirements
- Projects requiring sophisticated workflows (scraping → ML → validation loops)
- Groups building long-term computational capacity
- Multi-institutional studies with federated data access

## Technical Architecture: Progressive Enhancement

Our infrastructure follows progressive enhancement philosophy—ensuring research survives funding uncertainty.

**Layer 1 (always survives):**
- PostgreSQL database with documented schema
- Standard SQL queries work even if everything else fails
- Data exports to CSV/JSON always available
- **Requires:** Basic database knowledge (findable at any university)

**Layer 2 (survives moderate disruption):**
- API endpoints for programmatic access
- Basic authentication and permissions
- **Requires:** Web development knowledge (moderately common)

**Layer 3 (requires active maintenance):**
- Dagster orchestration for complex workflows
- MLOps pipelines and model monitoring
- Advanced features and integrations
- **Requires:** Ongoing RSE support or sophisticated in-house expertise

**Guarantee:** If our office closes, you lose Layer 3, may lose Layer 2, but always keep Layer 1. Your data remains in accessible formats with documentation. Contrast with commercial cloud solutions where vendor closure creates data hostage situations.

## Data Governance & Compliance

Both tiers support sensitive research data with appropriate controls:

**Access control options:**
- Role-based (faculty, postdocs, grad students, undergrads)
- Project-based (researchers see only their projects)
- Time-limited (collaborators access during grant period)
- Attribute-based (complex rules like "faculty in ecology department")

**Compliance support:**
- IRB protocol implementation
- Data sharing plan execution (required by NSF, NIH)
- Audit logging (track who accessed what, when)
- Data retention policies
- FERPA/HIPAA consultation (we help, but you need institutional approval)

**Privacy protections:**
- De-identification workflows
- Aggregate-only API endpoints (no individual-level data exposed)
- Differential privacy techniques for statistical releases
- Data minimization (expose only necessary fields)

**Example:** Course catalogs platform implements role-based access where admin users can edit all data, annotators can edit research group entries, and faculty can only edit entries matching their name.

## APIs as Bridges Between Research Platforms

Our goal isn't centralizing all university research data into one monolithic system. It's building infrastructure that can communicate across boundaries.

**Current reality:** Every lab maintains isolated data. Collaboration requires manual exports, email chains, and stale CSVs. No one knows what data exists outside their immediate group.

**The vision:** Multiple research groups each have their own data platforms (Alice's ecology lab, Brian's climate modeling group, Chen's urban planning center). Each uses different tools, stores different data types. But all expose APIs using common standards.

**What this enables:**
- When Bob needs climate data for migration study, he queries Brian's API programmatically
- When Chen studies urban bird populations, she queries Alice's bird database directly
- No manual coordination, no outdated exports, no duplication
- Discovery happens through API catalogs (what datasets exist, how to access them)

**For now:** We start with de-siloing within single research groups. But API-first design means when you're ready to connect externally—to collaborators, to institutional repositories, to public data archives—the infrastructure supports it.

**This is why we emphasize standards:** PostgreSQL, REST APIs, OpenAPI documentation, authentication patterns that work across systems. We're building bridges, not walled gardens.

## Pricing Summary

**Basic Data Infrastructure:** $6,400-9,600 (40-60 hours)
- PostgreSQL database with documented schemas
- Basic API endpoints
- Simple data import/export
- Timeline: 4-6 weeks

**Integrated Data Platform:** $17,250-27,360 (6-8 weeks)
- Automated pipelines (Dagster)
- Multiple data sources
- MLOps workflows
- Complex access controls
- Timeline: 8-12 weeks

**Ongoing maintenance options:**
- Self-maintain: We train your team, provide documentation
- Consulting retainer: $150/month (10% FTE) for technical updates
- Ongoing partnership: $2,273/month (20% FTE) for continuous development

> [!NOTE] **📦 INTEGRATION WITH RESEARCH WEBSITES (SECTION 3.1)**
> Data infrastructure becomes more valuable when connected to research websites:
> - Team pages display "Sam maintains Bird Database - [API docs] [access instructions]"
> - Onboarding documentation links directly to data access endpoints
> - New students discover both research AND data infrastructure through one interface
> - Publications auto-update from centralized database
>
> First project: 40-60 hours. Adding website integration: 20-30 additional hours because infrastructure exists.

> [!NOTE] **📦 ENABLING EXPLORATORY DASHBOARDS (SECTION 3.2)**
> Exploratory dashboards are most efficient when built on top of existing research data infrastructure:
> - Query centralized databases directly (no data duplication)
> - Reuse API endpoints and access controls
> - Inherit data quality and documentation
> - Leverage existing authentication systems
>
> If you're building data infrastructure (Section 3.3), adding an exploratory dashboard is incremental work—the hard part (backend) already exists.

## When to Choose Which Tier

**Choose Tier 1 (Basic Infrastructure) if:**
- You have multiple researchers needing access to shared data
- Current approach is fragmented (CSVs, Dropbox, email)
- Datasets need standardization and documentation
- You need basic access controls (who can see what)
- Budget supports foundational infrastructure ($6,400-9,600)
- Timeline allows 4-6 weeks development

**Choose Tier 2 (Integrated Platform) if:**
- You need automated data pipelines (scraping, API ingestion)
- Working with multiple heterogeneous data sources
- Require MLOps workflows (model training → validation → refinement)
- Data transformations are complex and need orchestration
- Building long-term computational capacity for research center
- Budget supports comprehensive platform ($17,250-27,360)
- Timeline allows 8-12 weeks iterative development

**Not sure?** Start with Tier 1. Many groups discover they need Tier 2 capabilities after experiencing the value of shared infrastructure. Upgrading is possible—we design for extensibility.

## Growth Path: From Scripts to Platform

Many research groups follow this progression:

**Stage 1: Individual Scripts**
Each student manages their own data → **Coordination problems emerge**

**Stage 2: Basic Infrastructure (Tier 1)**
Centralized database with documented schemas → **$6,400-9,600**

**Stage 3: Add Automated Pipelines**
Upgrade to Dagster orchestration for complex workflows → **Additional $10,850-17,760**

**Stage 4: Connect Visual Essays/Dashboards (Section 3.2)**
Public-facing interfaces to research data → **$3,200-9,600 per interface** (incremental because backend exists)

**Stage 5: Integrate with Research Website (Section 3.1)**
Display datasets from centralized catalog → **$3,200-4,800** (reuses existing infrastructure)

**The value:** Each stage builds on previous work. Infrastructure compounds. When you've built Tier 2 data infrastructure, adding exploratory dashboards or visual essays is straightforward—the hard part already exists.

## What This Solves (and What It Doesn't)

**What shared data infrastructure solves:**
✅ Knowledge evaporation when students graduate
✅ Every student rebuilding pipelines from scratch
✅ "Where's the data?" and "How do I access it?" questions
✅ Incompatible schemas preventing collaboration
✅ Undocumented transformations and lost provenance
✅ Data sitting on laptops or in email attachments
✅ New collaborators facing weeks of reverse-engineering

**What this doesn't solve:**
❌ **Data collection infrastructure:** If you need to annotate thousands of items or collect labeled data—that requires specialized tools → **Section 3.4 (Team Annotations)**
❌ **Public communication:** Once research is complete, sharing findings beyond academic papers → **Section 3.2 (Visual Data Essays)**
❌ **Motivation problems:** Infrastructure doesn't force people to document or follow standards (but it makes good practices easier)
❌ **Institutional incentive structures:** We can't change what counts for tenure

**Think of data infrastructure as the backbone.** It makes collaboration possible, reproducibility feasible, and institutional memory achievable. But research still requires domain expertise, careful methodology, and motivated teams.

## When to Invest in Infrastructure

**Signs you're ready:**
- Same "where's the data?" questions asked repeatedly
- Students spending more time on data wrangling than research
- Collaboration attempts failing due to incompatible formats
- Third time rebuilding similar infrastructure from scratch
- Worried about what happens when current students graduate
- External collaborators requesting data access
- IRB or funding agency requiring data sharing plans

**Signs you can wait:**
- Single researcher, near-term project
- Data collection nearly complete
- No collaboration plans
- Simple analysis, limited data reuse

**Contact us for honest assessment.** Sometimes the answer is "you're not ready yet" or "simpler solutions exist." We'd rather have sustainable long-term relationships than oversell infrastructure you don't need.

---

**Next:** Section 3.4 (Team Annotations) addresses a specialized but common need—collecting labeled data at scale with proper infrastructure, quality control, and team coordination.
