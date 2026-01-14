# Section 2: The Two-Mode Solution

## 2.1 Building digital infrastructure at VERSO

Research Software Engineers (RSEs) sit at the intersection of domain science and professional software development. We possess the technical capabilities to architect production-grade infrastructure while understanding the unique constraints and workflows of academic research. More importantly, we serve as **institutional memory**—preventing the knowledge evaporation that occurs when PhD students graduate and their hard-won computational expertise leaves with them.

We recognize that robust computational infrastructure demands dedicated professional roles with specialized expertise in data architecture, software engineering, and computational systems. It is not all or nothing. This knowledge can be transmitted in more effective ways by training researchers to become better programmers. As reearchers to balance research with computational skills, RSEs can play a multifacetted role to consolidate group and institutional knowledge about when and how adopting best software practices.

The Open Source Programming Office at the Vermont Complex Systems Center represents an experiment in making RSE support accessible to research groups across UVM. Rather than expecting each group to independently solve computational infrastructure challenges, we provide two complementary modes of support.

## 2.2 What We've Already Built

We've been busy building and refining this infrastructure for a few years. Current projects include:

**Visual Data Essays (Complex Stories platform)**
Publication-quality interactive storytelling for academic research. Mobile-first, static generation for performance (<1s load times), progressive enhancement for longevity. Stories reach audiences beyond academic papers—policymakers, families, concerned public—while maintaining scientific rigor.

**Custom Research Websites (data-driven, auto-updating)**
SvelteKit sites pulling from OpenAlex/ORCID APIs. Publications, topics, and team profiles update automatically from authoritative sources. Solves the discovery problem: new students find relevant datasets and collaborators through search rather than relying on PI's memory of who's working on what.

**Annotation Infrastructure (13 active users)**
Self-hosted Label Studio serving 4 research groups, plus a custom mobile-first annotator enabling work during "dead time" (commutes, waiting rooms). Built in 1 week using SvelteKit + FastAPI + PostgreSQL, now reused across multiple projects with minimal customization.

**Research Data Infrastructure (course catalogs platform, in collaboration with the Computational Ethics lab)**
Multi-year study processing PDFs from hundreds of institutions. Integrated pipeline: scraping → LLM-assisted extraction → PostgreSQL → FastAPI → dashboards. Enables collaboration between data engineers, ML researchers, and domain experts without coordination overhead. Researchers query clean data through documented APIs rather than reverse-engineering scrapers.

These aren't demonstrations—they're production systems supporting active research.

## 2.3 Our Two-Mode Approach

We reduce the infrastructure burden on research groups through two complementary strategies:

### Mode 1: Reusable Infrastructure Platforms
**The Problem:** Every research group independently builds annotation systems, hosting pipelines, and visualization tools. This collective reinvention wastes hundreds of person-hours annually across UVM while producing fragile, poorly-maintained infrastructure.

**Our Solution:** Build and maintain shared infrastructure that serves multiple research groups. One well-architected, professionally-maintained annotation platform serving 13 researchers is more efficient and reliable than 13 independently-built ad-hoc solutions.

**Examples:**
- Self-hosted Label Studio instance 
- Standardized data processing pipelines with documented best practices
- Reusable web hosting infrastructure for research outputs

**Value Proposition:** Near-zero marginal cost for new users once infrastructure exists. Groups gain access to production-quality tools without building or maintaining them.

### Mode 2: Custom Development with Knowledge Transfer
**The Problem:** Some research needs are genuinely unique—existing tools don't fit the workflow, data has special requirements, or the project demands novel capabilities. These require purpose-built solutions.

**Our Solution:** We architect custom infrastructure tailored to specific research workflows, but we design for sustainability and knowledge transfer. Custom solutions are built with:
- Modular, well-documented code following industry best practices
- Progressive enhancement architecture (graceful degradation if funding ends)
- Training and documentation enabling motivated students to maintain infrastructure
- Open-source licensing preventing vendor lock-in

