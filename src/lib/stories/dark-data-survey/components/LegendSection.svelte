<script>
    let { demographicBreakdown, selectedDemCategory } = $props();

    const categoryColors = {
        orientation_ord: {
            straight: "#8b5cf6",
            bisexual: "#06b6d4",
            gay: "#92400e",
            other: "#6b7280"
        },
        race_ord: {
            white: "#3b82f6",
            mixed: "#f59e0b",
            poc: "#ef4444"
        },
        gender_ord: {
            women: "#ec4899",
            men: "#3b82f6",
            other: "#6b7280"
        }
    };

    const categoryLabels = {
        orientation_ord: "Sexual Orientation",
        race_ord: "Race",
        gender_ord: "Gender"
    };

    const valueLabels = {
        orientation_ord: {
            straight: "Straight",
            bisexual: "Bisexual",
            gay: "Gay",
            other: "Other"
        },
        race_ord: {
            white: "White",
            mixed: "Mixed",
            poc: "POC"
        },
        gender_ord: {
            women: "Women",
            men: "Men",
            other: "Other"
        }
    };

    // Determine which categories to show (those present in demographicBreakdown)
    const categoriesToShow = $derived(
        Object.keys(demographicBreakdown).filter(key =>
            key !== 'total' && typeof demographicBreakdown[key] === 'object'
        )
    );
</script>

{#each categoriesToShow as category}
    {#if categoryColors[category]}
        <div class="section">
            <h4>{categoryLabels[category]} Legend</h4>
            <div class="legend">
                {#each Object.entries(demographicBreakdown[category]) as [key, count]}
                    <div class="legend-item">
                        <div class="legend-dot" style="background-color: {categoryColors[category][key] || '#6b7280'};"></div>
                        <span>{valueLabels[category][key] || key} ({count})</span>
                    </div>
                {/each}
            </div>
        </div>
    {/if}
{/each}

<style>
    .section {
        margin-bottom: 1rem;
    }

    .section:last-child {
        margin-bottom: 0;
    }

    .section h4 {
        margin: 0 0 0.5rem 0;
        font-size: 0.875rem;
        font-weight: 600;
        color: #333;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    .legend {
        display: flex;
        color: #333;
        flex-direction: row;
        gap: 1rem;
        flex-wrap: wrap;
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
        border: 1px solid #ccc;
        flex-shrink: 0;
    }
</style>
