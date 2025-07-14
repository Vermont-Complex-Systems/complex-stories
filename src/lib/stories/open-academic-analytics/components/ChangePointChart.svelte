<script>
    import { ageColorScale } from '../utils/combinedChartUtils'
    import { Plot, Dot, LineY, Text, selectLast } from 'svelteplot';
    let { data, visible = true } = $props();
</script>

<div class="switchpoint" class:visible>
    <div class="legend-title">Bayesian Change Point model</div>
    <Plot 
        grid 
        frame 
        width={190}
        height={170}
        x={{label: false}}
        y={{label: "↑ #Collaborations"}}
        color={{scheme: [ageColorScale('older'), ageColorScale('same'), ageColorScale('younger')]}}
    >
        <Dot 
            {data}  
            x="pub_year" 
            y="counts"
            stroke="age_category"
            fill="age_category"
            r={3}
        />
        <LineY 
            {data}  
            x="pub_year" 
            y="changing_rate"
            stroke="black" 
            strokeDasharray="3,3"
            strokeWidth={2}
        />
    </Plot>
    <div>
        Estimated collaboration rate with younger coauthors = {data[data.length-1].changing_rate.toFixed(1)} ({data[1].has_research_group === 1 ? 'Faculty has a research group' : 'Faculty does not have a research group'})
    </div>
</div>

<style>
    .switchpoint {
        background: var(--step-bg);
        border: 1px solid var(--color-border, #ddd);
        border-radius: 8px;
        padding: 12px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        font-size: 11px;
        
        /* Ensure solid background */
        background-color: rgba(255, 255, 255, 0.95);
        
        /* Compact dimensions */
        width: 210px;
        height: 260px;
        
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

    .legend-title {
    font-weight: bold;
    font-size: 12px;
    color: var(--step-bg);
    margin-bottom: 4px;
    text-align: center;
    border-bottom: 1px solid #eee;
    padding-bottom: 4px;
  }

</style>