<script>
    import * as d3 from "d3";
    import { base } from "$app/paths";
    import { fade, fly } from 'svelte/transition';
    import ThemeToggle from './ThemeToggle.svelte';

    import { innerWidth } from 'svelte/reactivity/window';
    import { Diamond, Legend, DivergingBarChart, Dashboard } from 'allotaxonometer-ui';
    import { combElems, rank_turbulence_divergence, diamond_count, wordShift_dat, balanceDat } from 'allotaxonometer-ui';
    import BarChartRank from './BarChartRank.svelte';
    import Slider from './Slider.svelte';

    import boys1895 from '../data/boys-1895.json';
    import boys1968 from '../data/boys-1968.json';
    
    import Scrolly from '$lib/components/helpers/Scrolly.svelte';
    import Md from '$lib/components/helpers/MarkdownRenderer.svelte';
    
    let { story, data } = $props();
    
    let scrollyIndex = $state();
	
	const steps = data.steps;
    let isDarkMode = $state(false);

    // Data systems
    let sys1 = $state(boys1895);
    let sys2 = $state(boys1968);
    let title = $state(['Boys 1895', 'Boys 1968']);
    
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

    $effect(() => { alpha = alphas[alphaIndex]; });

     // Use $derived instead of $effect for state synchronization
    let renderedData = $derived.by(() => {
        if (!dat || !barData) return null;
            
        // Treat undefined scrollyIndex as step 0 (initial state)
        const currentStep = scrollyIndex ?? 0;
        
        switch (currentStep) {
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
                
            case 2:
                return dat;
                
            default:
                return null;
        }
    });

    $inspect(scrollyIndex)
</script>

<div class="sticky-header">
    <div class="header-controls">
        <div class="logo-container">
            <a href="{base}/" class="logo-link">
                <img src="{base}/octopus-swim-left.png" alt="Home" class="logo" />
            </a>
        </div>
        
        <ThemeToggle bind:isDarkMode />
    </div>
</div>



