<script>
	import Label from './Label.svelte';
	import { base } from "$app/paths";
	import Divider from './Divider.svelte';
    import { reveal } from 'svelte-reveal';
</script>


<!-- - displaying **private** data in a secure way
- team annotation
- **managing data pipelines** - interoperability of data sharing through API
- stories - **interactive press release**
- website for larger project, or even research program
- participatory and interactive surveys -->

<!-- Slide 1: Title -->
<section class="slide slide-hero column-wide">
	<div class="content-section">
	<h1>How to work with us!</h1>
	<h3>Complex Stories is about broadening the audience of scientific research with whimsical and interactive data stories, while showcasing best software practices to ensure sustainability of research software. We are deeply inspired and grateful to the folks at <a href="https://pudding.cool/">The Pudding</a> for their work in the open.</h3>
	</div>
	<div class="author-info">
		<p>- Jonathan St-Onge</p>
		<p>2.12.2025</p>
	</div>
	<div class="hero-image">
		<img src="{base}/back-to-the-future.png" alt="back-to-the-future" />
	</div>
</section>

<Divider />

<!-- Slide 2: Who am I -->
<section class="slide slide-two-column column-wide"  use:reveal={{ delay: 100  }}>
	<div class="content-section">
	<Label>Who am I?</Label>
        <ul>
         	<li><a href="{base}/author/jonathan-st-onge">Jonathan St-Onge</a> holds a Ph.D. in Complex Systems and Data Science from the University of Vermont, where he was a <a href="https://verso.w3.uvm.edu/">VERSO</a> PhD Fellow. His thesis on theoretical models of groups in network science was completed under Professor Laurent Hébert-Dufresne's supervision as a member of the <a href="https://joint-lab.github.io/people/jonathan-st-onge/">Joint-lab</a>. With roots in the humanities, he brings an interdisciplinary perspective to complex systems research.</li>
            <li>As a research software engineer, he helps research groups accelerate and strengthen their computational capabilities by promoting <em>best software practices</em> in academia, including:</li>
            <ul>
                <li>Writing <em>sustainable code</em> that can outlive its original author — reducing technical debt and enabling long-term research continuity.</li>
                <li>Packaging software that is <em>adequately tested</em>, increasing its epistemic reliability and reproducibility.</li>
                <li><em>Promoting community practices</em> that bridge industry standards with academic workflows — improving team collaboration, onboarding, and project management.</li>
            </ul>	
            <li>With his experience in academia, he can help writing grants, collaborate across disciplines, and support diverse teams — especially those new to coding or computational tools.</li>
        </ul>	
    </div>

	
	<div class="image-section" style="transform:translateY(50%)">
		<a href="{base}/author/jonathan-st-onge">
			<img src="{base}/common/assets/authors/jso.jpg" alt="Jonathan St-Onge" />
		</a>
	</div>
</section>

<Divider />

<!-- Slide 3a: Short Projects -->
<section class="slide slide-three-column column-wide"  use:reveal={{ delay: 50  }}>
	<div class="content-section">
        <Label variant="secondary">"1-2" months projects</Label>
        <p>We can write code to help you accomplish specific research tasks — fast. These are short, high-impact collaborations that can be funded through fee-for-service mechanisms or grants.</p>
        <ul>
		    <li>Projects with <em>clear, established goals</em>, where the path to delivery is well defined.</li>
            <li>We have <em>prior experience</em> with similar open-source tools, so we can deliver quickly and reliably, <em>ceteris paribus</em>.</li>
            <li><em>The data is familiar</em> territory — data you already collected and understand, making the collaboration efficient and low-risk.</li>
            <li>Typical outcomes include <a href="{base}/allotaxonometry">interactive dashboards</a>, what we call <a href={base}/friends-funnier-than-you-are>interactive press releases</a> and other storytelling components of <a href="https://vermontcomplexsystems.org/events/cnww/">all kinds</a> that help share key findings with the broader public or stakeholders.</li>
        </ul>
    </div>
	
	<div class="divider-section">
		<div class="vertical-line"></div>
	</div>
	
	<div class="image-section">
		<div class="image-grid">
			<a href="{base}/friends-funnier-than-you-are" class="image-item primary">
				<img src="{base}/common/thumbnails/screenshots/friends-funnier-than-you-are.jpg" alt="Friends Funnier Than You Are Project" />
			</a>
			<a href="{base}/allotax-scrolly" class="image-item secondary">
				<img src="{base}/common/thumbnails/screenshots/allotax-scrolly.jpg" alt="Allotax Scrolly Project" />
			</a>
			<a href="https://vermontcomplexsystems.org/events/cnww/" class="image-item tertiary">
				<img src="{base}/common/thumbnails/screenshots/cnww.png" alt="CNWW" />
			</a>
		</div>
	</div>
