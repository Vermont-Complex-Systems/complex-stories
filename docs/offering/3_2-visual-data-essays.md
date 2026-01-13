# Section 3.2: Visual Data Essays and Interactive Dashboards

## The Communication Gap

Maria is a statistics PhD student working with incarcerated individuals who share their experiences through surveys. The participants contributed their stories with the explicit promise that their voices would reach beyond prison walls—that policymakers, families, and the broader public would hear what they had to say.

Maria completes a rigorous analysis. The findings are important: systematic patterns in how incarceration affects mental health, family relationships, and post-release outcomes. She publishes in a respected peer-reviewed journal. The paper is methodologically sound, carefully written, and will be read by approximately 200 academics.

The participants' voices—the reason they engaged with the research—will never reach the audiences they were promised. The findings sit in a 40-page PDF behind institutional access, formatted for academic reviewers, not public understanding.

Maria wants to do better. She explores her options:

**Jupyter notebooks or Quarto** offer familiar environments with minimal deployment complexity, but theming is opinionated and limiting. Custom layouts require fighting the notebook paradigm. The result looks computational, not designed.

**Streamlit or Shiny** provide more control for dashboard-style interfaces, but creating custom visualizations means working through wrapper libraries that constrain access to the full JavaScript ecosystem. They're built for analytical exploration, not narrative scrollytelling.

**Custom D3 development** offers complete creative control and publication-quality results, but requires months of learning frontend development—time Maria doesn't have while finishing her dissertation.

**The gap:** Researchers want engaging communication but existing tools either limit creative control or require prohibitive technical investment. The middle ground—publication-quality interactive storytelling without becoming a frontend specialist—isn't readily accessible.

## Our Solution: Two Interaction Patterns

We build interactive data experiences using modern web technologies (SvelteKit, D3, responsive design). The key distinction is **interaction pattern**:

### Pattern 1: Narrative-Driven Stories (Scrollytelling)

**Best for:** Communicating research findings to broader audiences with a guided, linear narrative

**Characteristics:**
- Author-controlled narrative flow (scroll-based progression)
- Visualizations reveal insights as reader progresses
- Text and graphics tightly integrated
- Mobile-first design (50-60% of readers use phones)
- Goal: Persuade, inform, engage

**Example: Complex Stories Platform**

Publication-quality interactive essays that make research accessible. Think data journalism (The Pudding, The Upshot) for academic research.

**Typical features:**
- Scrollytelling (visualizations respond to scroll position)
- Embedded interactive elements within narrative
- Aggregate visualizations with careful privacy protections
- Personal quotes/stories integrated with data
- Analytics tracking engagement

**Pricing:** $3,200-4,800 (20-30 hours)
**Timeline:** 3-4 weeks with existing infrastructure, 2-3 months for first collaboration
**Includes:** First year hosting, minor updates

**Workflow:**
1. Discovery meeting: Understand findings, identify key insights
2. Data preparation: Researcher provides cleaned data (CSV/JSON)
3. Narrative development: Researcher drafts story arc
4. Design & development: Build scrollytelling structure, custom visualizations
5. Iteration & refinement
6. Publication: Deploy, set up analytics

**Best for:**
- Published findings worth sharing beyond academic audiences
- Research with clear narrative arc and key takeaways
- Public engagement requirements or commitments to participants
- Policy implications or societal relevance

### Pattern 2: Exploratory Dashboards (User-Driven)

**Best for:** Enabling users to query, filter, and explore data themselves

**Characteristics:**
- User-controlled exploration (not author-directed)
- Multiple visualization modes and filtering options
- Real-time queries against backend databases
- Performance optimization for large datasets
- Goal: Enable discovery, answer user-specific questions

**Example: Wikigrams Dashboard**

Interactive interface for exploring Wikipedia n-grams data across time, geography, and topics. Users query millions of records through intuitive controls.

**Architecture:**
- MongoDB backend (handling large-scale data efficiently)
- FastAPI with intelligent caching strategies
- SvelteKit frontend with responsive visualizations
- Real-time query performance (<500ms for most requests)

**Typical features:**
- Multi-dimensional filtering (date, geography, categories)
- Sortable/searchable data tables
- Interactive charts responding to user selections
- Export functionality for user-defined subsets
- Progressive disclosure (simple → advanced controls)

**Pricing:** $4,800-9,600 (30-60 hours)
**Timeline:** 4-8 weeks depending on data complexity
**Includes:** Backend setup, API development, frontend implementation, first year hosting

**Workflow:**
1. Discovery: Understand data structure, user questions, query patterns
2. Backend architecture: Design database schema, API endpoints, caching strategy
3. Frontend development: Build query interface, visualization components
4. Performance optimization: Ensure responsive queries at scale
5. Documentation: API docs, user guides
6. Deployment: Backend + frontend hosting, monitoring setup

**Best for:**
- Large datasets requiring user-driven exploration
- Multiple valid ways to slice/analyze data
- Researchers wanting to share datasets publicly with query interfaces
- Projects where users have diverse, specific questions
- Datasets requiring backend infrastructure (>100MB, complex queries)

## Technical Architecture: How We Handle "Big-ish" Data

Many research datasets are too large for static sites (>100MB) but don't require enterprise database infrastructure. We specialize in this middle ground.

