<script>
	import Label from './Label.svelte';
	import { base } from "$app/paths";
	import Divider from './Divider.svelte';
</script>

<!-- Slide 1: Title -->
<section class="slide slide-title">
	<h1>How to work with us!</h1>
	<h3>Lets work together to write sustainable and reproducible software.</h3>
	<div class="author-info">
		<p>Jonathan St-Onge</p>
		<p>07.08.2025</p>
	</div>
</section>

<Divider />

<!-- Slide 2: Who am I -->
<section class="slide slide-two-column">
	<div class="content-section">
	<Label>Who am I?</Label>
        <ul>
            <li>Ph.D. in Complex Systems and Data Science at the University of Vermont — with roots in the humanities, which gives me a unique perspective on interdisciplinary collaboration.</li>
            <li>As a research software engineer, I help research groups accelerate and strengthen their work by adopting <strong>best software practices</strong> in academia, including:</li>
            <ul>
                <li>Writing <strong>sustainable code</strong> that can outlive its original author — reducing technical debt and enabling long-term research continuity.</li>
                <li>Packaging software that is <strong>adequately tested</strong>, increasing its epistemic reliability and reproducibility.</li>
                <li><strong>Promoting community practices</strong> that bridge industry standards with academic workflows — improving team collaboration, onboarding, and project management.</li>
            </ul>	
            <li>Thanks to my humanities background, I’m well-equipped to write grants, collaborate across disciplines, and support diverse teams — especially those new to coding or computational tools.</li>
        </ul>	
    </div>

	
	<div class="image-section">
		<a href="{base}/author/jonathan-st-onge">
			<img src="{base}/common/assets/authors/jso.jpg" alt="Jonathan St-Onge" />
		</a>
	</div>
</section>

<Divider />

<!-- Slide 3a: Short Projects -->
<section class="slide slide-three-column">
	<div class="content-section">
        <Label variant="secondary">"1-2" months projects</Label>
        <p>We can write code to help you accomplish specific research tasks — fast. These are short, high-impact collaborations that can be funded through fee-for-service mechanisms or grants.</p>
        <ul>
		    <li>Projects with <strong>clear, established goals</strong>, where the path to delivery is well defined.</li>
            <li>We have <strong>prior experience</strong> with similar open-source tools, so we can deliver quickly and reliably, <em>ceteris paribus</em>.</li>
            <li>Often, <strong>the data is familiar</strong> territory — data you already collected and understand, making the collaboration efficient and low-risk.</li>
            <li>Typical outcomes include interactive dashboards, lightweight web tools, or storytelling components that help share key findings with the broader public or stakeholders.</li>
        </ul>
    </div>
	
	<div class="divider-section">
		<div class="vertical-line"></div>
	</div>
	
	<div class="image-section">
		<div class="image-grid">
			<a href="{base}/networks-fast-and-slow" class="image-item primary">
				<img src="{base}/common/thumbnails/screenshots/networks-fast-and-slow.jpg" alt="Networks Fast and Slow Project" />
			</a>
			<a href="{base}/allotax-scrolly" class="image-item secondary">
				<img src="{base}/common/thumbnails/screenshots/allotax-scrolly.jpg" alt="Allotax Scrolly Project" />
			</a>
		</div>
	</div>
</section>

<Divider />

<!-- Slide 3b: Medium Projects -->
<section class="slide slide-three-column">
	<div class="content-section">
        <Label variant="secondary">"6" months projects</Label>
        <p>We collaborate to build reusable software components and infrastructure tailored to your research workflows — helping your group move faster while ensuring sustainability.</p>
        <ul>
            <li>You might have a project inspired by others’ work that needs <strong>new data collection</strong> or <strong>deployment of online platforms</strong> with interactive features.</li>
            <li>Together, we <strong>adopt sustainable software practices from the outset</strong>, improving reproducibility and reducing technical debts later on.</li>
            <li>We leverage existing infrastructure we've built at VERSO — like virtual machines and APIs — to avoid reinventing the wheel and accelerate development.</li>
        </ul>
    </div>

	
	<div class="divider-section">
		<div class="vertical-line"></div>
	</div>
	
	<div class="image-section">
		<div class="image-grid">
            <a href="https://verso-uvm.github.io/Vermont-Livability-Map/" target="_blank" class="image-item primary">
                <img src="{base}/common/thumbnails/screenshots/vermont-livability-map.jpg" alt="Vermont Livability Map" />
            </a>
			<a href="{base}/open-academic-analytics" target="_blank" class="image-item secondary">
				<img src="{base}/common/thumbnails/screenshots/open-academic-analytics.jpg" alt="Open Academic Analytics Project" />
			</a>
		</div>
	</div>
</section>

<Divider />

