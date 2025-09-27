<script>
    import LegendSection from './LegendSection.svelte';
    import TrustDistributionBars from './TrustDistributionBars.svelte';
    import { X } from '@lucide/svelte';
    
    let { scrollyIndex, individualPoints, GENDER, INST } = $props();
    
    let isCollapsed = $state(false);
    
    function togglePanel() {
        isCollapsed = !isCollapsed;
    }
</script>

{#if scrollyIndex === 1 && individualPoints.length > 0}
    {@const firstPoint = individualPoints[0]}
    {@const distribution = firstPoint?.trustDistribution || {}}
    {@const demographicBreakdown = firstPoint?.demographicBreakdown || {}}
    {@const orientationRaceBreakdown = firstPoint?.orientationRaceBreakdown || {}}
    {@const currentDemo = firstPoint?.currentDemographic || 'Current Group'}
    
    <div class="data-panel" class:collapsed={isCollapsed} onclick={isCollapsed ? togglePanel : undefined}>
        <!-- Close button -->
        <button class="close-button" class:hidden={isCollapsed} onclick={(e) => { e.stopPropagation(); togglePanel(); }} aria-label="Hide panel">
            <X size={16} />
        </button>
        
        <div class="panel-content" class:hidden={isCollapsed}>
            <h3>{GENDER == 1 ? "Men" : "Women"}'s Trust in {INST}</h3>
            
            <LegendSection {demographicBreakdown} />
            
            <TrustDistributionBars {distribution} {firstPoint} {demographicBreakdown} {GENDER} />
        </div>
    </div>
{/if}

<style>
    .data-panel {
        position: fixed;
        top: 50%;
        left: 0;
        transform: translateY(-50%);
        background: rgba(30, 30, 30, 0.95);
        backdrop-filter: blur(10px);
        border-radius: 0 12px 12px 0;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        border: 1px solid rgba(60, 60, 60, 0.5);
        border-left: none;
        z-index: 1000;
        min-width: 320px;
        max-width: 380px;
        max-height: 85vh;
        overflow-y: auto;
        transition: all 0.3s ease-in-out;
        pointer-events: auto;
        padding: 1.5rem;
        color: #f3f4f6;
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
        background: rgba(220, 38, 38, 0.1);
        color: rgba(220, 38, 38, 0.8);
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
        background: rgba(220, 38, 38, 0.2);
        color: rgba(220, 38, 38, 1);
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
        color: #f3f4f6;
        text-align: center;
    }
</style>