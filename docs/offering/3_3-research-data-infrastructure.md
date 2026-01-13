# Section 3.2: Research Data Infrastructure

## The Problem: Fragmented Infrastructure and Knowledge Evaporation

Research teams build fragmented, isolated data infrastructure that doesn't survive personnel turnover. Student A builds a scraping pipeline storing data in custom CSV format. Student B can't figure out A's schema, rebuilds everything differently. Student C needs both datasets, gives up, starts from scratch. When Student A graduates, their undocumented pipeline breaks, data sits in idiosyncratic formats, and privacy considerations that were afterthoughts become institutional liability.

**The consequence is cumulative inefficiency:**
- Every student rebuilds infrastructure independently (40-80 hours wasted per person)
- Research groups can't build on each other's work (no shared schemas or access patterns)
- Basic questions remain unanswered: "Can we share this data?" "How do we give collaborators access?" "Where did this number come from?"
- Institutional knowledge leaves when people graduate
- Publications claim "data available upon request" but requests reveal unusable, undocumented files

**This isn't just technical debt—it's scientific reproducibility failure.** Research groups need internal infrastructure that persists beyond individual researchers and enables cumulative progress.

## A Concrete Example: Bob's Growing Collaboration

Bob, the ecology PhD student from Section 3.1, discovered Jacques' complementary work through the lab website. Excited to collaborate, Jacques sends Bob his human activity data: a 15GB MongoDB export with nested JSON, inconsistent field names (`location` vs `coordinates`), mixed timestamp formats (Unix epochs, ISO strings, "2023-03" without day precision).

Bob spends two weeks writing parsing code, aligning it with Sam's bird migration CSV. He discovers that Sam's cryptic column `loc_type_3` means "migration stopover site" only by reading through 500 lines of analysis code. The spatial join is complicated by different coordinate systems.

Bob gets it working. The combined analysis reveals exciting patterns about how human activity affects migration routes.

Then Alice mentions the state wildlife database—30 years of historical migration records, just became available. Bob realizes he's about to repeat the entire process: download yet another dataset in a new format, reverse-engineer schema, write custom joining logic, hope coordinate systems align. And when the next student joins, they'll reconstruct all three datasets from scratch.

**The pattern is universal.** When Bob started with one dataset, shared infrastructure would have seemed like over-engineering. But six months in, with three datasets and active collaboration, the fragmented approach collapses under its own weight. Research groups don't know they need infrastructure until they're drowning in data silos—by then, retrofitting is expensive.

## Why Groups Don't Solve This Themselves

Building centralized research data infrastructure requires: database design, API development, authentication systems, data pipeline orchestration, schema versioning, access control logic, and documentation practices. Done properly: 120-200 hours of specialized work.

**The alternative:** Let every student handle data their own way. Each builds scripts, stores locally, shares via Dropbox or email. Total coordination overhead and rebuilding across students over 3-5 years: 200-400 hours collectively. But it's distributed invisibly across individuals, so no one recognizes the cumulative cost.

**Research incentive structures don't reward infrastructure work.** A PhD student who spends three months building proper data infrastructure has delayed publications. The next cohort benefits, but the infrastructure builder doesn't get credit.

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

**And even if you don't need it yet, anticipating future growth makes the upfront investment worthwhile.** Groups consistently report: "We wish we'd built shared infrastructure from the start."

## Our Solution: Practical, Right-Sized Research Data Infrastructure

We establish shared data systems for research teams—storage, pipelines, APIs, and access controls designed to persist beyond individual researchers.

**Our approach:**
- Start simple, add complexity only when justified
- Standardized schemas (everyone understands data structure)
- API layer for programmatic access (consistent queries, built-in permissions)
- Automated pipelines when needed (reproducible transformations, documented decisions)
- Progressive enhancement (core functionality survives even if advanced features break)
- Documentation and handoff plans (next cohort can maintain and extend)

