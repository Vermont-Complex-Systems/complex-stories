<script>
    import LegendSection from './LegendSection.svelte';
    import TrustDistributionBars from './TrustDistributionBars.svelte';
    import { X } from '@lucide/svelte';
    import trust_circles_individual from '../data/trust_circles_individual.csv';

    let { scrollyIndex, GENDER, INST, isCollapsed = $bindable(true) } = $props();

    const TIMEPOINT = 4;

    // Compute filtered data for current demographic and institution
    const filteredPoliceData = $derived.by(() => {
        if (scrollyIndex !== 1) return [];
        return trust_circles_individual.filter(d =>
            d.gender_ord == GENDER && d.institution === INST && d.Timepoint == TIMEPOINT
        );
    });

    // Calculate trust distribution
    const trustDistribution = $derived.by(() => {
        const distribution = {};
        filteredPoliceData.forEach(d => {
            const distance = parseFloat(d.distance);
            distribution[distance] = (distribution[distance] || 0) + 1;
        });
        return distribution;
    });

    // Calculate trust by orientation
    const trustByOrientation = $derived.by(() => {
        const byOrientation = {};
        filteredPoliceData.forEach(d => {
            const distance = parseFloat(d.distance);
            const orientation = d.orientation_ord.toString();
            if (!byOrientation[distance]) {
                byOrientation[distance] = {};
            }
            byOrientation[distance][orientation] = (byOrientation[distance][orientation] || 0) + 1;
        });
        return byOrientation;
    });

    // Calculate demographic breakdown
    const demographicBreakdown = $derived.by(() => {
        const data = filteredPoliceData;
        return {
            gender_ord: data.length,
            orientation: {
                straight: data.filter(d => d.orientation_ord == 0).length,
                bisexual: data.filter(d => d.orientation_ord == 1).length,
                gay: data.filter(d => d.orientation_ord == 2).length,
                other: data.filter(d => d.orientation_ord == 3).length
            },
            race: {
                white: data.filter(d => d.race_ord == 0).length,
                mixed: data.filter(d => d.race_ord == 1).length,
                poc: data.filter(d => d.race_ord == 2).length
            }
        };
    });

    // Create a fake "firstPoint" object for compatibility with TrustDistributionBars
    const firstPoint = $derived.by(() => ({
        trustByOrientation: trustByOrientation
    }));

    function togglePanel() {
        isCollapsed = !isCollapsed;
    }
</script>

{#if scrollyIndex === 1 && filteredPoliceData.length > 0}

    <div class="data-panel" class:collapsed={isCollapsed} onclick={isCollapsed ? togglePanel : undefined}>
        <!-- Close button -->
        <button class="close-button" class:hidden={isCollapsed} onclick={(e) => { e.stopPropagation(); togglePanel(); }} aria-label="Hide panel">
            <X size={16} />
        </button>

        <div class="panel-content" class:hidden={isCollapsed}>
            <h3>{GENDER == 1 ? "Men" : "Women"}'s Trust in {INST}</h3>

            <LegendSection {demographicBreakdown} />

            <TrustDistributionBars distribution={trustDistribution} {firstPoint} demographicBreakdown={demographicBreakdown} {GENDER} />
        </div>
    </div>
{/if}

<style>
    .data-panel {
        position: fixed;
        top: 50%;
        left: 0;
        transform: translateY(-50%);
        background: white;
        border-radius: 0 8px 8px 0;
        box-shadow: 1px 1px 10px rgba(0, 0, 0, 0.2);
        z-index: 1000;
        min-width: 320px;
        max-width: 380px;
        max-height: 85vh;
        overflow-y: auto;
        transition: all 0.3s ease-in-out;
        pointer-events: auto;
        padding: 1.5rem;
        color: #333;
    }
    
    .data-panel.collapsed {
        transform: translateY(-50%) translateX(calc(-100% + 40px));
        cursor: pointer;
    }
    
    .data-panel.collapsed:hover {
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
</style>