<script>
    import { scaleSequential, scaleLinear } from 'd3-scale';
    import { interpolateRdYlGn } from 'd3-scale-chromatic';
    import { extent } from 'd3-array';
    
    import TrustDistributionChart from './TrustDistributionChart.svelte';
    import trust_circles from '../data/trust_circles.csv';
    

    let { scrollyIndex, selectedDemographic, width, height, isStorySection = false, storySection, conclusionVisible = false } = $props();
    
    // Track if story section is in viewport
    let storySectionVisible = $state(false);
    
    $effect(() => {
        if (typeof window !== 'undefined' && storySection) {
            const observer = new IntersectionObserver((entries) => {
                storySectionVisible = entries[0].isIntersecting;
            }, { threshold: 0.1 });
            
            observer.observe(storySection);
            
            return () => observer.disconnect();
        }
    });
    
    // Phase detection - 1 baseline + 2 gender + 2 relationship + 4 orientation + 3 race = 12 total
    const isInteractivePhase = $derived(scrollyIndex >= 12);
    
    // Manual filter controls for interactive phase
    let selectedCategory = $state('overall_average');
    let selectedValue = $state("1.0");
    
    // Auto-select category based on scroll in phase 1
    const autoSelectedCategory = $derived(() => {
        if (scrollyIndex === 0) return 'overall_average';
        if (scrollyIndex === 1) return 'Dem_Gender_Man'; 
        if (scrollyIndex === 2) return 'Dem_Gender_Man';
        if (scrollyIndex === 3) return 'Dem_Relationship_Status_Single';
        if (scrollyIndex === 4) return 'Dem_Relationship_Status_Single';
        if (scrollyIndex === 5) return 'orientation_ord';
        if (scrollyIndex === 6) return 'orientation_ord';
        if (scrollyIndex === 7) return 'orientation_ord';
        if (scrollyIndex === 8) return 'orientation_ord';
        if (scrollyIndex === 9) return 'race_ord';
        if (scrollyIndex === 10) return 'race_ord';
        if (scrollyIndex === 11) return 'race_ord';
        return selectedCategory;
    });
    
    const autoSelectedValue = $derived(() => {
        if (scrollyIndex === 0) return "1.0"; // Overall average
        if (scrollyIndex === 1) return "0.0"; // Gender female (0)
        if (scrollyIndex === 2) return "1.0"; // Gender male (1)
        if (scrollyIndex === 3) return "0.0"; // Relationship not single (0)
        if (scrollyIndex === 4) return "1.0"; // Relationship single (1)
        if (scrollyIndex === 5) return "0.0"; // Orientation 0
        if (scrollyIndex === 6) return "1.0"; // Orientation 1
        if (scrollyIndex === 7) return "2.0"; // Orientation 2
        if (scrollyIndex === 8) return "3.0"; // Orientation 3
        if (scrollyIndex === 9) return "0.0"; // Race 0
        if (scrollyIndex === 10) return "1.0"; // Race 1
        if (scrollyIndex === 11) return "2.0"; // Race 2
        return selectedValue;
    });
    
    // Current active filters
    const currentCategory = $derived(isInteractivePhase ? selectedCategory : autoSelectedCategory());
    const currentValue = $derived(isInteractivePhase ? selectedValue : autoSelectedValue());
    
    // Get available categories and values
    const categories = [...new Set(trust_circles.map(d => d.category))];
    const getValuesForCategory = (cat) => [...new Set(trust_circles.filter(d => d.category === cat).map(d => d.value))];
    
    // Filtered data
    const filteredCircles = $derived(() => {
        const category = isInteractivePhase ? selectedCategory : autoSelectedCategory();
        const value = isInteractivePhase ? selectedValue : autoSelectedValue();
        
        return trust_circles.filter(d => 
            d.category === category && d.value.toString() === value
        );
    });
    
    // Background average circles (always visible as dotted lines)
    const backgroundCircles = $derived(() => {
        return trust_circles.filter(d => 
            d.category === 'overall_average' && d.value.toString() === '1.0'
        );
    });
    
    const centerX = $derived(width / 2);
    const centerY = $derived(height / 2);
    const maxRadius = $derived(height * 0.4);
    
    // Red (low trust) to Yellow to Green (high trust)
    // const trustworthinessColorScale = scaleSequential(interpolateRdYlGn).domain([1, 7]);
    
    // Use same scale for both circles and dots based on actual data range
    // const allDistances = [...trust_circles.map(d => d.distance), ...first_individual.map(d => d.distance)];

    const zScale = $derived(scaleSequential(interpolateRdYlGn)
        .domain(extent(trust_circles.map(d=>d.distance))));
    
    const radiusScale = $derived(scaleLinear()
        .domain(extent(trust_circles.map(d=>d.distance)))
        .range([1, maxRadius+25]));
    
    // Institution color mapping for consistent visualization (same as bar chart)
    const institutionColors = {
        'TP_Friend': '#10b981',        // Green - high trust category
        'TP_Relative': '#059669',      // Dark green
        'TP_Medical': '#0891b2',       // Teal - professional services
        'TP_School': '#0284c7',        // Blue - educational
        'TP_Employer': '#7c3aed',      // Purple - work related
        'TP_Researcher': '#9333ea',    // Purple variant
        'TP_Co_worker': '#8b5cf6',     // Light purple
        'TP_Police': '#dc2626',        // Red - authority/government
        'TP_Platform': '#ea580c',      // Orange - tech platforms
        'TP_Company_cust': '#f59e0b',  // Amber - business
        'TP_Company_notcust': '#d97706', // Dark amber
        'TP_Acquaintance': '#6b7280',  // Gray - neutral relationships
        'TP_Neighbor': '#9ca3af',      // Light gray
        'TP_Gov': '#ef4444',           // Red - government
        'TP_NonProf': '#22c55e',       // Green - community
        'TP_Financial': '#f97316',     // Orange - financial
        'TP_Stranger': '#374151'       // Dark gray - unknown
    };
    