</section>

<Divider />

<!-- Slide 3b: Medium Projects -->
<section class="slide slide-three-column column-wide" use:reveal={{ delay: 100  }}>
	<div class="content-section">
        <Label variant="secondary">"6" months projects</Label>
        <p>We collaborate to build reusable software components and infrastructure tailored to your research workflows — helping your group to better work together while ensuring sustainability.</p>
        <ul>
            <li>You might have a project inspired by others’ work that needs <em>new data collection</em> or <em>deployment of online platforms</em> with interactive features.</li>
			<li>We work on developing novel methods to conduct <em>participatory surveys</em>, combining expertise from interactive story telling with qualitative data collection. We have experience sharing and communicating <em>sensitive data</em> while respecting the privacy of individual data.</li> 
            <li>We leverage existing digital infrastructure we've built at VERSO — like research virtual machine and APIs — to avoid reinventing the wheel and accelerate development.</li>
        </ul>
    </div>

	
	<div class="divider-section">
		<div class="vertical-line"></div>
	</div>
	
	<div class="image-section">
		<div class="image-grid">
            <a href="https://wikimedia.uvm.edu/" target="_blank" class="image-item primary">
                <img src="{base}/common/thumbnails/screenshots/wikiwrangler.png" alt="Wiki Wrangler" />
            </a>
			<a href="{base}/open-academic-analytics" target="_blank" class="image-item secondary">
				<img src="{base}/common/thumbnails/screenshots/open-academic-analytics.jpg" alt="Open Academic Analytics Project" />
			</a>
		</div>
	</div>
</section>

<Divider />

<!-- Slide 3c: Long-term Projects -->
<section class="slide slide-three-column column-wide" use:reveal={{ delay: 100  }}>
	<div class="content-section">
	<Label variant="secondary">Longer-term partnerships</Label>
        <p>These are deep collaborations where we anticipate complexity and co-create innovative research tools. While the future is hard to predict, we help you stay on course and avoid costly pitfalls.</p>
        <ul>
            <li><em>Tailored projects</em> that explore new approaches — such as integrating a front-end data interface with a back-end API and database for custom data collection.</li>
            <li>We build <em>robust and secure infrastructure</em> that supports your research not just today, but for years to come — designed with long-term maintenance in mind.</li>
            <li>We offer <em>mentorship</em> in modern software practices, helping your team learn approaches from industry that are rarely taught in academia — improving onboarding, team coordination, and future grant competitiveness.</li>
        </ul>
    </div>

	
	<div class="divider-section">
		<div class="vertical-line"></div>
	</div>
	
	<div class="image-section">
		<div class="image-grid">
			<a href="https://verso-uvm.github.io/Vermont-Livability-Map/" class="image-item primary">
				<img src="{base}/common/thumbnails/screenshots/vermont-livability-map.jpg" alt="Vermont Zoning Atlas" />
			</a>
			<a href="https://catalogresearch.uvm.edu/" target="_blank" rel="noopener" class="image-item secondary">
				<img src="{base}/common/thumbnails/screenshots/explore-the-cat-project.jpg" alt="Explore the Cat Project" />
			</a>
		</div>
	</div>
</section>

<Divider />

<!-- Slide 4: Community -->
<section class="slide slide-two-column slide-community column-wide" use:reveal={{ delay: 100  }}>
	<div class="content-section">
		<Label variant="success">Our community</Label>
        <p>We're not alone, we bring expertise from all over the place.</p>
		<ul>
			<li>
				<a href="https://curioss.org/" target="_blank" rel="noopener noreferrer">
					Community for University and Research Institution OSPOs (CURIOSS)
				</a>
			</li>
			<li>
				<a href="https://numfocus.org/" target="_blank" rel="noopener noreferrer">
					NumFOCUS - Supporting open source scientific computing
				</a>
			</li>
			<li>
				<a href="https://pydata.org/vermont2024/" target="_blank" rel="noopener noreferrer">
					PyData Vermont 2024 Conference
				</a>
			</li>
			<li>
				<a href="https://www.cscce.org/" target="_blank" rel="noopener noreferrer">
					CSCCE - Center for Scientific Collaboration and Community Engagement
				</a>
			</li>
		</ul>	
	</div>
	
	<div class="image-section">
		<div class="image-wrapper">
			<img src="{base}/community-69fc3b40333659ebf12e64e787bf03e4.jpg" alt="community" />
			<div class="copyright">
				<p>
					Project illustration by Scriberia. Used under a CC-BY 4.0 licence. 
					DOI: The Turing Way Community & Scriberia (2024).
				</p>
			</div>
		</div>
	</div>
