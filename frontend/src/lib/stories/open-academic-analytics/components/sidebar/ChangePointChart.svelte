<script>
    import { Plot, Dot, LineY, Text, selectLast } from 'svelteplot';
    import { ageColorScale, colorConstants } from '../../utils/colorScales.js';
    import { dashboardState, uiState } from '../../state.svelte.js';
    import { loadTrainingData } from '../../data.remote.js';
    import { sidebar, spacing } from '../../utils/layout.js';
    import { BarChart3, Info } from "@lucide/svelte";
    let { authorName, visible = true } = $props();

    let containerWidth = $state(240); // Default fallback

    // Calculate plot width based on actual container width
    let plotWidth = $derived(Math.max(190, containerWidth - 40)); // 40px for padding

    // Color function that matches the main chart
    let getColor = $derived.by(() => {
        // Only show age colors when the main chart is using age coloring
        if (dashboardState.coauthorNodeColor === 'age_diff' || dashboardState.coauthorNodeColor === 'age_category') {
            return (d) => ageColorScale(d.age_category);
        } else {
            // Use neutral colors when main chart isn't using age coloring
            const neutralColors = {
                'older': '#cccccc',
                'same': '#999999',
                'younger': '#666666'
            };
            return (d) => neutralColors[d.age_category] || '#cccccc';
        }
    });

    // Use remote function to load training data
    let trainingData = $derived.by(async () => {
        if (!authorName) return [];

        try {
            return await loadTrainingData({ authorName });
        } catch (error) {
            console.error('Error loading training data:', error);
            return [];
        }
    });

    // Data is already in the correct format from the backend
    let plotData = $derived.by(async () => {
        const data = await trainingData;
        return data || [];
    });

    let hasResearchGroup = $derived.by(async () => {
        const data = await trainingData;
        if (!data?.length) return false;
        return data[0]?.has_research_group === 1;
    });

    let changingRate = $derived.by(async () => {
        const data = await trainingData;
        if (!data?.length) return 0;
        return data[0]?.changing_rate || 0;
    });
</script>

{#if visible && authorName}
    <div class="changepoint-widget">
        <div class="widget-header">
            <BarChart3 size={14} />
            <span class="widget-title">Bayesian Change Point Model</span>
        </div>
        <div class="switchpoint" class:visible bind:clientWidth={containerWidth}>

        {#await plotData}
            <div class="loading">Loading change point data...</div>
        {:then data}
            {#if data.length > 0}
                <Plot
                    grid
                    frame
                    width={plotWidth}
                    height={170}
                    x={{label: "Author Age"}}
                    y={{label: "↑ #Collaborations"}}
                >
                    <Dot
                        data={data}
                        x="pub_year"
                        y="counts"
                        stroke={getColor}
                        fill={getColor}
                        r={3}
                    />
                    <LineY
                        data={data.filter((d, i, arr) => arr.findIndex(x => x.pub_year === d.pub_year) === i)}
                        x="pub_year"
                        y="changing_rate"
                        stroke="black"
                        strokeDasharray="3,3"
                        strokeWidth={2}
                    />
                </Plot>
            {:else}
                <div class="no-data">No change point data available for this author</div>
            {/if}
        {:catch error}
            <div class="error">Error loading data: {error.message}</div>
        {/await}
        </div>
    </div>
{/if}

<style>
    .changepoint-widget {
        margin-bottom: 1rem;
    }

    .widget-header {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        margin-bottom: 0.5rem;
        padding-bottom: 0.25rem;
        border-bottom: 1px solid var(--color-border);
    }

    .widget-title {
        font-size: var(--font-size-xsmall);
        font-weight: var(--font-weight-medium);
        color: var(--color-fg);
    }

    .switchpoint {
        background: var(--step-bg, #ffffff);
        border: 1px solid var(--color-border, #ddd);
        border-radius: 8px;
        padding: 2px;
        margin-top: 1rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        font-size: 11px;

        /* Ensure solid background */
        background-color: rgba(255, 255, 255, 0.95);

        /* Responsive width, fixed height */
        width: 100%;
        min-width: 200px;
        max-width: 100%;
        height: 170px;

        /* Transition properties */
        opacity: 0;
        transform: translateX(-20px);
        transition: opacity 0.6s ease, transform 0.6s ease;
        pointer-events: auto;
    }

    .switchpoint.visible {
        opacity: 1;
        transform: translateX(0);
    }

    /* Make sure the Plot component fills the container properly */
    .switchpoint :global(svg) {
        max-width: 100%;
        height: auto;
    }


    .summary {
        margin-top: 8px;
        font-size: 10px;
        line-height: 1.3;
        color: var(--color-fg, #333);
    }


    .loading, .error, .no-data {
        display: flex;
        align-items: center;
        justify-content: center;
        height: 170px;
        text-align: center;
        font-size: 10px;
        color: var(--color-fg-muted, #666);
    }

    .error {
        color: var(--color-error, #d32f2f);
    }
</style>