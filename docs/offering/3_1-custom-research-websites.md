# Section 3.1: Custom Research Websites

- [ ] Conference/events website

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

## What We Build: Data-Driven Research Websites

We build custom research websites using modern web technologies (SvelteKit, responsive design) with **data-driven components that make research connections visible.**

**The Vermont Complex Systems Center website demonstrates this approach:**

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

**This works without requiring backend infrastructure (Section 3.2).** It's intelligent use of external APIs (OpenAlex, ORCID, institutional repositories) combined with thoughtful UX design and static site generation.

## How It Works: Static Sites with Dynamic Data

**Architecture principle:** Pull data at build time, generate static pages, update on schedule.

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

**For a research lab or center, typical features include:**
- **Team pages:** Dynamic profiles showing current research focus, recent publications, collaboration networks
- **Research topics:** Navigable taxonomy revealing who works on what
- **Publication search:** Full-text search across abstracts and titles
- **Project pages:** Automatically list papers/datasets associated with each funded project
- **Collaboration maps:** Visualize co-authorship patterns within and beyond the group

**Data sources we commonly integrate:**
- OpenAlex (publications, topics, citations)
- ORCID (researcher profiles, verified publications)
- Zotero (group libraries)
- GitHub (code repositories, activity)
- Institutional repositories

**Progressive enhancement layers:**
- **Layer 1:** Static HTML pages, readable anywhere, hostable forever
- **Layer 2:** Interactive components (search, filtering, visualizations)
- **Layer 3:** Real-time features if needed (rare for basic websites)

If sophisticated features break, basic content remains accessible. This isn't just good engineering—it's recognizing the reality of academic funding cycles and personnel turnover.

## Pricing and Timeline

**Standard data-driven website:** $6,400-8,000 (40-50 hours at $80/hour)

**What's included:**
- 5-10 pages (home, people, research, publications, contact)
- Data-driven components (publications, topics, team profiles updated automatically)
- Responsive mobile-first design
- Search and filtering capabilities
- Analytics integration
- First year hosting (~$100)

**Process:** Discovery meeting → Design and data integration planning → Development (3-4 weeks) → Review → Launch

**You provide:** Content for static pages, list of data sources to integrate, branding preferences

**Timeline:** 4-6 weeks from kickoff to launch

**If your needs are more complex** (extensive custom visualizations, sophisticated interactions, many data sources), the scope and pricing adjust accordingly—but it's the same fundamental offering.

> [!NOTE] **📦 ADDING VISUAL DATA ESSAYS (SECTION 3.4)**
> Once your research group has a custom website, integrating visual data essays becomes straightforward:
> - Interactive stories use the same design system and infrastructure
> - Seamless navigation between site pages and essays
> - Shared hosting and analytics
> 
> **Example:** VCSC website hosts research highlights as interactive stories. First story takes ~20 hours to build; subsequent stories take 10-15 hours because website infrastructure exists.
> 
> Many research groups start with a website (Section 3.1), then add visual essays (Section 3.4) as they publish findings worth showcasing.

> [!NOTE] **📦 CONNECTING TO DATA INFRASTRUCTURE (SECTION 3.2)**
> Data-driven websites become significantly more powerful when connected to research data infrastructure:
> 
> **Current capability (3.1 alone):** Display publications from OpenAlex, team bios, project descriptions
> 
> **With data infrastructure (3.1 + 3.2):** 
> - Display your lab's actual datasets from centralized catalog (not just publications)
> - Team pages show "Sam maintains Bird Database - [API docs] [access instructions]"
> - Onboarding documentation links directly to data access endpoints
> - New students discover both research AND data infrastructure through one interface
> 
> This is Bob's complete solution: website helps him discover Jacques' work, data infrastructure gives him immediate access to Jacques' data.
> 
> See Section 3.2 for how centralized data infrastructure enables this integration.

## What This Solves (and What It Doesn't)

**What custom websites with data-driven components solve:**
✅ Discovery of research and people ("who works on topics related to mine?")  
✅ Keeping content current without manual maintenance  
✅ Making connections visible across research groups  
✅ Professional presentation that reflects research sophistication  
✅ Better onboarding for new students and collaborators  

**What this doesn't solve:**
❌ **Data access details:** Bob discovers Jacques exists, but still needs to email to learn "my data is in MongoDB with schema X" → **This is Section 3.2 (Research Data Infrastructure)**  
❌ **Data collection infrastructure:** If Bob needs to annotate bird behaviors or Jacques needs human activity labeled → **This is Section 3.3 (Team Annotations)**  
❌ **Research storytelling and outreach:** Once Bob finishes his research, how does he share findings beyond academic PDF? → **This is Section 3.4 (Visual Data Essays)**

**Think of custom websites as the discovery layer.** It makes visible what research exists and who's doing it. But for the full vision—where Bob not only discovers Jacques' work but can immediately access the data, query it through documented APIs, and eventually tell compelling stories about the findings—you need the integrated approach across our service offerings.

## Current Capacity

**Available capacity (next 18 months):**
- Tier 2: Can build 3-4 new data-driven websites
- Tier 3: Can build 1-2 custom interactive sites

**Typical timeline:** 4-8 weeks from initial meeting to launch

**Early adoption:** We have budget to subsidize 1-2 pilot projects at reduced cost for research groups willing to provide feedback and serve as case studies.

## When Custom Development Makes Sense

**You probably need custom web development if:**
- Drupal templates don't serve your research context (no way to showcase data, code, interactive work)
- You want programmatic content updates (publications, team, projects) that stay current automatically
- Discovery is a problem (students can't find related work within your own group)
- Mobile experience matters (most academic site visitors use phones, Drupal mobile experience is poor)
- You're building a research center or multi-PI group needing cohesive presence

**You probably don't need us if:**
- Drupal adequately serves your needs
- Your research is purely informational (no data, code, or computational work to showcase)
- You have a single PI with occasional publication updates (a personal page suffices)
- You lack budget for professional development

**Contact us for a discovery meeting.** We'll provide honest assessment of whether custom development is justified or if simpler solutions suffice. Sometimes the right answer is "Drupal is fine for now" or "wait until you have more infrastructure needs."

---

**Next:** Section 3.2 (Research Data Infrastructure) continues Bob's story—he's discovered Jacques exists, but now needs to access and integrate their data. This is where centralized schemas, API endpoints, and data catalogs prevent the "Sam's database on his laptop" problem.