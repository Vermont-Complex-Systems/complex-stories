# Section 3.1: Custom Research Websites

## The Discovery Problem

Bob is a new PhD student in Alice's ecology lab studying bird migration patterns. Alice has a Drupal website following university guidelines—research overview, project descriptions, team photos updated eight months ago. She also maintains a personal page with her CV and publication list.

As Bob starts his PhD, Alice mentions he should "talk to Sam about the bird database." Bob emails Sam, who replies three days later with a CSV export from a PostgreSQL database on his laptop. The file has 47 columns with cryptic names like `loc_type_3` and `obs_conf_flag`. No documentation. No data dictionary. Sam is finishing their dissertation and frantically job hunting.

Bob spends weeks reverse-engineering the data structure, writes Python scripts to parse it, and builds his first migration models. Six weeks into his analysis, he presents preliminary results at lab meeting.

Alice says: "Interesting patterns! This aligns with what we saw in the human activity data."

Bob looks confused. "What human activity data?"

Alice realizes she forgot to mention Jacques entirely. "Oh! Jacques has been collecting social media and GPS data near the field sites—should have connected you two months ago."

**Bob only learns about Jacques' dataset by accident.** If Alice had been busier that week, or if Bob had been too nervous to present early results, he might have completed his entire first paper without knowing a crucial complementary dataset existed *in the same lab.* Not because anyone made mistakes, but because there's no infrastructure making visible what research and data exist.

This isn't a failure of Alice as a mentor or Bob as a student. It's a **structural absence of discovery mechanisms.** Research groups operate like disconnected silos even within the same lab.

## What Drupal and Personal Pages Don't Solve

**Alice's Drupal site provides:**
- Static "Research Projects" page describing broad themes
- "People" page with headshots and outdated bios
- Manually maintained publication list
- Generic contact form

**Alice's personal page provides:**
- CV with publications
- Brief research statement
- Perhaps student profiles (when she remembers to update them)

**What's systematically missing:**
- No searchable catalog of research topics or ongoing work
- No way to discover connections across lab members ("who else works on migration?")
- No programmatic updates (everything manual → gets outdated → becomes unreliable)
- No onboarding pathway beyond "email Alice and hope she mentions everyone"

**The consequence:** Bob explores both sites, sees Alice works on bird migration, sees Sam listed as a student. He has no mechanism to discover that Jacques—also in the lab—has complementary data on human activity patterns. The websites don't reveal connections between research threads.

## Our Solution: Two-Tier Approach

We build custom research websites using modern web technologies (SvelteKit, Hugo, responsive design) with a clear progression path as your needs grow.

### Tier 1: Simple Static Sites ($1,600-3,200)

**Best for:** Conferences, workshops, events, small lab sites with primarily static content

**What's included:**
- 5-10 static pages (home, about, speakers/people, schedule/research, venue/contact)
- Hugo/Jekyll/11ty static site generator (fast, secure, no backend)
- Responsive mobile-first design
- Basic customization of professional theme
- First year hosting included (~$50-100)
- Timeline: 1-2 weeks

**Pricing:** $1,600-3,200 (10-20 hours @ $160/hr effective rate)

**Examples:**
- Conference websites (IC2S2-2026 pattern)
- Workshop series sites
- Small research group homepages
- Temporary project sites

**Value proposition vs. alternatives:**
- **vs. Templates ($50-500):** Custom design, professional implementation, academic context understanding
- **vs. DIY platforms (Wix/Squarespace):** Better performance, no recurring subscription fees, full code ownership
- **vs. Agencies ($4,000-15,000):** Lower cost, faster turnaround, understanding of academic workflows

**Growth path:** Start here for basic presence. When you need auto-updating publications, interactive visualizations, or backend data, upgrade to Tier 2 with existing design/hosting intact.

### Tier 2: Data-Driven Research Websites ($6,400-8,000)

**Best for:** Research centers, labs needing discovery tools, sites showcasing ongoing research with auto-updating content

**What's included (everything from Tier 1, PLUS):**
- Data-driven components (publications, topics, team profiles auto-updated from external APIs)
- Interactive visualizations (topic bubble charts, filterable publication grids)
- Search functionality across content
- OpenAlex/ORCID/institutional repository integration
- Analytics integration
- Automatic rebuild schedule (weekly or triggered)

**Pricing:** $6,400-8,000 (40-50 hours)

