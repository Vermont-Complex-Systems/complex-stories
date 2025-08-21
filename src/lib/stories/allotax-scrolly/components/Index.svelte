<script>
    import * as d3 from "d3";
    import { base } from "$app/paths";
    import { fade, fly } from 'svelte/transition';
    import { innerWidth } from 'svelte/reactivity/window';
    import { Diamond, Legend, DivergingBarChart, Dashboard } from 'allotaxonometer-ui';
    import { combElems, rank_turbulence_divergence, diamond_count, wordShift_dat, balanceDat } from 'allotaxonometer-ui';
    
    import BarChartRank from './BarChartRank.svelte';

    import Slider from './Slider.svelte';
    import Nav from './Nav.svelte';
    
    import boys1980 from '../data/boys-qc-1980.json';
    import boys2023 from '../data/boys-qc-2023.json';
    import girls1980 from '../data/girls-qc-1980.json';
    import girls2023 from '../data/girls-qc-2023.json';
    
    // Create data object for easy switching
    const datasets = {
        girls: {
            sys1: girls1980,
            sys2: girls2023,
            title: ['Girls 1980', 'Girls 2023']
        },
        boys: {
            sys1: boys1980,
            sys2: boys2023,
            title: ['Boys 1980', 'Boys 2023']
        }
    };

    import Scrolly from '$lib/components/helpers/Scrolly.svelte';
    import ScrollyMd from './ScrollyMarkdown.svelte'; // New import
    import Md from '$lib/components/helpers/MarkdownRenderer.svelte';
    
    let { story, data } = $props();
    
    let scrollyIndex = $state();
	
	const steps = data.steps;

    let isDark = $state(false);
    let isGirls = $state(true);

    // Data systems
    let currentDataset = $derived(isGirls ? datasets.girls : datasets.boys);
    let sys1 = $derived(currentDataset.sys1);
    let sys2 = $derived(currentDataset.sys2);
    let title = $derived(currentDataset.title);
    
    let alpha = $state(0.58);
    const alphas = d3.range(0,18).map(v => +(v/12).toFixed(2)).concat([1, 2, 5, Infinity]);
    let alphaIndex = $state(7); // Start at 0.58
    
    let DiamondHeight = 600;
    let DiamondWidth = DiamondHeight;
    let marginInner = 160;
    let marginDiamond = 40;
    let max_shift = $derived(barData.length > 0 ? d3.max(barData, d => Math.abs(d.metric)) : 1);
    
    let me = $derived(sys1 && sys2 ? combElems(sys1, sys2) : null);
    let rtd = $derived(me ? rank_turbulence_divergence(me, alpha) : null);
    let dat = $derived(me && rtd ? diamond_count(me, rtd) : null);
    
    let barData = $derived(me && dat ? wordShift_dat(me, dat).slice(0, 30) : []);
    let balanceData = $derived(sys1 && sys2 ? balanceDat(sys1, sys2) : []);
    let maxlog10 = $derived(me ? Math.ceil(d3.max([Math.log10(d3.max(me[0].ranks)), Math.log10(d3.max(me[1].ranks))])) : 0);
    let max_count_log = $derived(dat ? Math.ceil(Math.log10(d3.max(dat.counts, d => d.value))) + 1 : 2);
    let isDataReady = $derived(dat && barData && balanceData && me && rtd);

    $effect(() => { 
        alpha = alphas[alphaIndex]; }
    );

    // Track scrolly progress to distinguish entering vs leaving the section
    let maxStepReached = $state(0);
    let hasStartedScrolly = $derived(maxStepReached > 0);

    $effect(() => {
        if (scrollyIndex !== undefined) {
            maxStepReached = Math.max(maxStepReached, scrollyIndex);
        }
    });

    let delta_sum = $derived(d3.sum(dat.deltas.map(d => +d)).toFixed(3));
    let math = $derived(`$D_{\\alpha}^R (\\Omega_1 || \\Omega_2 = ${delta_sum})$\n$\\propto \\sum_\\tau | \\frac{1}{r_{\\tau,1}^{${alpha == 'Infinity' ? '\\infty' : alpha}}} - \\frac{1}{r_{\\tau,2}^{${alpha == 'Infinity' ? '\\infty' : alpha}}} |$`);

    // Determine effective step: distinguish between entering (start at 0) vs leaving (keep final state)
    let effectiveStep = $derived(
        scrollyIndex !== undefined 
            ? scrollyIndex  // We're in the scrolly section - use actual step
            : hasStartedScrolly 
                ? maxStepReached  // We've left the scrolly section - maintain final state
                : 0  // We're entering the scrolly section - start at step 0
    );

    // Update your renderedData to use effectiveStep:
    let renderedData = $derived.by(() => {
        if (!dat || !barData) return null;
        
        switch (effectiveStep) {
            case 0:
                return {
                    ...dat,
                    counts: dat.counts.map(d => ({
                        ...d,
                        x1: Math.ceil(d.coord_on_diag),
                        y1: Math.ceil(d.coord_on_diag),
                        types: ""
                    }))
                };
                
            case 1:
                return {
                    ...dat,
                    counts: dat.counts.map(d => ({
                        ...d,
                        x1: d.which_sys === "right" ? Math.ceil(d.coord_on_diag) : d.x1,
                        y1: d.which_sys === "right" ? Math.ceil(d.coord_on_diag) : d.y1,
                        types: d.which_sys === "right" ? "" : d.types,
                        value: d.which_sys === "right" ? 0 : d.value
                    }))
                };
                
            default: // case 2 and beyond
                return dat;
        }
    });

