<script>
	import { reveal } from 'svelte-reveal';
	import Label from './Label.svelte';
	import { base } from "$app/paths";
</script>

<div class="container">
	<div class="docs" use:reveal={{ delay: 2500 }}>
		<Label>Who am I?</Label>
		<ul>
            <li use:reveal={{ delay: 3000, preset: 'slide', x: -20 }}>Ph.D. in Complex Systems and Data Science at the University of Vermont, but I come from the humanities. </li>
			<li use:reveal={{ delay: 3200, preset: 'fly', y: -20 }}>As a research software engineer, I support groups in adopting <strong >best software practices</strong> in academia. This includes the following:</li>
            <ul>
                    <li use:reveal={{ delay: 3000, preset: 'slide', x: -20 }}>Writing <strong>sustainable code</strong> that can outlive its original author, ensuring long-term viability.</li>
                    <li use:reveal={{ delay: 3200, preset: 'fly', y: -20 }}>Packaging software that it is <strong>adequately tested</strong>, ensuring its epistemic validity.</li>
                    <li use:reveal={{ delay: 3200, preset: 'fly', y: -20 }}><strong>Promoting community practices</strong> that bridge industry insights with academic expertise in managing complex, computational projects</li>
            </ul>	
			<li use:reveal={{ delay: 3400, preset: 'slide', x: -20 }}>As someone from the humanities, I am working towards promoting software practices to diverse groups and individuals who do not see themselves as coders</li>
		</ul>	
	</div>
	
	<div class="image-container" use:reveal={{ delay: 3600, preset: 'scale', scale: 0.5 }}>
		<a href="{base}/author/jonathan-st-onge">
		<img src="{base}/common/assets/authors/jso.jpg" alt="Jonathan St-Onge" />
		</a>
	</div>
</div>

<style>
	.container {
		display: grid;
		grid-template-columns: 2fr 1fr;
		gap: 2rem;
		align-items: start;
	}
	
	.docs {
		display: block;
		padding-bottom: 1rem;
	}
	
	.image-container {
		display: flex;
		justify-content: center;
		align-items: flex-start;
		padding-top: 2rem;
	}
	
	img {
		max-width: 100%;
		height: auto;
		border-radius: 8px;
		box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
	}
	
	li {
		line-height: 1.5;
		margin-bottom: 0.5rem;
	}
	
	a {
		text-decoration: underline;
	}
	
	/* Responsive design */
	@media (max-width: 768px) {
		.container {
			grid-template-columns: 1fr;
			gap: 1rem;
		}
		
		.image-container {
			order: -1; /* Put image on top on mobile */
			padding-top: 0;
		}

	}
</style>