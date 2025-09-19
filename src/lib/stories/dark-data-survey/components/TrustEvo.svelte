<script>
    import { scaleSequential } from 'd3-scale';
    import { interpolateRdYlGn } from 'd3-scale-chromatic';
    
    import People from './People.svelte';
    import CenterEgo from './CenterEgo.svelte';
    import Legend from './Legend.svelte';
    import TrustDistributionChart from './TrustDistributionChart.svelte';
    import IndividualUserPoints from './IndividualUserPoints.svelte';
    import TrustCircles from './TrustCircles.svelte';
    
    import { trustDistancesByDemographic } from '../data/trustDistances.js';


    let { scrollyIndex, selectedDemographic, width, height } = $props();
    
    const centerX = width / 2;
    const centerY = height / 2;
    const maxRadius = Math.min(centerX, centerY) - 50;
    
    // Get trust distances for current demographic and unique distances for circles
    const uniqueDistances = $derived(() => {
        const trustDistances = trustDistancesByDemographic[selectedDemographic] || trustDistancesByDemographic.all;
        return [...new Set(Object.values(trustDistances))].sort((a, b) => a - b);
    });

    // Red (low trust) to Yellow to Green (high trust)
    const trustworthinessColorScale = scaleSequential(interpolateRdYlGn)
        .domain([1, 7]);

</script>

<div class="chart-wrapper">
     <div class="viz-content">
        <div class="plot-container">
            <svg {width} {height} class="trust-visualization">
                <TrustCircles distances={uniqueDistances()} {centerX} {centerY} {maxRadius}/>
                <IndividualUserPoints {centerX} {centerY} {trustworthinessColorScale} {maxRadius}/>
            </svg>
        </div>
    </div>
</div>

<style>
    .chart-wrapper {
        display: flex;
        justify-content: center;
        align-items: center;
        width: 100%;
    }
    
    .viz-content {
        display: flex;
        justify-content: center;
        align-items: center;
    }
    
    .plot-container {
        display: flex;
        justify-content: center;
        align-items: center;
    }
    
    .trust-visualization {
        display: block;
        margin: 0 auto;
    }
</style>