<!-- Slide 3c: Long-term Projects -->
<section class="slide slide-three-column">
	<div class="content-section">
	<Label variant="secondary">Longer-term partnerships</Label>
        <p>These are deep collaborations where we anticipate complexity and co-create innovative research tools. While the future is hard to predict, our experienced team helps you stay on course and avoid costly pitfalls.</p>
        <ul>
            <li><strong>Tailored projects</strong> that explore new approaches — such as integrating a front-end data interface with a back-end API and database for custom data collection.</li>
            <li>We build <strong>robust and secure infrastructure</strong> that supports your research not just today, but for years to come — designed with long-term maintenance in mind.</li>
            <li>We offer <strong>mentorship</strong> in modern software practices, helping your team learn approaches from industry that are rarely taught in academia — improving onboarding, team coordination, and future grant competitiveness.</li>
        </ul>
    </div>

	
	<div class="divider-section">
		<div class="vertical-line"></div>
	</div>
	
	<div class="image-section">
		<a href="https://catalogresearch.uvm.edu/" target="_blank" rel="noopener" class="single-image">
			<img src="{base}/common/thumbnails/screenshots/explore-the-cat-project.jpg" alt="Explore the Cat Project" />
		</a>
	</div>
</section>

<Divider />

<!-- Slide 4: Community -->
<section class="slide slide-two-column slide-community">
	<div class="content-section">
		<Label variant="success">Our community</Label>
        <p>We're not alone, we bring expertise form all over the places.</p>
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
<section class="slide slide-two-column slide-value-proposition">
	<div class="content-section">
		<Label variant="primary">Why work with us?</Label>
		<ul>
			<li><strong>We help you focus on your research.</strong> We take care of the software side — clean, reliable, and well-structured — so you can spend more time thinking, writing, and analyzing.</li>
			<li><strong>We build tools that last.</strong> Our code is tested, documented, and designed to be reused by others in your group or future projects.</li>
			<li><strong>We understand how research works.</strong> With experience in both the humanities and data science, we can adapt to your methods and support your goals — including writing grants and onboarding collaborators.</li>
			<li><strong>We support <s>messiness</s> learning along the way.</strong> Whether you're comfortable with code or just starting out, we share practices that can make your work easier and more reproducible.</li>
			<li><strong>We’re part of a wider community.</strong> We stay connected to open science and research software communities, bringing in ideas and tools that align with academic values.</li>
		</ul>
	</div>
</section>



<style>
	/* ===== GLOBAL STYLES ===== */
	:global(p) {
		line-height: 1.5rem;
	}

	/* ===== SLIDE LAYOUTS ===== */
	.slide {
		padding-bottom: 2rem;
		margin-bottom: 2rem;
	}

	/* Title slide layout */
	.slide-title {
		text-align: left;
		max-width: 800px;
	}

	.slide-title h1 {
		font-size: 4rem;
	}

	.slide-title h3 {
		font-size: 1.5rem;
		margin-bottom: 0.1rem;
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
		font-size: 1rem;
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

	/* Simple stacking positions */
	.image-item.primary {
		z-index: 2;
		transform: translateX(-40px) translateY(20px);
	}

	.image-item.secondary {
		z-index: 1;
		transform: translateX(150px) translateY(-20px);
		opacity: 0.85;
	}

	/* Simple hover: just bring to front and scale slightly */
	.image-item.primary:hover {
	    scale: 1.05; /* This won't interfere with transform */
	}
	
    .image-item.secondary:hover {
		scale: 1.05; /* This won't interfere with transform */
	}

	/* Single image (for long-term projects) */
	.single-image {
		display: block;
		transition: transform 0.2s ease;
	}

	.single-image img {
		width: 100%;
		max-width: 300px;
		height: auto;
		border-radius: 8px;
		box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
	}

	.single-image:hover {
		transform: scale(1.05);
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
        font-size: 0.9rem;
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

		.content-section {
			padding-right: 0;
		}

		/* Simplify stacking on tablets */
		.image-item.primary {
			transform: translateX(15px) translateY(0px);
		}

		.image-item.secondary {
			transform: translateX(-15px) translateY(20px);
		}
	}

	@media (max-width: 768px) {
		.slide-title h1 {
			font-size: 2rem;
		}

		.slide-title h3 {
			font-size: 1.25rem;
		}

		.author-info {
			flex-direction: column;
			gap: 0.5rem;
		}

		/* Keep simple stacking on mobile */
		.image-grid {
			max-width: 280px;
		}

		.image-item.primary {
			transform: translateX(10px) translateY(0px);
		}

		.image-item.secondary {
			transform: translateX(-10px) translateY(15px);
		}

		.copyright {
			max-width: 280px;
		}

		.copyright p {
			font-size: 0.7rem;
		}
	}
</style>