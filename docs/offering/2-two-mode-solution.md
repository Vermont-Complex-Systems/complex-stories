# Section 2: The Two-Mode Solution

## 2.1 Why RSEs Are The Answer

The infrastructure crisis in computational research cannot be solved by training researchers to become better programmers. The solution requires recognizing that robust computational infrastructure demands dedicated professional roles with specialized expertise in data architecture, software engineering, and computational systems—knowledge that cannot be acquired incidentally while pursuing domain research.

Research Software Engineers (RSEs) sit at the intersection of domain science and professional software development. We possess the technical capabilities to architect production-grade infrastructure while understanding the unique constraints and workflows of academic research. More importantly, we serve as **institutional memory**—preventing the knowledge evaporation that occurs when PhD students graduate and their hard-won computational expertise leaves with them.

The Open Source Programming Office at the Vermont Complex Systems Center represents an experiment in making RSE support accessible to research groups across UVM. Rather than expecting each group to independently solve computational infrastructure challenges, we provide two complementary modes of support.

## 2.2 Our Two-Mode Approach

We reduce the infrastructure burden on research groups through two complementary strategies:

### Mode 1: Reusable Infrastructure Platforms
**The Problem:** Every research group independently builds annotation systems, hosting pipelines, and visualization tools. This collective reinvention wastes hundreds of person-hours annually across UVM while producing fragile, poorly-maintained infrastructure.

**Our Solution:** Build and maintain shared infrastructure that serves multiple research groups. One well-architected, professionally-maintained annotation platform serving 13 researchers is more efficient and reliable than 13 independently-built ad-hoc solutions.

**Examples:**
- Self-hosted Label Studio instance (currently serving 13 active users)
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

## 2.3 Progressive Enhancement: Infrastructure That Survives

A critical insight from three years of building computational infrastructure: **academic funding is inherently unstable**. Grants end. Students graduate. Priorities shift. Infrastructure that requires continuous specialized support becomes abandoned technical debt.

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

**If our office closes or funding ends:**
- You **lose** Layer 3 features (advanced analytics requiring specialized maintenance)
- You **keep** Layer 2 (functional web applications with source code, documentation, and architecture diagrams)
- You **always have** Layer 1 (your data in accessible, open-source formats with clear schema documentation)

**Compare to commercial cloud alternatives:**
- Vendor closes → export process may be painful, incomplete, or expensive
- Pricing changes → forced migration or locked-in costs with no alternatives
- Feature deprecation → workflows break with no recourse
- Data portability → often technically possible but practically difficult

**This is why self-hosted, open-source infrastructure is a strategic investment, not merely an operational cost.** You're building institutional capacity that survives individual funding cycles.

## 2.4 Service Tier Framework

Our offerings are organized into three tiers, each serving different research needs:

### Tier 1: Shared Infrastructure Access
**What it is:** Access to pre-configured platforms we maintain institutionally

**Current offerings:**
- Self-hosted Label Studio annotation platform
- Research data hosting infrastructure  
- Standard preprocessing and analysis pipelines

**Characteristics:**
- **Setup time:** 1-4 hours (primarily onboarding)
- **Cost structure:** Low one-time setup fee + modest annual access fee
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

**Characteristics:**
- **Setup time:** 2-4 weeks development + 1 week knowledge transfer
- **Cost structure:** Project-based pricing + optional ongoing maintenance retainer
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

**Characteristics:**
- **Setup time:** Initial 1-month sprint, then ongoing engagement
- **Cost structure:** Initial sprint + monthly retainer (typically 20% FTE)
- **Duration:** Minimum 12 months, often extended
- **Customization:** Continuous—infrastructure evolves with your research
- **Best for:** Well-funded groups making long-term commitment to computational research

**Trade-off:** Expensive but transforms computational capacity of the research group

## 2.5 The Triage Question: Which Tier Do You Need?

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

## 2.6 Our Startup Reality: Honest Assessment

### Current Status
The Open Source Programming Office is in a **pilot phase**. The Vermont Complex Systems Center has committed to a 2-year position (6 months completed, 18 months remaining) to prove this model can provide sufficient value to justify continued institutional investment.

This is an experiment in whether fee-for-service RSE support can be:
1. **Financially sustainable** (~$100-135k annually including salary and overhead)
2. **High-impact** (demonstrably improving computational research outcomes across UVM)
3. **Scalable** (building reusable infrastructure that compounds over time)

### What We're Building Toward

**Phase 1 (Months 1-6, Complete):**
- Established core infrastructure (annotation platforms, hosting pipelines)
- Delivered pilot projects demonstrating feasibility
- Documented best practices from 3 years of institutional learning
- Built initial customer base (13 active users on shared infrastructure)

**Phase 2 (Months 7-18, Current):**
- Expand service offerings through 9 core propositions
- Build customer pipeline across diverse research groups
- Refine pricing and service tiers based on market feedback
- Subsidize early adoption projects to demonstrate value
- Generate increasing revenue trajectory toward sustainability

**Phase 3 (Months 19-24):**
- Achieve or approach financial sustainability
- Demonstrate institutional impact (publications enabled, grants won, student training)
- Make case for permanent RSE capacity at UVM
- If sustainable: Plan for expansion (hire additional RSEs)
- If not sustainable: Document lessons learned, preserve open-source infrastructure

### The Investment Proposition

**To the Vermont Complex Systems Center:**
We need 18 months of runway to build customer base and prove the sustainability model. This requires:
- Flexibility to adjust pricing and offerings based on real demand
- Support connecting with potential customers across UVM
- Some subsidized or discounted projects to build portfolio and demonstrate value
- Honest evaluation at 18 months: Is this working? Should we continue?

**To Research Groups:**
We're asking you to take a bet on this model. In exchange for early adoption:
- **Discounted or subsidized initial projects** (we have budget to demonstrate value)
- **Priority access** to RSE services while capacity is available
- **Influence over offerings** (your feedback shapes what we build)
- **Progressive enhancement guarantee** (infrastructure survives even if we don't)

**If this experiment succeeds:**
UVM gains permanent RSE capacity—rare at universities our size—with compounding institutional computational infrastructure, reduced vendor lock-in, and knowledge transfer across research groups.

**If this experiment fails:**
- All code and infrastructure remains open source
- Documentation serves as institutional knowledge
- Early adopters retain their infrastructure (progressive enhancement design)
- We'll have learned what RSE support model doesn't work, informing future attempts

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

## 2.7 Why This Model Matters

Traditional approaches to computational research support at universities:

**Central IT approach:** Generic infrastructure that doesn't understand research workflows. Can host a server but can't help design an annotation scheme.

**Commercial cloud approach:** Convenient but creates vendor lock-in, recurring costs without building internal capacity, and no knowledge transfer.

**Every-group-for-themselves approach:** Massive redundancy, fragile infrastructure, knowledge evaporates when students graduate.

**Our approach:** Professional infrastructure development with institutional memory, open-source design, and progressive sustainability models. We're building capacity that compounds over time rather than repeatedly solving the same problems.

The next section details our nine core propositions—specific infrastructure offerings addressing concrete pain points in computational research at UVM.