**Timeline:** 4-6 weeks from kickoff to launch

**Example: Vermont Complex Systems Center website**

Each faculty member's page includes:
- **Interactive topic visualization:** Bubble chart where bubble size indicates number of papers on each topic (pulled from OpenAlex API)
- **Filterable publication grid:** Click a topic bubble → see related papers; sort by date or citations
- **Searchable abstracts:** Search functionality across all faculty publications

**How this helps Bob:**
1. Bob joins the lab, visits the research center website
2. Searches "bird migration" → finds Alice's papers, but also discovers Jacques' work on "migration patterns and human activity"
3. Clicks through to Jacques' papers, reads abstracts, realizes Jacques has complementary data
4. Contacts Jacques **before** building his entire analysis pipeline in isolation
5. **Problem prevented, not just discovered later**

**Architecture: Static Sites with Dynamic Data**

Pull data at build time, generate static pages, update on schedule:

```
Build process:
1. Query OpenAlex API for faculty publications
2. Extract topics, abstracts, citations, co-authors
3. Generate static HTML with interactive components
4. Deploy to simple hosting (~$100/year)
5. Rebuild weekly (or when triggered)

Result:
- Fast, cheap, scalable static site
- Always current (auto-updates from data sources)
- No database or backend to maintain
- Progressive enhancement (works even on old browsers)
```

**Process:** Discovery meeting → Design and data integration planning → Development (3-4 weeks) → Review → Launch

**You provide:** Content for static pages, list of data sources to integrate, branding preferences

## Growth Path: From Website to Platform

Many research groups follow this progression:

**Stage 1: Simple Static Site (Tier 1)**
Conference website or basic lab homepage → **$1,600-3,200**

**Stage 2: Data-Driven Site (Tier 2)**
Add auto-updating publications, interactive visualizations → **Additional $4,800-5,600**

**Stage 3: Add Visual Data Essays (Section 3.2)**
Publish interactive research stories using same design system → **$3,200-4,800 per essay**

**Stage 4: Connect Data Infrastructure (Section 3.3)**
Display lab's actual datasets from centralized catalog, provide API access → **$6,400-9,600 for basic infrastructure**

**The value:** Each stage builds on previous work. Design system reused. Hosting shared. Institutional memory preserved. You're not starting over each time—you're enhancing what exists.

> [!NOTE] **📦 ADDING VISUAL DATA ESSAYS (SECTION 3.2)**
> Once your research group has a custom website, integrating visual data essays becomes straightforward:
> - Interactive stories use the same design system and infrastructure
> - Seamless navigation between site pages and essays
> - Shared hosting and analytics
>
> Many research groups start with a website (Section 3.1), then add visual essays (Section 3.2) as they publish findings worth showcasing.

> [!NOTE] **📦 CONNECTING TO DATA INFRASTRUCTURE (SECTION 3.3)**
> Data-driven websites become significantly more powerful when connected to research data infrastructure:
>
> **With data infrastructure (3.1 + 3.3):**
> - Display your lab's actual datasets from centralized catalog (not just publications)
> - Team pages show "Sam maintains Bird Database - [API docs] [access instructions]"
> - Onboarding documentation links directly to data access endpoints
> - New students discover both research AND data infrastructure through one interface
>
> This is Bob's complete solution: website helps him discover Jacques' work, data infrastructure gives him immediate access to Jacques' data.
>
> See Section 3.3 for how centralized data infrastructure enables this integration.

## When to Choose Which Tier

**Choose Tier 1 (Simple Static) if:**
- You need a professional web presence quickly
- Content is primarily static (event info, team bios, project descriptions)
- Budget is constrained ($1,600-3,200 range)
- You don't need auto-updating content or complex interactions
- Timeline is short (1-2 weeks)

**Choose Tier 2 (Data-Driven) if:**
- You want discovery tools (search, filtering, topic visualization)
- Publications should auto-update from authoritative sources
- You have multiple researchers whose work interconnects
- Budget supports richer functionality ($6,400-8,000 range)
- Timeline allows 4-6 weeks development

**Not sure?** Start with Tier 1. We design for extensibility—upgrading to Tier 2 later reuses existing design and hosting, requiring only incremental investment in new features.

---

**Next:** Section 3.2 (Visual Data Essays and Interactive Dashboards) shows how to transform research findings into engaging, interactive narratives for broader audiences—or build exploratory dashboards for user-driven data analysis.
