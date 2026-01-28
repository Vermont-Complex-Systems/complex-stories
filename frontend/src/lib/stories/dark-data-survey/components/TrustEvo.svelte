<script>
    import { scaleSequential, scaleLinear, scaleOrdinal } from 'd3-scale';
    import { interpolateRdYlGn } from 'd3-scale-chromatic';
    import { extent } from 'd3-array';
    
    import TrustDistributionChart from './TrustDistributionChart.svelte';
    import ACESSlider from './ACESSlider.svelte';
    import { institutionColorMap, getInstitutionColor } from '../utils/institutionColors.js';


    let {
        data,
        scrollyIndex,
        width,
        height,
        isStorySection = false,
        isDashboard = false,
        storySection,
        conclusionVisible = false,
        externalCategory = undefined,
        externalHighlight = undefined,
        onInstitutionClick = undefined,
        showACESSlider = false,
        acesValue = $bindable(0)
    } = $props();

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
    
    // Manual filter controls for interactive phase
    let selectedDemCategory = $state('Dem_Gender_Woman');
    let highlightCircle = $state("");

    // Available demographic values in new format:
    // - Dem_Gender_Woman, Dem_Gender_Man, Dem_Gender_Other
    // - ACES_No, ACES_Yes (ACES_Compound exists in data but not used in storytelling)
    $effect(() => {
        // If external props are provided (dashboard mode), use those instead of scrollyIndex
        if (externalCategory !== undefined) {
            selectedDemCategory = externalCategory;
            highlightCircle = externalHighlight || "";
            return;
        }

        // Otherwise use scrollyIndex to control state
        switch (scrollyIndex) {
            // missing cases default to Dem_Gender_Woman baseline
            case 1:
                selectedDemCategory = 'Dem_Gender_Woman';
                highlightCircle = "TP_Platform";
                break;
            case 2:
                selectedDemCategory = 'Dem_Gender_Woman';
                highlightCircle = "TP_Platform";
                break;
            case 3:
                selectedDemCategory = 'Dem_Gender_Man';
                highlightCircle = "TP_Platform";
                break;
            case 4:
                selectedDemCategory = 'Dem_Gender_Woman';
                highlightCircle = "";
                break;
            case 5:
                selectedDemCategory = 'Dem_Gender_Woman';
                highlightCircle = "TP_Medical";
                break;
            case 6:
                selectedDemCategory = 'Dem_Gender_Man';
                highlightCircle = "TP_Medical";
                break;
            case 7:
                selectedDemCategory = 'Dem_Gender_Woman';
                highlightCircle = "";
                break;
            case 8:
                selectedDemCategory = 'Dem_Gender_Man';
                highlightCircle = "TP_Police";
                break;
            case 9:
                selectedDemCategory = 'Dem_Gender_Other';
                highlightCircle = "TP_Police";
                break;
            case 10:
                selectedDemCategory = 'Dem_Gender_Woman';
                highlightCircle = "";
                break;
            case 11:
                selectedDemCategory = 'ACES_0.0';
                acesValue = 0.0;
                highlightCircle = "TP_Relative";
                break;
            case 12:
                selectedDemCategory = 'ACES_1.25';
                acesValue = 1.25;
                highlightCircle = "TP_Relative";
                break;
            case 13:
                selectedDemCategory = 'ACES_2.25';
                acesValue = 2.25;
                highlightCircle = "TP_Relative";
                break;
            case 14:
                selectedDemCategory = 'ACES_4.25';
                acesValue = 4.25;
                highlightCircle = "TP_Relative";
                break;
            case 15:
                selectedDemCategory = 'ACES_5.25+';
                acesValue = 5.25;
                highlightCircle = "TP_Relative";
                break;
            default:
                selectedDemCategory = 'Dem_Gender_Woman';
                highlightCircle = "";
        }
    })
    
    // Simple filter - return new array (this is fine, flip doesn't depend on this)
    let filteredCircles = $derived.by(() =>
        data.filter((c) => c.Demographic == selectedDemCategory
        )
    )

    // TRUST CIRCLES PLOTTING ---

    // Use the responsive width/height from props
    // outerHeight is intentionally larger than viewport to maximize circle size
    const centerX = $derived(width / 2);
    const centerY = $derived(isDashboard ? height * 0.5 : height * 0.6);
    const maxRadius = $derived(isDashboard ? height * 0.95 : height * 0.43);
    
    const zScale = $derived(scaleSequential(interpolateRdYlGn).domain(extent(trust_circles.map(d=>d.Average_Trust))));
    
    // Likert scale from 1 to 7
    const radiusScale = $derived(scaleLinear().domain([1, 7]).range([50, maxRadius]));
    
    // Use shared institution color mapping
    const institutionColors = (institution) => getInstitutionColor(institution);

