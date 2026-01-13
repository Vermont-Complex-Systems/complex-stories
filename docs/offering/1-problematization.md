# 1.

Computational projects typically involve components of the data engineering lifecycle (Figure 1-1). Data generation takes one of three forms: (i) simulation, (ii) direct collection via surveys, experiments, or sampling, or (iii) ingestion from upstream providers such as APIs or public datasets. Unlike traditional qualitative research, computational projects require extensive custom code for data ingestion, transformation, and sharing—or data pipelines.

In industry, this lifecycle is supported by specialized roles (Figure 1-2): software engineers and data architects design systems, data engineers implement pipelines, DevOps engineers maintain infrastructure, and downstream consumers (data analysts, scientists, ML engineers) focus on analysis. This division of labor is a testimony that robust data infrastructure requires dedicated expertise and accountability structures. But academia is not industry. 

Individual researchers, typically graduate students in emerging computational fields, are expected to perform all these specialized roles simultaneously while lacking formal training in software engineering, data architecture, or systems design. A PhD student is expected to scrape data, wrangled the data in a way that is reproducible and bug-free, provide data visualization—while also conducting their research. Yet the validity of their scientific conclusions depends entirely on the robustness of infrastructure they build.

## The Consequences Are Measurable

Studies document that computational research suffers from obsolete data availability statements, code that cannot be executed without substantial reverse-engineering, and results that fail to replicate. A malformed data join silently redefines what entities the research is actually studying. An undocumented transformation makes methodology impossible to assess. A hardcoded parameter invalidates months of downstream analysis. These aren't edge cases—they represent systematic infrastructure failure.

**The pattern is predictable and pervasive:** A graduate student builds a scraping pipeline, stores data in custom CSV format, processes in Jupyter notebooks. Their labmate can't figure out the schema, rebuilds everything differently. A third student needs both datasets, gives up, starts from scratch. When the first student graduates, their undocumented code breaks, their idiosyncratic data format becomes archaeological puzzle, and privacy considerations that were afterthoughts become institutional liability. The next cohort rebuilds from zero, wasting hours and hours.

Beyond bugs and irreproducibility, there's a deeper issue: when domain experts build infrastructure without software engineering training, they encode their assumptions invisibly into the pipeline. Hardcoded values aren't just technical errors—they're epistemological choices made opaque by poor documentation. Bad joins don't just produce wrong numbers—they silently redefine what entities the research is actually studying. The amateurization of computational infrastructure means the methodological choices that most fundamentally shape results are made by people least equipped to recognize they're making choices at all.


Research groups collectively waste hundreds of person-hours annually reinventing infrastructure that already exists in mature form but remains invisible to researchers starting new projects. The cognitive load is incompatible with research productivity. A student who spends 3 months building proper data infrastructure has delayed their first paper and will be penalized in a job market that counts publications, not infrastructure contributions.

## The Root Cause Is Structural, Not Individual

This crisis emerges from treating code as ancillary to research rather than as research infrastructure requiring the same rigor as laboratory equipment. Consider the asymmetry: a biology department would never expect graduate students to fabricate their own microscopes, yet computational departments expect students to architect entire data systems from first principles.

**The incentive structure compounds the problem.** Researchers face mounting pressure to increase publication output while research questions grow more complex. Computational projects would benefit from simulation studies validating that proposed data can answer research questions, but such groundwork delays publication. Researchers access ever-larger datasets, creating expansive gardens of forking analytical paths, yet explore only narrow subsets without systematic validation that their choices yield representative or valid results.

Institutions have externalized the cost of computational infrastructure onto the researchers least equipped to bear it. Graduate students absorb impossible technical burdens, producing the computational scaffolding that enables senior researchers' careers while receiving minimal credit, training, or compensation for this specialized labor. When their code fails to replicate, the failure is individualized rather than recognized as inevitable outcome of systematic underinvestment.


## What This Requires: Professional Infrastructure Development

This is where the Open Source Programming Office enters: as an experiment in whether fee-for-service Research Software Engineering support can provide sufficient value to justify institutional investment while building computational capacity that compounds over time.

The solution is not training researchers to become better programmers—it is recognizing that robust computational infrastructure requires dedicated professional roles. Research Software Engineers (RSEs) possess specialized expertise in data architecture, software engineering, and computational systems.

**RSEs serve three critical functions:**

**Institutional memory:** Preventing the knowledge evaporation that occurs when PhD students graduate and their hard-won computational expertise leaves with them. An RSE who supports a research center for 3-5 years accumulates understanding of what works, what fails, and why—knowledge that would otherwise be rebuilt from scratch by each cohort.

**Force multipliers:** One RSE supporting 3-5 research teams produces better computational science than those teams struggling independently. This is an efficiency argument: the collective time saved across research groups exceeds the cost of professional support.

**Progressive enhancement philosophy:** RSEs architect infrastructure to survive funding uncertainty. When sophisticated features require ongoing support, core functionality remains accessible through simpler pathways. Data persists in open-source formats. Pipelines degrade gracefully rather than catastrophically. This isn't just good engineering—it's recognizing the reality of academic funding cycles.


## Looking Forward

The following sections detail our service offerings—not as comprehensive solution to systemic problems we cannot fix alone, but as pragmatic experiment in making computational research more efficient, reproducible, and sustainable within current institutional constraints.

We cannot change tenure requirements that prioritize publications over infrastructure. We cannot force departments to hire research software engineers as permanent staff. We cannot eliminate the pressure for "faster science" over methodologically rigorous science.

**What we can do:**
- Provide professional infrastructure that research groups cannot build themselves
- Establish institutional memory that survives personnel turnover  
- Build reusable systems that compound value over time
- Design with progressive enhancement so infrastructure survives funding uncertainty
- Train motivated researchers in computational best practices
- Demonstrate that professional RSE support is cost-effective compared to alternatives

If this experiment succeeds, it provides evidence that universities should invest in permanent RSE capacity. If it fails, we'll have learned what support model doesn't work—and the infrastructure we've built remains open-source, documented, and available for future attempts.

The next section outlines our two-mode approach to providing this support.