**Examples:**
- Custom annotation applications for domain-specific needs
- Preprocessing pipelines for complex data extraction (PDF parsing, reranking, entity extraction)
- Interactive data exploration platforms with novel visualization requirements

**Value Proposition:** Purpose-built infrastructure that solves your exact problem, with explicit plans for long-term sustainability and knowledge transfer.

## 2.4 Progressive Enhancement: Infrastructure That Survives

A critical insight from years of building computational infrastructure: **academic funding is inherently unstable**. Grants end. Students graduate. Priorities shift. Infrastructure that requires continuous specialized support becomes abandoned technical debt.

Our design philosophy addresses this reality through **progressive enhancement**—layering infrastructure so that failures degrade gracefully rather than catastrophically.

### The Three-Layer Model

**Layer 1: Core Data (Always Survives)**
- Open-source databases (PostgreSQL, DuckDB) with documented schemas  
- Plain SQL queries work even if everything else breaks
- Raw data exports always available
- **Requires:** Basic database knowledge (findable at any university)
- **Survives:** Funding cuts, personnel turnover, technology obsolescence

**Layer 2: Enhancement (Survives Moderate Disruption)**
- Web interfaces for data entry, viewing, and basic analysis
- User authentication and access control
- Standard visualization and export functions
- **Requires:** Web development knowledge (moderately common)
- **Survives:** Loss of RSE support with moderate technical capacity in the research group

**Layer 3: Advanced Features (Requires Active RSE Support)**
- Active learning pipelines
- LLM-assisted workflows
- Real-time analytics and custom integrations
- Novel computational approaches
- **Requires:** Ongoing RSE partnership or highly sophisticated in-house expertise
- **At Risk:** When specialized RSE support ends

### The Guarantee to Research Groups

When you invest in our infrastructure:

**If VERSO closes or funding ends:**
- You **lose** Layer 3 features (advanced analytics requiring specialized maintenance)
- You **keep** Layer 2 (functional web applications with source code, documentation, and architecture diagrams)
- You **always have** Layer 1 (your data in accessible, open-source formats with clear schema documentation)

**Compare to commercial cloud alternatives:**
- Vendor closes → export process may be painful, incomplete, or expensive
- Pricing changes → forced migration or locked-in costs with no alternatives
- Feature deprecation → workflows break with no recourse
- Data portability → often technically possible but practically difficult

**This is why self-hosted, open-source infrastructure is a strategic investment, not merely an operational cost.** You're building institutional capacity that survives individual funding cycles.

## 2.5 Service Tier Framework

Our offerings are organized into three tiers, each serving different research needs:

### Tier 1: Shared Infrastructure Access
**What it is:** Access to pre-configured platforms we maintain institutionally

**Current offerings:**
- Self-hosted Label Studio annotation platform
- Research data hosting infrastructure
- Standard preprocessing and analysis pipelines

**Pricing Example - Label Studio Access:**
- Setup: $500 one-time
- Annual access: $200/year per research group
- Includes: Platform maintenance, security updates, basic technical support

**Characteristics:**
- **Setup time:** 1-4 hours (primarily onboarding)
- **Maintenance:** Covered by institutional investment (security patches, platform upgrades)
- **Customization:** Limited—you adapt to the platform
- **Best for:** Standard research workflows, groups starting computational work

**Trade-off:** Less flexibility, but near-zero marginal cost and guaranteed professional maintenance

### Tier 2: Custom Implementation with Knowledge Transfer
**What it is:** Purpose-built solutions designed for sustainability and eventual independence

**Deliverables:**
- Custom preprocessing pipelines or lightweight applications
- Complete documentation and architecture diagrams
- Training materials and knowledge transfer sessions
- Initial maintenance period (typically 6 months)
- Optional: Training for motivated students on the codebase

**Pricing Examples:**
- **Custom research website:** $6,400-8,000 (40-50 hours @ $160/hr effective rate including fringe)
  - Includes: 5-10 pages, data-driven components, responsive design, first year hosting
  - Timeline: 4-6 weeks
