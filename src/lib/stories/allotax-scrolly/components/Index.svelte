<script>
    import * as d3 from "d3";
    import { fade, fly } from 'svelte/transition';
    
    import { innerWidth } from 'svelte/reactivity/window';
    import { Diamond, Legend, DivergingBarChart, Dashboard } from 'allotaxonometer-ui';
    import { combElems, rank_turbulence_divergence, diamond_count, wordShift_dat, balanceDat } from 'allotaxonometer-ui';
    import BarChartRank from './BarChartRank.svelte';
    

    import boys1895 from '../data/boys-1895.json';
    import boys1968 from '../data/boys-1968.json';
    
    import Scrolly from '$lib/components/helpers/Scrolly.svelte';
    import Md from '$lib/components/helpers/MarkdownRenderer.svelte';
    
    let { story, data } = $props();
    
    let scrollyIndex = $state(0);
	
	const steps = data.steps;

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
    let DashboardHeight = 815;
    let DashboardWidth = 1200;
    let max_shift = $derived(barData.length > 0 ? d3.max(barData, d => Math.abs(d.metric)) : 1);
    
    let me = $derived(sys1 && sys2 ? combElems(sys1, sys2) : null);
    let rtd = $derived(me ? rank_turbulence_divergence(me, alpha) : null);
    let dat = $derived(me && rtd ? diamond_count(me, rtd) : null);
    
    let barData = $derived(me && dat ? wordShift_dat(me, dat).slice(0, 30) : []);
    let balanceData = $derived(sys1 && sys2 ? balanceDat(sys1, sys2) : []);
    let maxlog10 = $derived(me ? Math.ceil(d3.max([Math.log10(d3.max(me[0].ranks)), Math.log10(d3.max(me[1].ranks))])) : 0);
    let max_count_log = $derived(dat ? Math.ceil(Math.log10(d3.max(dat.counts, d => d.value))) + 1 : 2);
    let isDataReady = $derived(dat && barData && balanceData && me && rtd);

    let renderedData = $state(null);

    $effect(() => {
        alpha = alphas[alphaIndex];
    });

    // Initialize with the original data
    $effect(() => {
        if (dat && !renderedData) {
            renderedData = dat;
            renderedBarData = barData;
        }
    });

    // Simple reactive logic like the working example
    $effect(() => {
        if (!dat || !barData) return;
            

        if (scrollyIndex === 0) {
            renderedData = {
                ...dat,
                counts: dat.counts.map(d => ({
                    ...d,
                    x1: Math.ceil(d.coord_on_diag),
                    y1: Math.ceil(d.coord_on_diag),
                    types: ""
                }))
            };
            

        } else if (scrollyIndex === 1) {
            renderedData = {
                ...dat,
                counts: dat.counts.map(d => ({
                    ...d,
                    x1: d.which_sys === "right" ? Math.ceil(d.coord_on_diag) : d.x1,
                    y1: d.which_sys === "right" ? Math.ceil(d.coord_on_diag) : d.y1,
                    types: d.which_sys === "right" ? "" : d.types,
                    value: d.which_sys === "right" ? 0 : d.value
                }))
            };


        } else {
            renderedData = dat;
        }
    });
</script>


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
    {#if scrollyIndex <= 2}
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
    
    <!-- Rest stays the same -->
    {#if scrollyIndex >= 1}
        <div class="additional-charts" 
            in:fade={{ duration: 800, delay: 300 }}
            out:fade={{ duration: 400 }}
        >
            <div class="legend-container" in:fly={{ x: -50, duration: 600, delay: 500 }}>
                <Legend
                    diamond_dat={dat.counts}
                    DiamondHeight={DiamondHeight}
                    max_count_log={max_count_log || 5}
                />
            </div>
            
            <div class="balance-container" style="opacity: {scrollyIndex >= 2 ? 1 : 0};">
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
    </div>
    <div class="slider-container">
    <div class="alpha-display">
        <span class="alpha-value">α = {alpha}</span>
    </div>
    <input 
                type="range"
                min="0"
                max={alphas.length - 1}
                value={alphaIndex}
                oninput={(e) => alphaIndex = parseInt(e.target.value)}
                class="alpha-slider"
    />
    <div class="slider-labels">
                <span>0</span>
                <span>∞</span>
            </div>
</div>
<p>We also show how the α parameter let us tweak the relative importance of divergence. We also finally learn what those contour lines mean! </p>
</section>

<style>


    .alpha-display {
        text-align: center;
        padding: 0.5rem;
        background-color: transparent;
        border: none;
    }

    .alpha-value {
        font-size: 0.9rem;
        font-weight: 500;
        color: var(--text-primary);
        margin-bottom: 0.25rem;
    }

    .slider-container {
        display: block;
        margin-left: auto;
        margin-right: auto;

        max-width: 300px;
        flex-direction: column;
        gap: 0.25rem;
    }

    .alpha-slider {
        width: 100%;
        height: 3px;
        background-color: var(--border-color);
        border-radius: 2px;
        outline: none;
        cursor: pointer;
        -webkit-appearance: none;
        appearance: none;
    }

    .alpha-slider::-webkit-slider-thumb {
        -webkit-appearance: none;
        appearance: none;
        width: 12px;
        height: 12px;
        background: var(--accent-color);
        border-radius: 50%;
        cursor: pointer;
    }

    .alpha-slider::-moz-range-thumb {
        width: 12px;
        height: 12px;
        background: var(--accent-color);
        border-radius: 50%;
        cursor: pointer;
        border: none;
    }

    .slider-labels {
        display: flex;
        justify-content: space-between;
        font-size: 0.7rem;
        color: var(--text-muted);
        opacity: 0.6;
    }

	section {
		margin: 2rem auto;
		max-width: 1200px;
		padding: 0 2rem;
	}

	/* Allow viz sections to overflow the max-width */
	section:has(.chart-container-scrolly) {
		max-width: none; /* Remove width constraint for sections with visualizations */
		padding: 0 1rem; /* Reduce padding to give more space */
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