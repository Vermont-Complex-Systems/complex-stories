<script>
    import * as d3 from "d3";
    import { Plot, BarY, RuleY } from 'svelteplot';
    import { innerWidth } from 'svelte/reactivity/window';
    import { Diamond } from 'allotaxonometer-ui';
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
    
    
    let height = 600;
    const padding = { top: 20, right: 40, bottom: 20, left: 60 };
    let width = $state(innerWidth.current > 1200 ? 450 : 350);

    let DashboardHeight = 815;
    let DashboardWidth = 1200;
    let DiamondHeight = 600;
    let DiamondWidth = DiamondHeight;
    let marginInner = 160;
    let marginDiamond = 40;
    let WordshiftWidth = 550;

    
    let me = $derived(sys1 && sys2 ? combElems(sys1, sys2) : null);
    let rtd = $derived(me ? rank_turbulence_divergence(me, alpha) : null);
    let dat = $derived(me && rtd ? diamond_count(me, rtd) : null);
    
    let barData = $derived(me && dat ? wordShift_dat(me, dat).slice(0, 30) : []);
    let balanceData = $derived(sys1 && sys2 ? balanceDat(sys1, sys2) : []);
    let maxlog10 = $derived(me ? Math.ceil(d3.max([Math.log10(d3.max(me[0].ranks)), Math.log10(d3.max(me[1].ranks))])) : 0);
    let max_count_log = $derived(dat ? Math.ceil(Math.log10(d3.max(dat.counts, d => d.value))) + 1 : 2);
    let max_shift = $derived(barData.length > 0 ? d3.max(barData, d => Math.abs(d.metric)) : 1);
    let isDataReady = $derived(dat && barData && balanceData && me && rtd);

    let renderedData = $state(null);
    let renderedBarData = $state([]);

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
                    value: 0, // Use 0 instead of null
                    types: ""
                }))
            };
            
            renderedBarData = barData.map(d => ({
                ...d,
                metric: 0
            }));

        } else if (scrollyIndex === 1) {
            renderedData = {
                ...dat,
                counts: dat.counts.map(d => ({
                    ...d,
                    x1: Math.ceil(d.coord_on_diag),
                    y1: Math.ceil(d.coord_on_diag),
                    types: ""
                }))
            };
            
            renderedBarData = barData.map(d => ({
                ...d,
                metric: 0
            }));

        } else if (scrollyIndex === 2) {
            renderedData = {
                ...dat,
                counts: dat.counts.map(d => ({
                    ...d,
                    x1: d.which_sys === "left" ? Math.ceil(d.coord_on_diag) : d.x1,
                    y1: d.which_sys === "left" ? Math.ceil(d.coord_on_diag) : d.y1,
                    types: d.which_sys === "left" ? "" : d.types
                }))
            };
            
            renderedBarData = barData.map(d => ({
                ...d,
                metric: d.metric < 0 ? 0 : d.metric
            }));

        } else if (scrollyIndex === 3) {
            renderedData = dat;
            renderedBarData = barData;
        }
    });

    $inspect(sys1.slice(0,30), )
</script>


<section>
    <h1>Allotaxonometer Scrolly</h1>

    <p>
        This is a scrolly visualization of the <a href="https://allotaxonometer.org" target="_blank">Allotaxonometer</a> tool, which visualizes the differences between two data systems. 
        The diamond plot shows the rank turbulence and divergence between the two systems, while the word shift plot illustrates the shifts in word usage.
    </p>

    <p>Here's the top 30 boy baby names from two different years:</p>
    <div class="comparison-charts">
    <Plot 
        subtitle="1895" 
        y={{ grid: true }}
        x={{ tickRotate: 25 }}
        marginTop={25} 
        marginRight={25} 
        height={300}>
        <BarY 
            data={sys1.slice(0,30)} 
            y="counts" x="types" 
            fill="#01010133" 
            stroke="grey"
            sort={{ channel: '-y' }}  />
        <RuleY data={[0]} />
    </Plot>
    
    <Plot 
        subtitle="1968"
        y={{ grid: true }} 
        x={{ tickRotate: 25 }}
        marginTop={25} 
        marginRight={25} 
        height={300}>
        <BarY 
            data={sys2.slice(0,30)} 
            y="counts" x="types" 
            fill="#c3e6f3e6" 
            stroke="grey"
            sort={{ channel: '-y' }}  />
        <RuleY data={[0]} />
    </Plot>
    </div>
    
    <p>If you wanted to compare which babyname got more popular over time, how would you do it? 
	   You can say that Robert is more popular than John. Then what?</p>
    
    <div class="chart-container-scrolly">
        {#if isDataReady && renderedData}
            <div class="visualization-container">
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
                
                <!-- Bar chart that appears in later steps -->
                {#if renderedBarData.length > 0 && scrollyIndex >= 2}
                    <div class="barchart">
                        <h3>Word Shift Analysis</h3>
                        <BarChartRank barData={renderedBarData.slice(0, 15)} height={250} />
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

<style>
    .comparison-charts {
        display: flex;
        gap: 2rem;
        margin: 2rem 0;
        align-items: flex-start;
    }

    .chart-item {
        flex: 1;
        min-width: 0; /* Allows flex items to shrink below their content size */
    }

    /* Only global page styles */
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
		height: 550px;
		position: sticky;
		top: calc(50vh - 275px);
		right: 5%;
		margin-left: auto;
	}

	/* Global CSS transitions like the working example */
	:global(rect) {
		transition: 
			x 700ms cubic-bezier(0.76, 0, 0.24, 1), 
			y 700ms cubic-bezier(0.76, 0, 0.24, 1),
			fill 700ms cubic-bezier(0.76, 0, 0.24, 1),
			width 700ms cubic-bezier(0.76, 0, 0.24, 1),
			height 700ms cubic-bezier(0.76, 0, 0.24, 1),
			opacity 700ms cubic-bezier(0.76, 0, 0.24, 1);
	}

	:global(text) {
		transition: 
			x 700ms cubic-bezier(0.76, 0, 0.24, 1), 
			y 700ms cubic-bezier(0.76, 0, 0.24, 1),
			opacity 700ms cubic-bezier(0.76, 0, 0.24, 1);
	}

	:global(circle) {
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
</style>