- **Visual data essay:** $3,200-4,800 (20-30 hours)
  - Includes: Scrollytelling, custom visualizations, mobile-first design, first year hosting
  - Timeline: 3-4 weeks with existing infrastructure, 2-3 months for first collaboration
- **Custom annotation platform:** $6,400-13,600 (40-85 hours)
  - Includes: Domain-specific workflows, mobile-first UI, 6 months maintenance
  - Timeline: 2-4 weeks development + knowledge transfer
- **Basic data infrastructure:** $6,400-9,600 (40-60 hours)
  - Includes: PostgreSQL setup, API endpoints, documentation, first year hosting
  - Timeline: 4-6 weeks

**After initial 6 months, choose:**
- Ongoing maintenance retainer: $250/month
- Consulting retainer (for self-maintaining groups): $150/month (10% FTE)
- Sunset project (infrastructure remains accessible, code is yours)

**Characteristics:**
- **Maintenance:** Initially us, with transition pathway to self-maintenance or ongoing support contract
- **Customization:** High—built specifically for your workflow
- **Best for:** Groups with specific needs AND capacity to potentially self-maintain

**Trade-off:** Higher upfront investment, but you gain custom infrastructure with multiple support pathways

### Tier 3: Long-term Partnership
**What it is:** Embedded RSE support for building computational capabilities over time

**Not just project delivery—this is strategic computational infrastructure development:**
- Iterative improvement and experimentation
- Student training integrated throughout
- Co-investment in long-term computational maturity
- Continuous adaptation as research questions evolve

**Pricing:**
- **Initial sprint:** $11,366 (1 month full-time, includes fringe benefits)
- **Ongoing engagement:** $2,273/month (20% FTE)
- **Minimum duration:** 12 months
- **Complex integrated platform:** $17,250-27,360 for initial 6-8 week build, then monthly retainer

**Characteristics:**
- **Customization:** Continuous—infrastructure evolves with your research
- **Best for:** Well-funded groups making long-term commitment to computational research
- **Examples:** Multi-institutional studies, research centers coordinating multiple PIs, long-running observational studies

**Trade-off:** Expensive but transforms computational capacity of the research group

## 2.6 The Triage Question: Which Tier Do You Need?

**Use Tier 1 if:**
- Your needs fit existing platforms (standard annotation, hosting, analysis)
- You want minimal setup time and guaranteed maintenance
- Budget constraints favor low ongoing costs
- Your workflow can adapt to established patterns

**Use Tier 2 if:**
- Existing tools don't fit your workflow
- You have specific preprocessing or integration requirements  
- You value custom infrastructure but want sustainability options
- You might have capacity to self-maintain with initial training
- You need mobile-first, novel UI/UX, or specialized features

**Use Tier 3 if:**
- You're building computational research as a core long-term capability
- Your research questions continuously evolve
- You want to train students in computational best practices
- You have multi-year funding and commitment to computational infrastructure
- You need "garden cultivation"—continuous improvement and experimentation

**Not sure?** Start with Tier 1. Many groups discover their needs through using shared infrastructure, then graduate to Tier 2 or 3 when they encounter limitations or see additional opportunities.

## 2.8 Current Status & Growth Plan

### Where We Are
Six months into a 2-year Vermont Complex Systems Center initiative. We've validated the technical model (4 deployed production systems, 13 active users across multiple research groups) and are now scaling the customer base toward financial sustainability.

**What we've delivered:**
- Label Studio infrastructure serving 4 research groups
- Custom annotation platform (interdisciplinarity project, now reused)
- Course catalogs data infrastructure (multi-year, multi-institutional study)
- Visual data essays platform (Complex Stories)
- Custom research websites with auto-updating publications

