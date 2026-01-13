# Section 3: Core Propositions

## 3.1 Team Annotations

### The Problem

Annotation projects consistently take longer and produce less robust data pipelines than researchers expect. Annotation infrastructure tend to have hidden complexity that only becomes apparent mid-project.

**Common failure modes we've observed:**

**Coordination breakdown:** Email and Excel workflows collapse with more than 2 annotators. Files get lost, versions conflict, and no one can reconstruct who annotated what. A recent data availability statement project in our group wasted weeks because we couldn't track annotation provenance through email chains.

**Lost validity:** Without structured workflows, calculating inter-rater reliability is challenging. Research groups annotate thousands of items but can't demonstrate that their annotations are reliable or that annotators agree on theory-laden categories.

**Scope creep:** "Simple annotation" reveals unexpected needs—preprocessing to find relevant text in PDFs, sampling strategies to reduce annotation burden, or real-time consensus metrics to catch disagreements early. Groups realize they need better infrastructure after already investing weeks in broken workflows.

**The Don Norman principle applies:** When every research group independently struggles with the same workflow, the problem isn't individual competence—it's missing infrastructure.

### Why Groups Don't Solve This (Even Though They Could)

Some research groups *could* build proper annotation infrastructure—they have computationally sophisticated students who could learn DevOps, database design, and frontend development. But they **rationally choose not to** because the incentive structure favors fast, cheap solutions over robust infrastructure.

**The cost-benefit calculation:**
- Building production-quality annotation infrastructure: 80-120 hours of skilled labor
- Learning curve for DevOps, database management, and maintenance: 40-80 hours
- Ongoing maintenance burden: 5-10 hours per month indefinitely
- **Total investment: 150+ hours initial + ongoing overhead**

**The alternative:**
- Excel + Dropbox: 2 hours setup, familiar tools, "good enough"
- Label Studio cloud: 4 hours setup, $100/month, works immediately
- Google Forms: 1 hour setup, free, minimal learning curve

**Even when the alternative breaks (which it often does)**, the time spent troubleshooting (20-40 hours) is still less than building proper infrastructure from scratch. And critically: graduate students are optimizing for their dissertation timeline, not the research group's long-term computational capacity.

**The slow vs. fast science problem:**
Current incentive structures reward fast publication over methodological rigor. A PhD student who spends 3 months building robust annotation infrastructure has *delayed their first paper*. They're penalized for doing the responsible thing. The next cohort will thank them, but by then they've graduated and moved on.

**What we offer is amortization of the upfront cost:**
We've already invested the 150+ hours (actually, closer to 300 hours over 3 years) learning what works. We maintain it continuously so individual groups don't have to. When you use our infrastructure, you're accessing institutional investment rather than making that investment yourself.

**The value proposition isn't "you can't do this"—it's "you shouldn't have to reinvent this wheel."** Your students should focus on domain research, not learning PostgreSQL administration.

### What We Offer

After 3 years of trial and error, we've built annotation infrastructure that now serves 13 researchers with near-zero marginal onboarding cost. Our self-hosted Label Studio instance has supported annotation of 45,000+ data points across multiple projects. We've learned what works, what fails, and how to avoid common pitfalls.

We offer annotation support at three levels:

#### Tier 1: Managed Label Studio Access
**What you get:**
- Access to pre-configured, self-hosted Label Studio instance
- SSO authentication (ORCID or university credentials)
- Standard workflows for categorical labeling, span annotation, and image classification
- Onboarding documentation based on institutional learning
- Professional maintenance (security patches, platform upgrades)

**Setup time:** 1-2 hours (add user, brief training session)

**Pricing:**
- One-time setup: $500
- Annual access fee: $200/year per research group
- Included: Platform maintenance, basic technical support

**Best for:** 
- Teams with 2-10 annotators doing standard annotation tasks
- Projects with straightforward categorical or span labeling
- Groups wanting minimal setup time and guaranteed maintenance

**Current users:** 13 active researchers across 4 research groups