**The stack we use—PostgreSQL, Dagster, SvelteKit—isn't ideological.** It's what we've found strikes a good balance between capability and accessibility in academic contexts. PostgreSQL is robust, well-supported, survives for decades. Dagster provides pipeline orchestration when needed without excessive overhead. SvelteKit builds frontends efficiently. All are open-source with strong communities.

## Example: Course Catalogs Research Project

A multi-year study analyzing faculty hiring patterns across higher education institutions demonstrates integrated infrastructure at scale.

**The challenge:** Data locked in inconsistent PDF course catalogs across hundreds of institutions. Extracting structured information requires scraping, parsing, and standardization—then making it queryable for multiple researchers with different questions.

**Upstream data production:**
- Scraping pipeline collects PDFs from institutional websites
- LLM-augmented extraction converts PDFs to structured JSON
- Through iteration, team agreed on shared data schema
- PostgreSQL database stores standardized output with documented fields

**MLOps layer:**
- Models extract faculty hiring dates from catalogs (challenging due to variable institutional conventions)
- Feedback loop: model predictions → human review → pipeline refinement → improved extraction
- Dagster orchestrates this workflow (data ingestion, model runs, quality checks)
- Performance monitoring catches degradation early

**Downstream consumption:**
- New PhD student queries structured data to answer specific research questions
- Doesn't need to understand scraping or extraction—just uses clean API
- Can focus on analysis rather than data engineering

**Frontend component:**
- Dashboard for exploring hiring patterns
- Updated by RSE as research questions evolve
- Connects to same API backend that researchers query

**The integrated approach enables multiple researchers with different expertise to collaborate efficiently:**
- Data engineer maintains scraping infrastructure
- ML researcher improves extraction models
- Domain expert (faculty hiring) validates output and poses questions
- Data analyst queries results
- RSE builds visualization interfaces

**Each contributes their strength. Infrastructure coordinates their work.** Without shared systems, these roles would duplicate effort or fail to connect.

## What We Build

**Basic Infrastructure (simpler projects):**

Centralized storage with standardized schemas and basic access patterns.

**Components:**
- PostgreSQL database designed for your data types (publications, survey responses, experimental results, etc.)
- Documented schemas with data dictionaries (no more `loc_type_3` mysteries)
- Basic API endpoints for common queries (authenticated, role-based permissions)
- Data import scripts from common sources (Zotero, survey platforms, sensors)
- Version control and migration strategy