</script>

{#snippet G(text)}
    <span class="gender-text" class:girls={isGirls} class:boys={!isGirls}>
        {text}
    </span>
{/snippet}


<Nav bind:isDark bind:isGirls />


<section id="story"  class="story">
    <h1>A whirlwind tour of the <a href="https://vermont-complex-systems.github.io/complex-stories/allotaxonometry" target="_blank">allotaxonometer</a></h1>
    <div class="article-meta">
        <p class="author">By <a href="{base}/author/jonathan-st-onge">Jonathan St-Onge</a></p>
        <p class="date">June 23, 2025</p>
    </div>

    <p>Every year in Quebec, the newspaper <em>La Presse</em> does a <a href="https://www.lapresse.ca/societe/2025-06-22/palmares-des-prenoms/pres-d-un-demi-siecle-en-modes-et-tendances.php">short analysis</a> of baby name dynamics. On June 22nd, they examined the trend of 433,000 unique baby names Quebecers have given to their children, over 4.1 million births since <span class="year-1980">1980</span>. They found that Emma hit first place in <span class="year-2023">2023</span>, while Noah stayed at the top for the fourth consecutive year. Some names have made a comeback, such as <em>Charlie</em>, a popular name in the 2000s that lost ground in the 2010s, before making a comeback between 2018 and 2023.</p>
    
    <p>Here is the ranking of the {@render G(isGirls ? 'girl' : 'boy')} baby names in <span class="year-1980">1980</span>:</p>
    
    <div class="initial-chart">
        <BarChartRank data={sys1.slice(0, 30)} fill={"#a6a6a6"} />
    </div>
    
    <p>Here is the ranking for {@render G(isGirls ? 'girl' : 'boy')} baby names in Quebec for <span class="year-2023">2023</span>:</p>

    <div class="initial-chart">
        <BarChartRank data={sys2.slice(0, 30)} fill={"#c3e6f3e6"} />
    </div>
    
    <p>I really like this analysis, but there are some limitations in comparing ranks using raw counts, especially when it comes to systems that are known to be "heavy-tailed". That is, when a few names, or types, occur many more times in your dataset than less frequent ones, aka the tail. For instance, in the analysis the author compares baby names between "then and now". By just looking at raw counts, we are stuck with such comparisons where top-ranking baby names in <span class="year-1980">1980</span> might now be in the tail, which is a bit underwhelming. How can we know about the most surprising comparisons, given the heavy-tailed distribution?</p>

    <p>Allotaxonometer provides a systematic way to analyze these shifts using <a href="https://arxiv.org/abs/2008.13078">divergence metrics</a>.</p>

    <div class="chart-container-scrolly">
        {#if isDataReady && renderedData}
            <div class="visualization-container">
                <!-- Diamond plot: show for steps 0, 1, 2 (including undefined as 0) -->
                {#if effectiveStep >= 0}
                <div class="diamondplot">
                    <Diamond
                        dat={renderedData} 
                        {alpha} 
                        divnorm={rtd.normalization} 
                        {title} 
                        {maxlog10}
                        {DiamondHeight} 
                        {marginInner} 
                        {marginDiamond}
                    />
                </div>
                {/if}
                
                <!-- Additional charts: show from step 1 onwards (no upper limit) -->
                {#if effectiveStep >= 1}
                    <div class="additional-charts" 
                        in:fade={{ duration: 800, delay: 300 }}
                    >
                        <div class="legend-container" 
                            in:fly={{ x: -50, duration: 600, delay: 500 }}>
                            <Legend
                                diamond_dat={dat.counts}
                                DiamondHeight={DiamondHeight}
                                max_count_log={max_count_log || 5}
                            />
                        </div>
                        
                        <!-- Balance chart: visible from step 2 onwards -->
                        <div class="balance-container" style="opacity: {effectiveStep >= 2 ? 1 : 0};">
                            <DivergingBarChart
                                data={balanceData}
                                DiamondHeight={DiamondHeight}
                                DiamondWidth={DiamondWidth}
                            />
                        </div>
                    </div>
                {/if}
            </div>
        {/if}
    </div>


    <div class="spacer"></div>
    <Scrolly bind:value={scrollyIndex} offset={innerWidth.current > 1200 ? '50vh' : '20vh'}>
        {#each steps as text, i}
            {@const active = scrollyIndex === i}
            <div class="step" class:active>
                <p> 
                    <ScrollyMd text={text.value} {isGirls} />
                </p>
            </div>
        {/each}
    </Scrolly>
    <div class="spacer"></div>
</section>

<section>
    <h1>The full picture</h1>
    <p>We now add the final chart to our canvas, the wordshift plot, with our divergence metric of choice, the rank-turbulence divergence. The wordshift plot shows a more direct view of how baby names shift across pairs of systems, with the rank being shown in pale grey. For instance, {@render G(isGirls ? 'Florence' : 'Noah')} going from the {isGirls ? '409' : '855'} rank in <span class="year-1980">1980</span> to {isGirls ? '1.5' : '1'} in <span class="year-2023">2023</span>.</p>
    <div class="dashboard-section">
    <div class="dashboard-container">
        <div class="math-overlay">
            <Md text={math} />
        </div>
        
        <Dashboard 
            {dat}
            {alpha}
            divnorm={rtd?.normalization || 1}
            {barData}
            {balanceData}
            {title}
            {maxlog10}
            {max_count_log}
            width={Math.min(innerWidth.current - 40, 1400)} 
            {DiamondHeight}
            {DiamondWidth}
            {marginInner}
            {marginDiamond}
            xDomain={[-max_shift * 1.5, max_shift * 1.5]}
            class="dashboard"
        />
    </div>
    <Slider bind:alphaIndex {alphas} />
</div>

    
<p>Where the α parameter lets us tweak the relative importance of the divergence metric, as shown in the top left expression. Try α = ∞, you will see that types tend to be similarly ranked with their frequency, with {@render G(isGirls ? 'Julie' : 'Eric')} at the top. By contrast, α = 0 allows us to inspect what is happening further down in the tail. Finally, those contour lines underlying the diamond plot help guide our interpretation of the rank-divergence metric, tracking how α is varied.</p>

<p>For much more detail about this tool, see the foundational <a href="https://epjdatascience.springeropen.com/articles/10.1140/epjds/s13688-023-00400-x">paper</a>. To try the tool with your own dataset, visit our <a href="{base}/allotaxonometry">web app</a>. If you are more of a coder, you might enjoy our <a href="https://github.com/car-d00r/py-allotax">Python version</a>.</p>

</section>

<section id="appendix">
    <em>Appendix: Data can be found <a href="https://www.donneesquebec.ca/recherche/dataset/banque-de-prenoms-garcons/resource/c35c6bc3-fbc1-47bd-bfa9-90be087f954a">here</a>, La Presse trend analysis can be found <a href="https://www.lapresse.ca/societe/2025-06-22/palmares-des-prenoms/pres-d-un-demi-siecle-en-modes-et-tendances.php">here</a>. </em>
</section>


<style>
    .article-meta {
        margin: -1rem 0 2rem 0; /* Negative margin to pull closer to title */
        font-family: var(--sans);
    }

    .article-meta .author {
        font-size: var(--font-size-medium);
        color: var(--color-secondary-gray);
        margin: 0 0 0.25rem 0;
        font-weight: 500;
    }

    .article-meta .date {
        font-size: var(--font-size-small);
        color: var(--color-tertiary-gray);
        margin: 0;
        font-weight: 400;
    }

    /* Sticky container for the toggle */
.year-1980,
.year-2023,
.gender-text {
        font-weight: 600;
        text-decoration: underline;
        text-decoration-thickness: 2px;
        text-underline-offset: 3px;
        transition: all 300ms cubic-bezier(0.4, 0, 0.2, 1);
        padding: 0.1rem 0.2rem;
        border-radius: 0.25rem;
    }

    .gender-text.girls {
        color: #be185d; /* Dark pink */
        text-decoration-color: #ec4899; /* Lighter pink underline */
        background: rgba(236, 72, 153, 0.1); /* Very light pink background */
    }

    .gender-text.boys {
        color: #1e40af; /* Dark blue */
        text-decoration-color: #3b82f6; /* Lighter blue underline */
        background: rgba(59, 130, 246, 0.1); /* Very light blue background */
    }


     /* Year highlighting */
    .year-1980 {
        background: rgb(230, 230, 230);
        color: #374151;
        text-decoration-color: rgb(148, 148, 148);
    }
    
    .year-2023 {
        background: rgb(195, 230, 243);
        color: #374151;
        border-radius: 0.3rem;
        text-decoration-color: rgb(129, 208, 237); /* Lighter blue underline */
    }

     :global(#story) {
        max-width: 1200px;
        margin: 2rem auto;
        padding: 0 2rem;
    }

    section h1 {
        font-size: var(--font-size-xlarge);
        margin: 2rem 0 3rem 0;
        text-align: left;
        font-family: var(--serif);
    }

    section h1 a {
            font-family: var(--mono);
        }

	section p {
      font-size: 22px;
      max-width: 800px;
      line-height: 1.3;
      margin: 1rem 0 1rem 0;
  }


    .initial-chart {
        margin-top: 2rem; /* Add more space above charts */
        margin-bottom: 2rem; /* And below charts */
    }

	/* Keep only the first section's scrolly styles */

	.chart-container-scrolly {
        margin-top:  3rem;
        width: 40%;
        position: sticky;
        top: calc(50vh - 350px);
        float: right;
        margin-right: 5%;
        clear: both;
    }

	 .visualization-container {
        display: flex;
        flex-direction: column;
        gap: 1rem;
        /* Don't constrain the width - let it be natural */
    }

	.diamondplot {
        flex: 0 0 auto;
        display: flex;
        justify-content: center;
        align-items: center;
        
        /* Ensure the Diamond has enough space */
        min-width: 600px; /* Match your DiamondHeight */
        min-height: 600px;
    }

	.additional-charts {
        display: flex;
        gap: 15rem; /* Your preferred spacing */
        margin-left: 12rem; /* Your preferred positioning */
        justify-content: center;
        margin-top: 2rem;
        flex: 0 0 auto;
    }

	/* Keep the rest of your styles the same */
    .legend-container {
        flex: 0 0 auto;
        display: flex;
        justify-content: center;
        align-items: flex-start;
    }

    .balance-container {
        flex: 0 0 auto;
        display: flex;
        justify-content: center;
        align-items: flex-start;
        transition: opacity 600ms ease;
    }
    
	/* Scoped CSS transitions - only for diamond plot */
    .diamondplot :global(rect),
    .diamondplot :global(text) {
        transition: 700ms cubic-bezier(0.76, 0, 0.24, 1);
    }

	
    .diamondplot :global(rect) {
		transition: 
			x 700ms cubic-bezier(0.76, 0, 0.24, 1), 
			y 700ms cubic-bezier(0.76, 0, 0.24, 1),
			fill 700ms cubic-bezier(0.76, 0, 0.24, 1),
			width 700ms cubic-bezier(0.76, 0, 0.24, 1),
			height 700ms cubic-bezier(0.76, 0, 0.24, 1),
			opacity 700ms cubic-bezier(0.76, 0, 0.24, 1);
	}

	.diamondplot :global(text) {
		transition: 
			x 700ms cubic-bezier(0.76, 0, 0.24, 1), 
			y 700ms cubic-bezier(0.76, 0, 0.24, 1),
			opacity 700ms cubic-bezier(0.76, 0, 0.24, 1);
	}

	.spacer {
		height: 75vh;
	}

	 .step {
        height: 80vh;
        display: flex;
        place-items: center;
        justify-content: flex-start; /* Align to left */
        margin-right: 60%;
    }


	.step p {
        padding: 0.5rem 1rem;
        background: var(--step-bg, #f5f5f5);
        color: var(--step-text, #ccc);
        border-radius: 5px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        box-shadow: var(--step-shadow, 1px 1px 10px rgba(0, 0, 0, 0.2));
        z-index: 10;
        transition: background 500ms ease, color 500ms ease, box-shadow 500ms ease;
    }

    
    .step.active p {
        background: var(--step-active-bg, white);
        color: var(--step-active-text, black);
        box-shadow: var(--step-active-shadow, 1px 1px 10px rgba(0, 0, 0, 0.2));
    }
    
    /* Dark mode overrides */
    :global(.dark) .step p {
        --step-bg: #2a2a2a;
        --step-text: #888;
        --step-shadow: 1px 1px 10px rgba(227, 227, 227, 0.5);
    }

    :global(.dark) .step.active p {
        --step-active-bg: #383838;
        --step-active-text: #fff;
        --step-active-shadow: 1px 1px 10px rgba(230, 230, 230, 0.5);
    }

    /* Dark mode support */
    :global(.dark) .gender-text.girls {
        color: #fbb6ce;
        background: rgba(236, 72, 153, 0.2);
    }

    :global(.dark) .gender-text.boys {
        color: #93c5fd;
        background: rgba(59, 130, 246, 0.2);
    }
    
    .math-overlay {
        position: absolute;
        top: 5rem;
        left: 3rem;
        z-index: 10;
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        padding: 0 0;
        border-radius: 0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(0, 0, 0, 0.05);
        max-width: 200px; /* Constrain overlay width */
        overflow: hidden; /* Prevent overflow */
        line-height: 1.2; /* Tighter line spacing for math */
    }

    .math-overlay :global(.markdown-content) {
        font-size: 1.2rem;
        margin: 0;
    }

    .math-overlay :global(.katex) {
        font-size: 0.9em !important;
    }

	@media (max-width: 1200px) {
        section {
            padding: 0 1rem; /* Less side padding */
        }

        section p {
            font-size: 18px; /* Smaller text */
            max-width: none;
        }

        .chart-container-scrolly {
            position: sticky;
            top: calc(50vh - 200px); /* Less aggressive positioning */
            width: 100%;
            max-width: 600px;
            margin: 2rem auto; /* Center it, not right-aligned */
            display: flex;
            justify-content: center;
            align-items: center;
        }

        .additional-charts {
            flex-direction: column;
            gap: 1rem; /* Much smaller gap */
            margin-left: 0; /* Remove the 12rem offset */
            align-items: center;
        }

        .step p {
            width: 100%;
            max-width: 600px;
            margin: 0 auto;
            text-align: center;
            transform: none; /* Remove the translateX offset */
        }
    }

    /* Add extra small screen support */
    @media (max-width: 768px) {

        section h1 {
            font-size: var(--font-size-xlarge); 
        }
        
        section h1 a {
               font-size: var(--font-size-large);
               font-family: var(--mono);
        }
        
        .initial-chart {
            margin: 1.5rem 0; /* Tighter spacing */
        }
        
        .chart-container-scrolly {
            top: calc(50vh - 150px); /* Even less aggressive */
            max-width: 90vw; /* Use more screen width */
        }
        
        section p {
            font-size: 16px; /* Even smaller text */
            line-height: 1.4; /* Better readability */
        }
    }

    /* Dashboard section styles */
    section:has(.dashboard-section) {
        max-width: 100vw;
        margin: 0;
        padding: 0;
        width: 100%;
    }

    .dashboard-section {
        width: 100vw;
        margin-left: calc(-50vw + 50%);
        padding: 4rem 0 0 8rem;
        text-align: center;
    }

     .dashboard-container {
        width: 100%;
        display: flex;
        justify-content: center;
        padding: 1rem 0;
        position: relative;
        max-width: 1400px; /* Constrain dashboard container */
        margin: 0 auto; /* Center it */
    }
</style>