#### Tier 2: Custom Annotation Infrastructure
**What you get:**
- Everything in Tier 1, PLUS:
- Custom preprocessing pipelines (PDF text extraction, reranking for "needle in haystack" problems, entity extraction)
- Sampling strategies (stratified sampling, simple active learning)
- Inter-rater reliability calculation scripts and dashboards
- Training sessions for annotation team (resolving category disagreements, establishing coding protocols)
- OR: Purpose-built annotation application for workflows that don't fit Label Studio

**Example custom application:** Our interdisciplinarity annotator—a mobile-first web app that addresses two limitations of Label Studio:

1. **Mobile accessibility:** Label Studio's desktop-oriented interface is clunky on phones. Our app is designed mobile-first, allowing annotators to work during commutes, waiting rooms, or fieldwork. This dramatically increases annotation completion rates—researchers report annotating 2-3x more items per week when they can utilize "dead time."

2. **Better inter-annotator agreement visualization:** Label Studio's agreement metrics are buried in exports. Our app displays real-time agreement matrices showing exactly where annotators disagree, enabling early intervention when systematic misunderstandings emerge.

Built in 1 week using SvelteKit + FastAPI + PostgreSQL. Features ORCID authentication, custom annotation categories, and structured data export. Now being reused by another research group with minimal customization.

**Setup time:** 2-4 weeks (1 week requirements gathering + 1-3 weeks development + knowledge transfer)

**Pricing:**
- Initial build: $8,500 (includes 6 months maintenance)
- After 6 months, choose:
  - Ongoing maintenance retainer: $250/month
  - Consulting retainer (for self-maintaining groups): $150/month
  - Sunset project (infrastructure remains accessible, code is yours)

**Best for:**
- Complex annotation tasks requiring domain-specific preprocessing
- Novel workflows not supported by standard platforms
- Projects needing mobile access or specialized UI/UX
- Groups with capacity to eventually self-maintain (with training)

#### Tier 3: Annotation Partnership
**What you get:**
- Everything in Tier 2, PLUS:
- Iterative experimentation and continuous improvement
- Integrated student training on computational best practices
- Strategic consultation on annotation scheme design and methodology

> [!NOTE] **📦 ADVANCED ANNOTATION FEATURES (TIER 3)**
> Long-term partnerships enable experimentation with cutting-edge approaches:
> 
> **Active learning:** Intelligently sample which items to annotate next based on model uncertainty, reducing annotation burden by 30-40%
> 
> **LLM-assisted pre-annotation:** Use language models to suggest initial labels, with human verification—speeds up annotation while maintaining quality
> 
> **Information surprisal sampling:** Prioritize annotating items that are most informative for your research question
> 
> **Real-time consensus metrics:** Track annotator agreement continuously, catch systematic misunderstandings early
> 
> These are research-grade capabilities requiring ongoing collaboration, not one-time setup. Available only in Tier 3 partnerships where we co-develop solutions iteratively.

**Setup time:** Initial 1-month sprint, then ongoing engagement

**Pricing:**
- Initial sprint: $11,366
- Ongoing: $2,273/month (20% FTE) for minimum 12 months

**Best for:**
- Research groups building annotation as a core long-term capability
- Projects with evolving requirements and continuous data collection
- Groups wanting to cultivate "garden" of computational capabilities over time

### Evidence: What We've Learned

**From 3 years of iteration:**

**What works:**
- Self-hosting Label Studio is cheaper long-term than cloud ($250/year VM vs. $1,200+ cloud subscription)
- Preprocessing matters more than platform choice (finding relevant text in 50-page PDFs is the hard part)
- Mobile-first interfaces dramatically increase annotation completion rates—researchers report completing 2-3x more annotations per week when they can utilize "dead time" (commutes, waiting rooms, fieldwork breaks)
- Real-time inter-annotator agreement dashboards catch systematic disagreements early
- Simple active learning (annotate high-uncertainty items first) can reduce annotation burden by 30-40%

