<script>
    let { distribution, firstPoint, demographicBreakdown, selectedDemCategory = 'orientation_ord', selectedValue } = $props();

    const categoryColors = {
        orientation_ord: {
            "0": "#8b5cf6", // Purple for straight
            "1": "#06b6d4", // Cyan for bisexual
            "2": "#92400e", // Brown for gay
            "3": "#6b7280"  // Grey for other
        },
        race_ord: {
            "0": "#3b82f6", // Blue for White
            "1": "#f59e0b", // Amber for Mixed
            "2": "#ef4444"  // Red for POC
        },
        gender_ord: {
            "0": "#ec4899", // Pink for Women
            "1": "#3b82f6", // Blue for Men
            "2": "#6b7280"  // Grey for Other
        },
        multi_platform_ord: {
            "1": "#10b981", // Green for 1
            "2": "#3b82f6", // Blue for 2
            "3": "#8b5cf6", // Purple for 3
            "4": "#f59e0b", // Amber for 4
            "5": "#ef4444"  // Red for 5
        },
        ACES_Compound: {
            "0": "#10b981", "1": "#34d399", "2": "#6ee7b7", "3": "#99f6e4",
            "4": "#5eead4", "5": "#2dd4bf", "6": "#14b8a6", "7": "#0d9488",
            "8": "#0f766e", "9": "#115e59", "10": "#134e4a", "11": "#dc2626", "12": "#991b1b"
        },
        overall_average: {
            "1.0": "#6b7280"
        }
    };

    const colors = $derived(categoryColors[selectedDemCategory] || categoryColors.orientation_ord);

    const categoryLabels = {
        orientation_ord: {
            "0": "Straight", "1": "Bisexual", "2": "Gay", "3": "Other"
        },
        race_ord: {
            "0": "White", "1": "Mixed", "2": "POC"
        },
        gender_ord: {
            "0": "Women", "1": "Men", "2": "Other"
        },
        multi_platform_ord: {
            "1": "1 Platform", "2": "2 Platforms", "3": "3 Platforms", "4": "4 Platforms", "5": "5 Platforms"
        },
        overall_average: {
            "1.0": "All Users"
        }
    };

    const labels = $derived(categoryLabels[selectedDemCategory] || {});
</script>

<div class="section">
    <!-- Legend -->
    <div class="legend">
        {#each Object.entries(colors) as [key, color]}
            {@const isSelected = parseFloat(key) === parseFloat(selectedValue)}
            <div class="legend-item" class:selected={isSelected}>
                <div class="legend-dot" style="background-color: {color};"></div>
                <span>{labels[key] || key}</span>
            </div>
        {/each}
    </div>

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
                        {#each Object.entries(orientationData) as [categoryValue, count]}
                            {@const segmentWidth = (count / totalCount) * 100}
                            {@const isSelected = parseFloat(categoryValue) === parseFloat(selectedValue)}
                            {@const colorKey = String(Math.floor(parseFloat(categoryValue)))}
                            <div
                                class="bar-segment"
                                class:selected-segment={isSelected}
                                style="width: {segmentWidth}%; background-color: {colors[colorKey] || '#6b7280'}"
                                title="{categoryValue}: {count}"
                            ></div>
                        {/each}
                    </div>
                </div>
                <span class="count">{totalCount}</span>
            </div>
        {/each}
    </div>
    
    <div class="subtotal">
        <strong>Total: {demographicBreakdown.total || 0}</strong>
    </div>
</div>

<style>
    .section {
        margin-bottom: 1.5rem;
    }
    
    .section:last-child {
        margin-bottom: 0;
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
        opacity: 0.4;
        transition: all 0.2s ease;
    }

    .bar-segment.selected-segment {
        opacity: 1 !important;
    }

    .bar-segment:hover {
        opacity: 0.7;
        cursor: pointer;
    }
    
    .count {
        color: #333;
        font-weight: 600;
        min-width: 25px;
        text-align: right;
        flex-shrink: 0;
    }

    .legend {
        display: flex;
        flex-direction: row;
        gap: 0.75rem;
        flex-wrap: wrap;
        margin-bottom: 1rem;
        row-gap: 0.25rem;
    }

    .legend-item {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        font-size: 0.875rem;
        opacity: 0.5;
        transition: opacity 0.3s ease;
    }

    .legend-item.selected {
        opacity: 1;
        font-weight: 600;
    }

    .legend-dot {
        width: 12px;
        height: 12px;
        border-radius: 50%;
        border: 1px solid #ccc;
        flex-shrink: 0;
    }

    .legend-item.selected .legend-dot {
        border-width: 2px;
        border-color: #333;
    }
</style>