**Our approach:**

**For narrative stories (<100MB data):**
- Static site generation (fast, cheap, scalable)
- Data embedded as JSON/CSV
- No backend required
- Hosting: ~$50-100/year

**For exploratory dashboards (>100MB to ~1TB):**
- FastAPI backend with PostgreSQL or MongoDB
- Intelligent caching (Redis for frequently-accessed queries)
- API design prioritizing common query patterns
- Frontend optimizations (virtualization, pagination, lazy loading)
- Progressive enhancement (core functionality works even if backend slow)
- Hosting: ~$250-500/year

**Performance tricks we use:**
- Pre-aggregate common queries during ETL
- Cache results with smart invalidation
- Frontend pagination/virtualization for large result sets
- Responsive design that adapts to mobile constraints
- Progressive loading (show results as they arrive)

**Example: Wikigrams serves millions of n-grams efficiently** through pre-computed indexes, intelligent caching, and frontend optimizations—enabling real-time exploration without enterprise infrastructure costs.

## Working with Sensitive/Proprietary Data

Both patterns can handle sensitive or proprietary data with appropriate controls:

**Access control options:**
- Public (anyone can access)
- Authentication required (ORCID, institutional SSO)
- IP-restricted (campus networks only)
- Time-limited access (conference attendees during event)
- Request-based access (researchers apply for credentials)

**Privacy protections:**
- Aggregate-only visualizations (no individual-level data)
- Differential privacy techniques for statistical releases
- Data minimization (only expose necessary fields)
- Audit logging (track who accessed what, when)

**Compliance support:**
- IRB protocol implementation
- FERPA/HIPAA compliance consultation
- Data sharing agreements
- Usage analytics for reporting requirements

**Example: Wikigrams demonstrates public data sharing** with API-based access, but the same architecture supports authenticated access for proprietary datasets.

## Pricing Summary

**Narrative-Driven Story (Simple):** $3,200-4,800 (20-30 hours)
- Scrollytelling narrative
- Static site (no backend)
- 3-6 sections with custom visualizations
- Timeline: 3-4 weeks

**Narrative-Driven Story (Complex):** $6,400-9,600 (40-60 hours)
- Multiple interconnected visualizations
- Backend required (large dataset or real-time updates)
- Custom interactive features
- Timeline: 6-8 weeks

**Exploratory Dashboard (Standard):** $4,800-9,600 (30-60 hours)
- Query interface with multiple views
- Backend + API + frontend
- Datasets up to ~100GB
- Timeline: 4-8 weeks

**Exploratory Dashboard (Complex):** $9,600-16,000 (60-100 hours)
- Multiple linked datasets
- Advanced query capabilities
- Performance optimization for large scale
- Timeline: 8-12 weeks

> [!NOTE] **📦 INTEGRATION WITH RESEARCH WEBSITES (SECTION 3.1)**
> Both narrative essays and dashboards become more efficient when research groups already have custom websites:
> - Reuse design system and infrastructure (consistent branding)
> - Integrate into site navigation
> - Share hosting and analytics setup
>
> First project: 20-30 hours. Subsequent projects: 10-20 hours because infrastructure exists.

> [!NOTE] **📦 CONNECTION TO DATA INFRASTRUCTURE (SECTION 3.3)**
> Exploratory dashboards are most efficient when built on top of existing research data infrastructure:
> - Query centralized databases directly (no data duplication)
> - Reuse ETL pipelines and data cleaning logic
> - Leverage existing API endpoints
> - Inherit access controls and audit logging
>
> If you're building data infrastructure (Section 3.3), adding an exploratory dashboard is incremental work—the hard part (backend) already exists.

## When to Choose Which Pattern

**Choose Narrative-Driven Story if:**
- You have a clear story to tell with defined takeaways
- Target audience is general public, policymakers, or journalists
- Goal is persuasion or engagement (not self-service exploration)
- Data is manageable size (<100MB) or can be aggregated
- You want author control over how findings are presented

**Choose Exploratory Dashboard if:**
- Users have diverse, specific questions you can't anticipate
- Dataset is too large/complex for static embedding
- Goal is enabling discovery and self-service analysis
- You're sharing a dataset publicly with query capabilities
- Target audience includes researchers who want to explore independently

**Not sure?** Start with a narrative story. If users consistently ask "can I filter by X?" or "show me Y subset," that signals need for exploratory dashboard. We can add query capabilities later.

## Growth Path: From Story to Platform

Many research groups follow this progression:

**Stage 1: Simple Narrative Story**
Communicate one key finding → **$3,200-4,800**

**Stage 2: Add Backend for Interactivity**
Enable user filtering/exploration within narrative → **Additional $3,200-4,800**

**Stage 3: Build Exploratory Dashboard**
Full self-service query interface → **$4,800-9,600** (or incremental if backend exists)

**Stage 4: Connect to Data Infrastructure**
Dashboard queries centralized research databases → **$6,400-9,600 for infrastructure** (Section 3.3)

**The value:** Each stage builds on previous work. Code reused. Lessons learned. Institutional knowledge preserved.

---

**Next:** Section 3.3 (Research Data Infrastructure) shows how to build centralized data systems that enable collaboration, reproducibility, and institutional memory—the foundation for exploratory dashboards and growing research groups.