**Demonstrated capabilities:**
- 13 active annotation users across 4 research groups (Label Studio + custom platform)
- Mobile-first annotation interface enabling work during commutes and downtime
- Multi-year course catalogs dataset with documented API access for new researchers
- Visual data essays reaching broader audiences beyond academic papers

### Path to Sustainability

**Our goal:** $100-135k annual revenue by Month 18, demonstrating the model can support permanent RSE capacity at UVM.

**How we get there:**
- Expand from 4 to 10-12 research groups using our infrastructure
- Mix of Tier 1 (shared platforms), Tier 2 (custom projects), and Tier 3 (partnerships)
- Early adopters benefit from subsidized rates while we build portfolio
- Refine offerings based on real customer feedback

**If successful:** UVM gains permanent RSE capacity—rare at universities our size—with compounding institutional infrastructure, reduced vendor lock-in, and knowledge transfer across research groups.

### Your Investment is Protected

**Progressive enhancement guarantee:** Even if our office doesn't secure permanent funding, your infrastructure survives:
- **Layer 1 (always):** Data in PostgreSQL with documented schemas, accessible via standard SQL
- **Layer 2 (likely):** Functional web applications with source code, architecture docs, deployment guides
- **Layer 3 (at risk):** Advanced features requiring ongoing RSE expertise

**All code is open source. All data in standard formats. All documentation complete.**

Compare to commercial alternatives: vendor closes → expensive migration, feature deprecation → broken workflows, pricing changes → locked-in costs.

### Early Adopter Benefits

For the next 6-12 months, we're offering:
- **Subsidized pilot projects** (50% discount on select Tier 2 projects)
- **Priority access** to RSE services while capacity is available
- **Influence over offerings** (your feedback shapes what we build next)
- **Flexible pricing** as we refine the model

**Why early adoption makes sense:**
- Get production-quality infrastructure at discounted rates
- Shape services to fit your actual needs
- Build relationship before capacity fills
- Progressive enhancement protects your investment

### Capacity Constraints: Radical Transparency

**As a single-RSE office, I cannot serve unlimited demand.** Current realistic capacity:

- **Tier 1 (Shared Infrastructure):** Can scale to 20-30 concurrent users ✅
- **Tier 2 (Custom Development):** 3-4 new projects annually 📊  
- **Tier 3 (Long-term Partnerships):** 2-3 concurrent partnerships maximum ⚠️

**When demand exceeds capacity, we prioritize projects that:**
- Serve multiple research groups (infrastructure with high reuse potential)
- Build institutional capacity (strong knowledge transfer components)
- Strategic importance to Vermont Complex Systems Center's research priorities
- Potential to generate sustainable revenue supporting the office

**If we approach capacity limits:**
- Waitlist for new projects
- Price adjustments to match supply and demand
- Evidence-based case for hiring additional RSEs (~$200k annual revenue supports 2 FTE)

## 2.9 Why This Model Matters

Traditional approaches to computational research support at universities:

**Central IT approach:** Generic infrastructure that doesn't understand research workflows. Can host a server but can't help design an annotation scheme or preprocess domain-specific data.

**Commercial cloud approach:** Convenient initially but creates vendor lock-in, recurring costs without building internal capacity, no knowledge transfer, and data portability risks.

**Every-group-for-themselves approach:** Massive redundancy (every lab rebuilds annotation systems, scraping pipelines, dashboards), fragile infrastructure (breaks when students graduate), and knowledge evaporation (next cohort starts from zero).

**Our approach:** Professional infrastructure development with institutional memory, open-source design, and progressive sustainability models. We're building capacity that compounds over time rather than repeatedly solving the same problems.

**The compounding value:**
- Infrastructure built for one project can be adapted and reused
- Component libraries make subsequent projects faster (custom annotator built once, reused across multiple groups with minimal customization)
- Institutional knowledge accumulates rather than evaporating with each graduate cohort
- Research groups can focus on science rather than DevOps

---

**Next:** Section 3 details our four core propositions—specific infrastructure offerings addressing concrete pain points in computational research at UVM.