</script>


<div class="chart-wrapper">
     <div class="viz-content">
        <div class="plot-container" class:dashboard={isDashboard} style={isDashboard ? `height: ${height}px;` : ''}>
            <svg class="trust-visualization" viewBox={`0 0 ${width} ${height}`}>
                {#each filteredCircles as circle}
                    {@const isHighlighted = circle.Trust_Category === highlightCircle}
                    {@const hasHighlight = highlightCircle !== ""}
                    <circle
                        cx={centerX}
                        cy={centerY}
                        r={radiusScale(+circle.Average_Trust)}
                        fill="none"
                        stroke={institutionColors(circle.Trust_Category)}
                        stroke-width={isHighlighted ? "4.0" : "2.0"}
                        opacity={hasHighlight ? (isHighlighted ? "1.0" : "0.3") : "0.6"}
                        style="transition: r 0.8s ease-in-out, stroke-width 0.3s ease, opacity 0.3s ease; pointer-events: none;"
                    />
                {/each}
            </svg>
        </div>

        <!-- ACES Slider for interactive exploration -->
        {#if showACESSlider}
            <div class="aces-slider-overlay">
                <ACESSlider bind:value={acesValue} />
            </div>
        {/if}
        
        <!-- Trust Distribution Chart in bottom right - only during main scrolly story, NOT in dashboard -->
        {#if !isDashboard}
            <div class="chart-overlay"
                class:visible={isStorySection}
                class:fade-out={conclusionVisible}>
                <TrustDistributionChart filteredData={filteredCircles} colorScale={zScale} {highlightCircle} {onInstitutionClick} {isDashboard} />
            </div>
        {/if}
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
        overflow: visible;
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

    .plot-container.dashboard {
        width: 100%;
        height: auto;
        left: 0;
        transform: none;
    }
    
    .trust-visualization {
        width: 100%;
        height: 100%;
        position: absolute;
        top: 0;
        left: 0;
    }
    
    
    .data-panel-wrapper {
        pointer-events: none;
        opacity: 0;
        transition: opacity 0.6s ease;
    }

    .data-panel-wrapper.visible {
        pointer-events: auto;
        opacity: 1;
    }

    .data-panel-wrapper.fade-out {
        opacity: 0;
        pointer-events: none;
    }

    .data-panel-wrapper.dashboard {
        position: static;
        opacity: 1;
        pointer-events: auto;
        margin-bottom: 2rem;
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

    .chart-overlay.dashboard {
        position: static;
        transform: none;
        opacity: 1;
        pointer-events: auto;
        margin-bottom: 2rem;
        right: auto;
        bottom: auto;
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

    /* Mobile adjustments */
    @media (max-width: 768px) {
        .chart-overlay {
            display: none !important;
        }

        .plot-container {
            /* Center the circles better on mobile and position them lower */
            top: 20vh;
        }

        .trust-visualization {
            /* Ensure circles appear behind survey boxes */
            z-index: 0;
        }
    }

</style>