</script>

<div bind:clientWidth={width} bind:clientHeight={height} class="chart-wrapper">
     <div class="viz-content">
        {#if isInteractivePhase}
            <div class="controls" style="pointer-events: auto; position: relative; z-index: 1000;">
                <label>
                    Category:
                    <select bind:value={selectedCategory}>
                        {#each categories as category}
                            <option value={category}>{category}</option>
                        {/each}
                    </select>
                </label>
                
                <label>
                    Value:
                    <select bind:value={selectedValue}>
                        {#each getValuesForCategory(selectedCategory) as value}
                            <option value={value.toString()}>{value}</option>
                        {/each}
                    </select>
                </label>
            </div>
        {:else}
            <div class="scrolly-info">
                <p>Currently showing: {currentCategory} = {currentValue}</p>
            </div>
        {/if}
        
        <div class="plot-container">
            <svg width={width} height={height} class="trust-visualization" viewBox={`0 0 ${width} ${height}`}>
                <!-- Background average circles (always visible as dotted lines) -->
                <g class="background-circles">
                    {#each backgroundCircles() as circle}
                        <circle
                            cx={centerX}
                            cy={centerY}
                            r={radiusScale(circle.distance)}
                            fill="none"
                            stroke={institutionColors[circle.institution] || '#cccccc'}
                            stroke-width="1"
                            stroke-dasharray="4,4"
                            opacity="0.3"
                        />
                    {/each}
                </g>
                
                <g class="trust-circles">
                    {#each filteredCircles() as circle}
                        <circle
                            cx={centerX}
                            cy={centerY}
                            r={radiusScale(circle.distance)}
                            fill="none"
                            stroke={institutionColors[circle.institution] || '#6b7280'}
                            stroke-width="2"
                            stroke-dasharray={circle.value === 0 ? "8,4" : "none"}
                            opacity={scrollyIndex === 1 && circle.value === 0 ? "0.7" : "1.0"}
                            style="transition: r 0.8s ease-in-out;"
                        />
                    {/each}
                </g>                
            </svg>
        </div>
        
        <!-- Trust Distribution Chart in bottom right - only during main scrolly story -->
        <div class="chart-overlay" 
             class:visible={isStorySection && typeof scrollyIndex === 'number' && scrollyIndex >= 0 && scrollyIndex <= 11 && filteredCircles().length > 0}
             class:fade-out={conclusionVisible}>
            {#if filteredCircles().length > 0}
                <TrustDistributionChart 
                    filteredData={filteredCircles()} 
                    colorScale={zScale} />
            {/if}
        </div>
    </div>
</div>

<style>
    .chart-wrapper {
        --chart-grid-color: var(--color-border);
        --chart-text-color: var(--color-secondary-gray);
        --chart-tooltip-bg: var(--color-bg);
        width: 100%;
        position: relative;
        height: 100vh;
    }
    
    .controls {
        display: flex;
        gap: 1rem;
        margin-bottom: 1rem;
        padding: 1rem;
        background: rgba(255, 255, 255, 0.9);
        border-radius: 8px;
    }
    
    .controls label {
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
    }
    
    .controls select {
        padding: 0.5rem;
        border: 1px solid #ccc;
        border-radius: 4px;
    }
    
    .scrolly-info {
        padding: 1rem;
        text-align: center;
        font-weight: 500;
        color: var(--color-secondary-gray);
    }
    
    .plot-container {
        position: relative;
        overflow: visible;
        width: 100vw;
        height: 100vh;
        left: 50%;
        transform: translateX(-50%);
        pointer-events: none;
    }
    
    .plot-container svg {
        width: 100%;
        height: 100%;
        position: absolute;
        top: 0;
        left: 0;
    }
    
    .chart-overlay {
        position: fixed;
        bottom: 2rem;
        right: 2rem;
        z-index: 1000;
        pointer-events: none;
        transform: translateX(100%);
        opacity: 0;
        transition: opacity 0.6s ease, transform 0.8s ease;
    }
    
    .chart-overlay.visible {
        pointer-events: auto;
        transform: translateX(0);
        opacity: 1;
    }
    
    .chart-overlay.fade-out {
        opacity: 0;
        pointer-events: none;
    }
    
    @keyframes slideInFromRight {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    

</style>