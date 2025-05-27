<script>
    import { scaleLinear } from "d3-scale";
    import { extent } from "d3-array";
    
    let { scrollyIndex, data } = $props();
    
    // Reactive state
    let width = $state(600);
    let height = $state(400);
    
    // Constants
    const margin = { top: 20, right: 20, left: 60, bottom: 40 };
    
    // Derived values
    let innerWidth = $derived(width - margin.left - margin.right);
    let innerHeight = $derived(height - margin.top - margin.bottom);
    
    // Process coauthor data
    let processedData = $derived(data?.map(d => ({
        name: d.coauth_name,
        authorAge: parseFloat(d.author_age) || 0,
        coauthAge: parseFloat(d.coauth_age) || 0,
        pubYear: parseInt(d.pub_year) || 2000,
        institution: d.institution,
        acquaintance: d.acquaintance,
        ageBucket: d.age_bucket
    })) || []);
    
    // Scales
    let xScale = $derived(() => {
        if (!processedData.length) return scaleLinear().range([0, innerWidth]);
        const extent_x = extent(processedData, d => d.authorAge);
        return scaleLinear()
            .domain([Math.max(0, extent_x[0] - 2), extent_x[1] + 2])
            .range([0, innerWidth]);
    });
    
    let yScale = $derived(() => {
        if (!processedData.length) return scaleLinear().range([innerHeight, 0]);
        const extent_y = extent(processedData, d => d.pubYear);
        return scaleLinear()
            .domain([extent_y[0] - 1, extent_y[1] + 1])
            .range([innerHeight, 0]);
    });
    
    // Generate tick marks for axes
    let xTicks = $derived(() => {
        if (!processedData.length) return [];
        return xScale().ticks(6);
    });
    
    let yTicks = $derived(() => {
        if (!processedData.length) return [];
        return yScale().ticks(8);
    });
    
    // Filter data based on scrollyIndex
    let visibleData = $derived(() => {
        if (scrollyIndex === undefined) return processedData;
        
        // You can customize this logic based on your story steps
        switch (scrollyIndex) {
            case 0:
                return processedData.slice(0, 5); // Show first 5 collaborations
            case 1:
                return processedData.filter(d => d.acquaintance === 'new_collab'); // New collaborations only
            case 2:
                return processedData.filter(d => d.ageBucket === 'much_older'); // Much older coauthors
            case 3:
                return processedData.filter(d => d.pubYear >= 2000); // Recent collaborations
            default:
                return processedData; // Show all
        }
    });
</script>

<div class="chart-container" bind:clientWidth={width}>
    <svg {width} {height}>
        <g transform="translate({margin.left}, {margin.top})">
            
            <!-- Y-axis (Time) -->
            <g class="y-axis">
                <line x1="0" y1="0" x2="0" y2={innerHeight} stroke="#e2e8f0" stroke-width="1" />
                {#each yTicks as tick}
                    <g transform="translate(0, {yScale()(tick)})">
                        <line x1="-5" y1="0" x2="0" y2="0" stroke="#e2e8f0" />
                        <text x="-10" y="0" text-anchor="end" dominant-baseline="middle" class="axis-label">
                            {tick}
                        </text>
                    </g>
                {/each}
                <text 
                    x="-40" 
                    y={innerHeight / 2} 
                    text-anchor="middle" 
                    dominant-baseline="middle"
                    transform="rotate(-90, -40, {innerHeight / 2})"
                    class="axis-title"
                >
                    Publication Year
                </text>
            </g>
            
            <!-- X-axis (Author Age) -->
            <g class="x-axis">
                <line x1="0" y1={innerHeight} x2={innerWidth} y2={innerHeight} stroke="#e2e8f0" stroke-width="1" />
                {#each xTicks as tick}
                    <g transform="translate({xScale()(tick)}, {innerHeight})">
                        <line x1="0" y1="0" x2="0" y2="5" stroke="#e2e8f0" />
                        <text x="0" y="20" text-anchor="middle" class="axis-label">
                            {tick}
                        </text>
                    </g>
                {/each}
                <text 
                    x={innerWidth / 2} 
                    y={innerHeight + 35} 
                    text-anchor="middle" 
                    class="axis-title"
                >
                    Author Age
                </text>
            </g>
            
            <!-- Data points -->
            {#each visibleData as point, i}
                <circle
                    cx={xScale()(point.authorAge)}
                    cy={yScale()(point.pubYear)}
                    r="5"
                    fill="#667eea"
                    opacity="0.7"
                    stroke="#4c51bf"
                    stroke-width="1"
                    title="{point.name} ({point.pubYear})"
                />
            {/each}
            
        </g>
    </svg>
    
    <!-- Data info -->
    <div class="info-panel">
        <div class="stat">
            <span class="label">Collaborations shown:</span>
            <span class="value">{visibleData.length}</span>
        </div>
        <div class="stat">
            <span class="label">Total collaborations:</span>
            <span class="value">{processedData.length}</span>
        </div>
    </div>
</div>

<style>
    .chart-container {
        position: relative;
        margin: 0 auto;
        height: 500px;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        background: white;
        border-radius: 8px;
        padding: 20px;
    }
    
    .axis-label {
        font-size: 12px;
        fill: #64748b;
    }
    
    .axis-title {
        font-size: 14px;
        fill: #334155;
        font-weight: 500;
    }
    
    circle {
        transition: all 0.3s ease;
    }
    
    circle:hover {
        opacity: 1;
        r: 7;
        stroke-width: 2;
    }
    
    .info-panel {
        position: absolute;
        top: 20px;
        right: 20px;
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 6px;
        padding: 12px;
        font-size: 0.9rem;
    }
    
    .stat {
        display: flex;
        justify-content: space-between;
        margin-bottom: 4px;
        min-width: 180px;
    }
    
    .stat:last-child {
        margin-bottom: 0;
    }
    
    .label {
        color: #64748b;
    }
    
    .value {
        color: #667eea;
        font-weight: bold;
        font-family: monospace;
    }
</style>