**What doesn't work:**
- Expecting researchers to learn Label Studio on their own (onboarding matters)
- Building overly complex custom apps (maintenance burden kills you)
- Ignoring the human side (annotation scheme design, training, resolving disagreements)
- Treating annotation as purely technical problem (it's methodology + infrastructure)

**Concrete impact:**
Our interdisciplinarity annotator enabled a systematic review of 500+ papers with 5 annotators. Without proper infrastructure, this would have taken 4-6 months with Excel/email workflow. With our platform: 6 weeks, with full inter-rater reliability metrics and audit trails.

### Cost Analysis: Ecology Lab Example

**Scenario:** Mid-sized ecology lab needs to annotate species identifications from 2,000 field camera images. Three research assistants will annotate over 3 months.

**Without RSE support (typical approach):**
- PhD student researches annotation tools: 80 hours
- Builds Excel + Dropbox workflow: 20 hours
- Workflow breaks down, tries Label Studio cloud: 40 hours
- Label Studio cloud subscription: $100/month × 12 months = $1,200
- Training 3 annotators on evolving workflow: 15 hours
- Lost productivity from coordination issues: 20 hours
- **Total: 175 person-hours + $1,200 ≈ $9,950** (assuming $50/hour student labor)
- **Outcome:** Annotations complete but no inter-rater reliability calculated, methodology defensibility questionable

**With RSE support (Tier 1):**
- Setup: $500 (1-2 hours RSE time)
- Annual access: $200
- Training: 2 hours (included)
- Student time: ~35 hours (actual annotation work only)
- **Total Year 1: $700 + $1,750 = $2,450**
- **Total Year 2+: $200/year** (maintenance included)
- **Outcome:** Production-quality infrastructure, full inter-rater reliability, defensible methodology, reusable for future projects

**ROI:** Save ~$7,500 in first year, plus:
- Students focus on research instead of infrastructure
- Methodology is defensible (reviewers can't question annotation reliability)
- Infrastructure reusable for lab's next 5-10 annotation projects
- Students learn professional annotation workflows (skill transfer)

**If lab needs custom preprocessing (Tier 2):**
Perhaps images need ML-based filtering first, or annotation workflow requires specialized UI. Initial cost higher ($8,500) but still cheaper than failed attempts + commercial alternatives over 2-3 years.

### Maintenance & Sustainability

**Tier 1 maintenance (included):**
- Security patches and platform upgrades
- Basic technical support (email response within 48 hours)
- Platform hosting and backups
- **Funded by:** Collective annual fees + institutional investment

**Tier 2/3 maintenance:**
After initial 6-month period, groups choose their path:
- **Continue with us:** Predictable monthly retainer, we handle everything
- **Self-maintain:** We've trained your team, provided documentation, available for consulting
- **Sunset gracefully:** Core data remains accessible (PostgreSQL), code is yours (open source)

**Progressive enhancement guarantee:**
Even if our office closes, your data survives in open-source formats with documented schemas. Compare to commercial cloud where vendor closure could make data recovery painful or expensive.

### Current Status & Capacity

**Active deployments:**
- 1 production Label Studio instance (13 active users, 4 research groups)
- 1 custom annotation application (interdisciplinarity annotator)
- 2 subsidized pilot projects in progress

**Available capacity (next 18 months):**
- Tier 1: Can onboard 10-15 additional users ✅
- Tier 2: Can develop 3-4 new custom projects 📊
- Tier 3: Can support 1-2 new long-term partnerships ⚠️

**Early adoption incentive:**
For the next 6 months, we're subsidizing 2-3 Tier 2 pilot projects at 50% cost ($4,250 instead of $8,500) to demonstrate value and refine our offerings. Contact us to discuss eligibility.

---

**Next steps:** If annotation infrastructure addresses a pain point in your research, contact the Open Source Programming Office to schedule a consultation. We'll assess your needs, recommend appropriate tier, and provide honest evaluation of whether our services are a good fit for your project.