</section>

<Divider />

<!-- Slide 5: Why Work With Us -->
<section class="slide slide-two-column slide-value-proposition column-wide" use:reveal={{ delay: 100  }}>
	<div class="content-section">
		<Label variant="primary">Why work with us?</Label>
		<ul>
			<li><em>We help you focus on your research.</em> We take care of the software side — clean, reliable, and well-structured — so you can spend more time thinking, writing, and analyzing.</li>
			<li><em>We build tools that last.</em> Our code is tested, documented, and designed to be reused by others in your group or future projects.</li>
			<li><em>We understand how research works.</em> With experience in both the humanities and data science, we can adapt to your methods and support your goals — including writing grants and onboarding collaborators.</li>
			<li><em>We support <s>messiness</s> learning along the way.</em> Whether you're comfortable with code or just starting out, we share practices that can make your work easier and more reproducible.</li>
			<li><em>We’re part of a wider community.</em> We stay connected to open science and research software communities, bringing in ideas and tools that align with academic values.</li>
		</ul>
	</div>
</section>


<style>
	/* ===== GLOBAL STYLES ===== */
	:global(main:has(.column-wide)) {
		max-width: none;    
		padding: 0 !important; /* Remove default padding to let column-screen handle spacing */

	}

	:global(p) {
		line-height: 1.5rem;
	}

	/* ===== SLIDE LAYOUTS ===== */
	.slide {
		padding: 2rem var(--margin-left) 2rem var(--margin-left) !important;
		margin-bottom: 2rem;
		max-width: none !important;
	}

	/* Hero slide layout */
	.slide-hero {
		text-align: left;
		max-width: 800px;
		margin-top: 4rem;
	}

	.slide-hero h1 {
		font-size: 4rem;
	}

	.slide-hero h3 {
		font-size: 1.9rem;
		margin-bottom: 0.1rem;
		font-weight: 500;
		color: #666;
	}

	.author-info {
		display: flex;
		gap: 1rem;
		justify-content: left;
		margin-bottom: 1rem;
	}

	/* Two-column layout */
	.slide-two-column {
		display: grid;
		grid-template-columns: 2fr 1fr;
		gap: 2rem;
		align-items: start;
	}

	/* Three-column layout (content | divider | image) */
	.slide-three-column {
		display: grid;
		grid-template-columns: 2fr auto 1fr;
		gap: 2rem;
		align-items: start;
	}

	/* Community slide specific */
	.slide-community {
		grid-template-columns: 0.7fr 1fr;
	}

	/* ===== CONTENT SECTIONS ===== */
	.content-section {
		padding-right: 1rem;
	}

	.content-section p {
		font-size: 1.2rem;
		line-height: 1.5;
		margin-bottom: 1.5rem;
		color: #666;
	}

	.content-section ul {
		list-style: none;
		padding: 0;
		margin: 0;
	}

	.content-section li {
		margin-bottom: 1rem;
		color: #555;
		position: relative;
		padding-left: 1.5rem;
		font-size: 1.2rem;
		line-height: 1.4;
	}

	.content-section li::before {
		content: "•";
		font-weight: bold;
		position: absolute;
		left: 0;
		font-size: 1.2rem;
	}

	/* ===== IMAGE SECTIONS ===== */
	.image-section {
		display: flex;
		justify-content: center;
		align-items: flex-start;
		padding-top: 1rem;
	}

	.hero-image {
		display: flex;
		justify-content: center;
		align-items: flex-start;
		padding-top: 5rem;
		max-width: 500px;
  		margin-inline: auto;
	}

	/* ===== SIMPLE IMAGE STACKING ===== */
	.image-grid {
		display: grid;
		grid-template-areas: "stack";
		max-width: 320px;
		min-height: 250px;
	}

	.image-item {
		grid-area: stack;
		display: block;
		transition: transform 0.2s ease, z-index 0.2s ease;
		cursor: pointer;
	}

	.image-item img {
		width: 100%;
		height: auto;
		border-radius: 8px;
		box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
		display: block;
		pointer-events: none; /* Let clicks go to the link */
	}

	/* Simple stacking positions - further apart */
	.image-item.primary {
		z-index: 2;
		transform: translateX(-30px) translateY(40px);
	}

	.image-item.secondary {
		z-index: 1;
		transform: translateX(150px) translateY(-30px);
		opacity: 0.85;
	}

	.image-item.tertiary {
		z-index: 1;
		transform: translateX(60px) translateY(30px);
		opacity: 0.9;
	}

	/* Simple hover: just bring to front and scale slightly */
	.image-item.primary:hover {
	    scale: 1.05; /* This won't interfere with transform */
	}
	
    .image-item.secondary:hover {
		scale: 1.05; /* This won't interfere with transform */
	}

    .image-item.tertiary:hover {
		scale: 1.05; /* This won't interfere with transform */
	}


	/* ===== COMMUNITY IMAGE WITH COPYRIGHT ===== */
	.image-wrapper {
		display: flex;
		flex-direction: column;
		align-items: center;
		max-width: 100%;
	}

	.slide-community .image-section img {
		width: 100%;
		min-width: 300px;
		max-width: none;
	}

	.copyright {
		margin-top: 0.75rem;
		max-width: 350px;
		text-align: center;
	}

	.copyright p {
		font-size: 0.75rem;
		line-height: 1.3;
		color: #666;
		margin: 0;
		font-style: normal;
	}

	/* ===== LINK STYLES ===== */
	a {
		color: #667eea;
		text-decoration: none;
		font-weight: 500;
		border-bottom: 2px solid transparent;
		transition: all 0.2s ease;
		display: inline-block;
	}

	/* Special styling for inline content links */
	.content-section a {
		color: #333;
		font-weight: 600;
		text-decoration: underline;
		transition: color 0.2s ease;
	}

	.content-section a:hover {
		color: #666;
	}

	a:active {
		transform: translateY(0);
	}

	a[target="_blank"]::after {
		content: " ↗";
		font-size: 0.8em;
		opacity: 0.7;
		margin-left: 0.2em;
	}

    /* Nested ul styling */
    .content-section ul ul {
        margin-top: 0.5rem;
        margin-left: 1.5rem; /* Indent the entire nested list */
    }

    .content-section ul ul li {
        font-size: 1.0rem;
        margin-bottom: 0.8rem;
        padding-left: 1.8rem; /* Space for the glyph */
    }

    .content-section ul ul li::before {
        content: "▸";
        font-weight: bold;
        position: absolute;
        left: 0;
        font-size: 1rem;
    }

	/* ===== RESPONSIVE DESIGN ===== */
	@media (max-width: 1024px) {
		.slide-two-column,
		.slide-three-column,
		.slide-community {
			grid-template-columns: 1fr;
			gap: 1.5rem;
		}

		.divider-section {
			display: none;
		}

		.image-section {
			order: -1;
			padding-top: 0;
		}

		.hero-image {
			padding-top: 0rem;
		}

		.content-section {
			padding-right: 0;
		}

		.content-section li {
			font-size: 1.05rem;
		}

		/* Simplify stacking on tablets */
		.image-item.primary {
			transform: translateX(15px) translateY(0px);
		}

		.image-item.secondary {
			transform: translateX(-15px) translateY(20px);
		}

		.image-item.tertiary {
			transform: translateX(0px) translateY(25px);
		}
	}

	@media (max-width: 768px) {
		.slide {
			padding: 1rem 2rem 2rem 2rem !important;
		}

		/* Hide author image on mobile */
		.slide-two-column .image-section {
			display: none;
		}

		/* Stack project images below content on mobile */
		.slide-three-column {
			grid-template-columns: 1fr;
			gap: 1.5rem;
		}

		.slide-three-column .image-section {
			order: 2;
			padding-top: 0;
		}

		.slide-three-column .image-grid {
			max-width: 250px;
			margin: 0 auto;
		}

		/* Mobile hero styling */
		.slide-hero {
			margin-top: 1.5rem;
		}

		.slide-hero h1 {
			font-size: 2rem;
		}

		.slide-hero h3 {
			font-size: 1.4rem !important;
		}

		.author-info p {
			font-size: 1.1rem !important;
		}

		/* Keep simple stacking on mobile */
		.image-grid {
			max-width: 280px;
		}

		.image-item.primary {
			transform: translateX(-30px) translateY(30px);
		}

		.image-item.secondary {
			transform: translateX(30px) translateY(-15px);
		}

		.image-item.tertiary {
			transform: translateX(0px) translateY(35px);
		}

		.copyright {
			max-width: 280px;
		}

		.copyright p {
			font-size: 0.7rem;
		}
	}
</style>