<section>
    <h1>A whirlwind tour of the <a href="https://vermont-complex-systems.github.io/complex-stories/allotaxonometry" target="_blank">allotaxonometer</a></h1>

    <p>Here is the rank of the baby names for boys in 1895:</p>
    <div class="initial-chart">
        <BarChartRank data={sys1.slice(0, 30)} fill={"#a6a6a6"} />
    </div>
    
    <p>Here is the ranking for boy baby names in the US for 1968:</p>
    <div class="initial-chart">
        <BarChartRank data={sys2.slice(0, 30)} fill={"#c3e6f3e6"} />
    </div>
    
    <p>
        If you wanted to compare which baby name got more popular over time, how would you do it? 
        You can say that John is more popular than James within 1895, and that John lost its first rank in favor of Michael in 1968. Then what? What about the less frequent names in the tail of the distribution, how can we asses there growth over time, even though the distribution is dominated by a few very popular name? The Allotaxonometer provides a systematic way to analyze these shifts.
    </p>


    <div class="chart-container-scrolly">
        {#if isDataReady && renderedData}
            <div class="visualization-container">
                <!-- Diamond plot: show for steps 0, 1, 2 (including undefined as 0) -->
                {#if (scrollyIndex ?? 0) >= 0 && (scrollyIndex ?? 0) <= 2}
                <div class="diamondplot" out:fly={{ y: -50, duration: 800 }}>
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
                
                <!-- Additional charts: show for steps 1, 2 -->
                {#if (scrollyIndex ?? 0) >= 1 && (scrollyIndex ?? 0) <= 2}
                    <div class="additional-charts" 
                        in:fade={{ duration: 800, delay: 300 }}
                    >
                        <div class="legend-container" 
                            in:fly={{ x: -50, duration: 600, delay: 500 }}
                            out:fly={{  x: -50, duration: 800, delay: 300 }}>
                            <Legend
                                diamond_dat={dat.counts}
                                DiamondHeight={DiamondHeight}
                                max_count_log={max_count_log || 5}
                            />
                        </div>
                        
                        <!-- Balance chart: always present for positioning, but opacity controlled -->
                        <div class="balance-container" style="opacity: {(scrollyIndex ?? 0) >= 2 ? 1 : 0};">
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
                    <Md text={"Step: " + i + " " + text.value}/>
                </p>
            </div>
        {/each}
    </Scrolly>
    <div class="spacer"></div>
</section>

<section>
    <h1>The full picture</h1>
    <p>We now add the wordshift plot, which allows us to have a more direct view of how types shift across pairs of systems. </p>
    <div class="dashboard-section">
        <div class="dashboard-container">
            <Dashboard 
                {dat}
                {alpha}
                divnorm={rtd?.normalization || 1}
                {barData}
                {balanceData}
                {title}
                {maxlog10}
                {max_count_log}
                width={innerWidth.current - 40}
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
    
<p>We also show how the α parameter let us tweak the relative importance of the divergence metric. Try α = ∞, you will see that types tend to be correlated with their frequency, with Michael at the top. By contrast, α = 0 allow us to inspect what is happenning further down in the tail. We also finally learn what those contour lines mean! </p>
</section>


<style>
    .sticky-header :global(button) {
        background: transparent !important;
        color: var(--dash-text-primary) !important;
        border: 1px solid var(--dash-border-color) !important;
        padding: 0.5rem !important;
    }

    .sticky-header :global(button:hover) {
        background: var(--dash-bg-secondary) !important;
    }

    .sticky-header {
        position: sticky;
        top: 0;
        left: 0;
        right: 0;
        z-index: 1000;
        pointer-events: none;
        width: 100vw; /* Full viewport width */
        margin-left: calc(-50vw + 50%); /* Break out of any container */
        height: auto; /* Let content determine height */
    }

    .header-controls {
        display: flex;
        justify-content: flex-end;
        align-items: center;
        gap: 1rem;
        pointer-events: auto;
        padding: 1rem 3.4rem 1rem 1rem;
        width: 100%;
        /* Removed absolute positioning */
    }

    .logo-container {
        max-width: 250px;
        transition: transform var(--transition-medium) ease;
        flex-shrink: 0; /* Prevent logo from shrinking */
    }

    .logo-container:hover {
        transform: rotate(var(--left-tilt)) scale(1.05);
    }

    .logo-link {
        display: block;
        border: none;
    }
    
    .logo {
        width: 100%;
        height: auto;
        border-radius: var(--border-radius);
        max-height: 3rem;
    }

    @media (max-width: 768px) {
        .header-controls {
            padding: 0.5rem;
            gap: 0.5rem;
        }
        
        .logo {
            max-height: 2.5rem;
        }
    }

	section {
		margin: 2rem auto;
		max-width: 1200px;
		padding: 0 2rem;
	}


	section p {
		font-size: 22px;
		max-width: 800px;
		line-height: 1.3;
	}

	/* Keep only the first section's scrolly styles */

	.chart-container-scrolly {
		width: 40%;
		position: sticky;
		top: calc(50vh - 275px);
		right: 5%;
		margin-left: auto;
	}

	.visualization-container {
		display: flex;
		flex-direction: column;
		gap: 1rem;
		height: 100%;
	}

	.diamondplot {
		flex: 0 0 auto;
		display: flex;
		justify-content: center;
		align-items: center;
	}

	.additional-charts {
		display: flex;
		gap: 8rem;
        margin-left: 3rem;
		justify-content: center;
		margin-top: 2rem;
		flex: 0 0 auto;
	}

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

	.diamondplot :global(circle) {
		transition: 
			cx 700ms cubic-bezier(0.76, 0, 0.24, 1), 
			cy 700ms cubic-bezier(0.76, 0, 0.24, 1),
			fill 700ms cubic-bezier(0.76, 0, 0.24, 1),
			opacity 700ms cubic-bezier(0.76, 0, 0.24, 1);
	}

	.spacer {
		height: 75vh;
	}

	.step {
		height: 80vh;
		display: flex;
		place-items: center;
		justify-content: center;
	}

	.step p {
		padding: 0.5rem 1rem;
		background: whitesmoke;
		color: #ccc;
		border-radius: 5px;
		display: flex;
		flex-direction: column;
		justify-content: center;
		transition: background 500ms ease, color 500ms ease;
		box-shadow: 1px 1px 10px rgba(0, 0, 0, 0.2);
		z-index: 10;
		width: 40%;
		transform: translateX(-60%);
	}

	.step.active p {
		background: white;
		color: black;
	}

	@media (max-width: 1200px) {
		section {
			padding: 0 1rem;
		}

		section p {
			font-size: 18px;
			max-width: none;
		}

		.chart-container-scrolly {
			position: sticky;
			top: calc(50vh - 275px);
			width: 100%;
			max-width: 600px;
			margin: 2rem auto;
			display: flex;
			justify-content: center;
			align-items: center;
		}

		.additional-charts {
			flex-direction: column;
			gap: 1rem;
			align-items: center;
		}

		.step {
			margin-left: 0;
			padding: 0 1rem;
			justify-content: center;
		}

		.step p {
			width: 100%;
			max-width: 600px;
			margin: 0 auto;
			text-align: center;
			transform: none;
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
        width: 100%;
        padding: 4rem 0 0 8rem; /* Only top and side padding */
        text-align: center;
    }

    .dashboard-container {
        width: 100vw;
        margin-left: calc(-50vw + 50%); /* Break out of container */
        display: flex;
        justify-content: center;
        padding: 1rem 0;
    }
</style>