**What this enables:**
- Multiple team members query same data source (no "where's the latest version?")
- Consistent structure (new students don't rebuild schemas)
- Access control built in (undergrads see public data, postdocs see everything)
- Other applications can build on this (websites pull from same database—see Section 3.1)

**Process:** Discovery (understand data and workflows) → Schema design → Implementation → Team training → Documentation

**You provide:** Description of data types, existing files/formats, team structure, access requirements

**Pricing:** $6,400-9,600 (40-60 hours)  
**Includes:** Schema design, database setup, basic API, documentation, first year hosting (~$250-500)  
**Timeline:** 4-6 weeks

**Best for:**
- Labs with multiple students on related projects
- Groups collecting data over multiple years
- Teams asking "where's the data?" and "how do I access it?" repeatedly
- Projects transitioning from individual scripts to shared systems

**Integrated Platform (complex projects):**

Comprehensive infrastructure with automated pipelines, multiple data sources, sophisticated access controls.

**Additional capabilities:**
- Automated data orchestration (Dagster pipelines)
- Multiple integrated sources (APIs, scrapers, sensors, surveys)
- MLOps workflows (model predictions → human review → refinement)
- Complex access control (project-based, time-based, attribute-based permissions)
- Data transformation pipelines (cleaning, aggregation, feature engineering)
- Multiple frontend applications (dashboards, exploratory tools, public websites)
- Monitoring and alerting (pipeline failures, data quality issues)

**Example applications:**
- Course catalogs platform (described above)
- Multi-institutional studies with federated data access
- Long-running observational studies with continuous data collection
- Research centers coordinating multiple PIs and projects

**Pricing:** $17,250-27,360 (6-8 weeks effort, structured as retainer)  
**Ongoing maintenance:** $2,273/month (20% FTE) or train team to maintain  
**Timeline:** 8-12 weeks iterative development

**Best for:**
- Research centers with multiple ongoing projects
- Multi-year studies with evolving requirements
- Projects requiring sophisticated workflows
- Groups building long-term computational capacity

> [!NOTE] **📦 APIs AS BRIDGES BETWEEN RESEARCH PLATFORMS**
> Our goal isn't centralizing all university research data into one monolithic system. It's building infrastructure that can communicate across boundaries.
> 
> **Current reality:** Every lab maintains isolated data. Collaboration requires manual exports, email chains, and stale CSVs. No one knows what data exists outside their immediate group.
> 
> **The vision:** Multiple research groups each have their own data platforms (Alice's ecology lab, Brian's climate modeling group, Chen's urban planning center). Each uses different tools, stores different data types. But all expose APIs using common standards.
> 
> **What this enables:**
> - When Bob needs climate data for migration study, he queries Brian's API programmatically
> - When Chen studies urban bird populations, she queries Alice's bird database directly
> - No manual coordination, no outdated exports, no duplication
> - Discovery happens through API catalogs (what datasets exist, how to access them)
> 
> **Long-term potential:** Federation of research data platforms where LLMs can read API documentation, suggest relevant datasets, help write queries. Researchers discover and access data across institutional boundaries.
> 
> **For now:** We start with de-siloing within single research groups. But API-first design means when you're ready to connect externally—to collaborators, to institutional repositories, to public data archives—the infrastructure supports it.
> 
> **This is why we emphasize standards:** PostgreSQL, REST APIs, OpenAPI documentation, authentication patterns that work across systems. We're building bridges, not walled gardens.

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
❌ **Data collection infrastructure:** If Bob needs to annotate thousands of bird behaviors, or Jacques needs human activity labeled—that requires specialized tools → **Section 3.3 (Team Annotations)**  
❌ **Public communication:** Once research is complete, sharing findings beyond academic papers → **Section 3.4 (Visual Data Essays)**  
❌ **Motivation problems:** Infrastructure doesn't force people to document or follow standards (but it makes good practices easier)  
❌ **Institutional incentive structures:** We can't change what counts for tenure

**Think of data infrastructure as the backbone.** It makes collaboration possible, reproducibility feasible, and institutional memory achievable. But research still requires domain expertise, careful methodology, and motivated teams.

## Progressive Enhancement and Long-Term Sustainability

**Our infrastructure follows progressive enhancement philosophy:**

**Layer 1 (always survives):**
- PostgreSQL database with documented schema
- Standard SQL queries work even if everything else fails
- Data exports to CSV/JSON always available
- Requires only basic database knowledge (findable at any university)

**Layer 2 (survives moderate disruption):**
- API endpoints for programmatic access
- Basic authentication and permissions
- Requires web development knowledge (moderately common)

**Layer 3 (requires active maintenance):**
- Dagster orchestration for complex workflows
- MLOps pipelines and model monitoring
- Advanced features and integrations
- Requires ongoing RSE support or sophisticated in-house expertise

**Guarantee:** If our office closes, you lose Layer 3, may lose Layer 2, but always keep Layer 1. Your data remains in accessible formats with documentation. Contrast with commercial cloud solutions where vendor closure creates data hostage situations.

**Maintenance options after initial build:**
- **Self-maintain:** We train your team, provide documentation, available for consulting
- **Consulting retainer:** $150/month (10% FTE) for technical updates, you handle content
- **Ongoing partnership:** 20% FTE ($2,273/month) for continuous development

## Current Capacity

**Available capacity (next 18 months):**
- Basic infrastructure: Can build 3-4 new systems annually
- Integrated platforms: Can build 1 major platform annually OR maintain 2-3 existing systems

**Early adoption:** We have budget to subsidize 1-2 pilot projects at reduced cost for research groups willing to provide feedback and serve as case studies.

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

**Next:** Section 3.3 (Team Annotations) addresses a specialized but common need—collecting labeled data at scale with proper infrastructure, quality control, and team coordination.