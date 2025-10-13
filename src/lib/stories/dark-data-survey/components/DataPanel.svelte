<script>
    import TrustDistributionBars from './TrustDistributionBars.svelte';
    import { X } from '@lucide/svelte';
    // import trust_circles_individual from '../data/trust_circles_individual.csv';

    let { highlightCircle, selectedDemCategory, selectedValue, isDashboard = false, isCollapsed = $bindable(true) } = $props();

    const TIMEPOINT = 1;
    const trust_circles_individual = [];

    function togglePanel() {
        isCollapsed = !isCollapsed;
    }

    const categoryLabels = {
        'overall_average': 'Overall Average',
        'race_ord': 'Race',
        'gender_ord': 'Gender',
        'multi_platform_ord': 'Platform Usage',
        'Dem_Relationship_Status_Single': 'Relationship Status',
        'orientation_ord': 'Sexual Orientation',
        'ACES_Compound': 'Adverse Childhood Experiences'
    };

    const valueLabels = {
        'race_ord': { '0.0': 'White', '1.0': 'Mixed', '2.0': 'POC' },
        'gender_ord': { '0.0': 'Women', '1.0': 'Men', '2.0': 'Other' },
        'orientation_ord': { '0.0': 'Straight', '1.0': 'Bisexual', '2.0': 'Gay', '3.0': 'Other' },
        'multi_platform_ord': { '1.0': 'Single Platform', '2.0': '2 Platforms', '3.0': '3 Platforms', '4.0': '4 Platforms', '5.0': '5 Platforms' },
        'overall_average': { '1.0': 'All Users' }
    };

    const displayCategory = $derived(categoryLabels[selectedDemCategory] || selectedDemCategory);
    const displayValue = $derived(valueLabels[selectedDemCategory]?.[selectedValue] || selectedValue);
    const displayInstitution = $derived(highlightCircle || 'None');

    // Fetch data from server instead of importing CSV
    const trustData = $derived(await getTrustCirclesData({
        timepoint: TIMEPOINT,
        category: selectedDemCategory,
        value: selectedValue,
        institution: highlightCircle || undefined
    }));

    const selectedValueCount = $derived(trustData.count);
    const trustDistribution = $derived(trustData.distribution);
    const trustByCategory = $derived(trustData.byCategory);
    const demographicBreakdown = $derived.by(() => {
        const breakdown = trustData.breakdown;

        // Remove the category we're filtering by from the breakdown
        if (selectedDemCategory === 'race_ord') {
            delete breakdown.race;
        } else if (selectedDemCategory === 'gender_ord') {
            delete breakdown.gender;
        } else if (selectedDemCategory === 'orientation_ord') {
            delete breakdown.orientation;
        }

        return breakdown;
    });

    // Create a fake "firstPoint" object for compatibility with TrustDistributionBars
    const firstPoint = $derived.by(() => ({
        trustByOrientation: trustByCategory
    }));
</script>

<div class="data-panel" class:collapsed={isCollapsed} class:dashboard={isDashboard}
     style={isDashboard ? 'position: static !important; transform: none !important;' : ''}
     onclick={isCollapsed ? togglePanel : undefined}
     onkeydown={(e) => { if (isCollapsed && (e.key === 'Enter' || e.key === ' ')) { e.preventDefault(); togglePanel(); } }}
     role={isCollapsed ? "button" : undefined}
     tabindex={0}
     aria-label={isCollapsed ? "Expand panel" : undefined}>
    <!-- Close button -->
    <button class="close-button" class:hidden={isCollapsed} onclick={(e) => { e.stopPropagation(); togglePanel(); }} aria-label="Hide panel">
        <X size={16} />
    </button>

    <div class="panel-content" class:hidden={isCollapsed}>
        <h3>Detailed View</h3>

        <div class="info-row">
            <span class="label">Category:</span>
            <span class="value">{displayCategory}</span>
        </div>

        <div class="info-row">
            <span class="label">Highlighted:</span>
            <span class="value">{displayInstitution}</span>
        </div>

        {#if selectedValueCount > 0}
            <h4>Trust Distribution by {displayCategory}</h4>
            <div class="filter-info">Viewing: <strong>{displayValue}</strong> ({selectedValueCount} people)</div>
            <TrustDistributionBars
                distribution={trustDistribution}
                {firstPoint}
                {demographicBreakdown}
                {selectedDemCategory}
                {selectedValue} />
        {/if}
    </div>
</div>

<style>
    .data-panel {
        background: whitesmoke;
        box-shadow: 1px 1px 10px rgba(0, 0, 0, 0.2);
        overflow-y: auto;
        transition: all 0.3s ease-in-out;
        pointer-events: auto;
        padding: 1.5rem;
        color: #333;
    }

    /* Dashboard mode - MUST come first to avoid being overridden */
    .data-panel.dashboard {
        border-radius: 8px;
    }

    /* Default fixed positioning for scrolly story */
    .data-panel:not(.dashboard) {
        position: fixed;
        top: 50%;
        left: 0;
        transform: translateY(-50%);
        border-radius: 0 8px 8px 0;
        width: 300px;
        max-height: 85vh;
        z-index: 1000;
    }

    /* Collapsed state only for scrolly story */
    .data-panel:not(.dashboard).collapsed {
        transform: translateY(-50%) translateX(calc(-100% + 40px));
        cursor: pointer;
    }

    .data-panel:not(.dashboard).collapsed:hover {
        transform: translateY(-50%) translateX(calc(-100% + 50px));
    }

    .close-button {
        position: absolute;
        top: 1rem;
        right: 1rem;
        background: rgba(0, 0, 0, 0.05);
        color: #666;
        border: none;
        border-radius: 6px;
        width: 28px;
        height: 28px;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        transition: all 0.2s ease;
        z-index: 10;
    }

    .close-button:hover {
        background: rgba(0, 0, 0, 0.1);
        color: #333;
        transform: scale(1.05);
    }

    .panel-content {
        transition: opacity 0.3s ease;
    }

    .panel-content.hidden {
        opacity: 0;
        pointer-events: none;
    }

    .close-button.hidden {
        opacity: 0;
        pointer-events: none;
    }

    h3 {
        margin: 0 0 1rem 0;
        font-size: 1rem;
        font-weight: 600;
        color: #333;
        text-align: center;
    }

    .info-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .info-row:last-child {
        border-bottom: none;
    }

    .label {
        font-weight: 600;
        color: #666;
        font-size: 0.9rem;
    }

    .value {
        color: #333;
        font-size: 0.9rem;
    }

    .filter-info {
        font-size: 0.85rem;
        color: #666;
        margin-bottom: 0.75rem;
        text-align: center;
    }

    h4 {
        margin: 1rem 0 0.5rem 0;
        font-size: 0.95rem;
        font-weight: 600;
        color: #333;
        border-top: 1px solid rgba(0, 0, 0, 0.1);
        padding-top: 1rem;
        line-height: 1.2;    }

</style>
