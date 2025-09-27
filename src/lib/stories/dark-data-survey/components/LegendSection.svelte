<script>
    let { demographicBreakdown } = $props();
    
    const raceColors = {
        "0": "#3b82f6", // Blue for white
        "1": "#f59e0b", // Amber for mixed  
        "2": "#ef4444"  // Red for poc
    };
</script>

<!-- Race color legend -->
<div class="section">
    <h4>Race (Color) Legend</h4>
    <div class="race-legend">
        <div class="legend-item">
            <div class="legend-dot" style="background-color: #3b82f6;"></div>
            <span>White ({demographicBreakdown.race?.white || 0})</span>
        </div>
        <div class="legend-item">
            <div class="legend-dot" style="background-color: #f59e0b;"></div>
            <span>Mixed ({demographicBreakdown.race?.mixed || 0})</span>
        </div>
        <div class="legend-item">
            <div class="legend-dot" style="background-color: #ef4444;"></div>
            <span>POC ({demographicBreakdown.race?.poc || 0})</span>
        </div>
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
        color: #f3f4f6;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .race-legend {
        display: flex;
        color: #f3f4f6;
        flex-direction: column;
        gap: 0.5rem;
    }
    
    .legend-item {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        font-size: 0.875rem;
    }
    
    .legend-dot {
        width: 12px;
        height: 12px;
        border-radius: 50%;
        border: 1px solid #f3f4f6;
        flex-shrink: 0;
    }
    
</style>