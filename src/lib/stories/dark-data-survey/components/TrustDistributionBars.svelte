<script>
    let { distribution, firstPoint, demographicBreakdown, GENDER } = $props();
    
    const orientationColors = {
        "0": "#8b5cf6", // Purple for straight
        "1": "#06b6d4", // Cyan for bisexual  
        "2": "#92400e", // Brown for gay
        "3": "#6b7280"  // Grey for other
    };
</script>

<div class="section">
    <h4>Trust Distribution</h4>
    
    <!-- Stacked bar chart -->
    <div class="trust-bars">
        {#each Object.entries(distribution).sort(([a], [b]) => parseFloat(a) - parseFloat(b)) as [level, totalCount]}
            {@const trustByOrientationData = firstPoint?.trustByOrientation || {}}
            {@const maxCount = Math.max(...Object.values(distribution))}
            {@const orientationData = trustByOrientationData[level] || {}}
            {@const barWidth = (totalCount / maxCount) * 100}
            
            <div class="trust-level-row">
                <span class="trust-label">Trust {level}:</span>
                <div class="bar-container">
                    <div class="stacked-bar" style="width: {barWidth}%">
                        {#each Object.entries(orientationData) as [orientation, count]}
                            {@const segmentWidth = (count / totalCount) * 100}
                            <div 
                                class="bar-segment" 
                                style="width: {segmentWidth}%; background-color: {orientationColors[orientation] || '#6b7280'}"
                                title="{orientation === '0' ? 'Straight' : orientation === '1' ? 'Bisexual' : orientation === '2' ? 'Gay' : 'Other'}: {count}"
                            ></div>
                        {/each}
                    </div>
                </div>
                <span class="count">{totalCount}</span>
            </div>
        {/each}
    </div>
    
    <div class="subtotal">
        <strong>Total: {demographicBreakdown.gender_ord} {GENDER == 1 ? "Men" : "Women"}</strong>
    </div>
</div>

<style>
    .section {
        margin-bottom: 1.5rem;
    }
    
    .section:last-child {
        margin-bottom: 0;
    }
    
    .section h4 {
        margin: 0 0 0.75rem 0;
        font-size: 0.875rem;
        font-weight: 600;
        color: #333;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    .subtotal {
        padding-top: 0.5rem;
        border-top: 1px solid #ddd;
        text-align: center;
        font-size: 0.8rem;
        color: #333;
    }
    
    .trust-bars {
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
        margin-bottom: 1rem;
    }
    
    .trust-level-row {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        font-size: 0.8rem;
    }
    
    .trust-label {
        color: #666;
        font-weight: 500;
        min-width: 60px;
        flex-shrink: 0;
    }

    .bar-container {
        flex: 1;
        height: 16px;
        background: #f5f5f5;
        border-radius: 2px;
        overflow: hidden;
    }
    
    .stacked-bar {
        height: 100%;
        display: flex;
        background: transparent;
    }
    
    .bar-segment {
        height: 100%;
        transition: all 0.2s ease;
    }
    
    .bar-segment:hover {
        opacity: 0.8;
        cursor: pointer;
    }
    
    .count {
        color: #333;
        font-weight: 600;
        min-width: 25px;
        text-align: right;
        flex-shrink: 0;
    }
</style>