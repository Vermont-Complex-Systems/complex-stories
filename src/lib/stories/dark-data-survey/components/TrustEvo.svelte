<script>
    import { scaleSequential, scaleLinear, scaleOrdinal } from 'd3-scale';
    import { interpolateRdYlGn } from 'd3-scale-chromatic';
    import { extent } from 'd3-array';
    
    import TrustDistributionChart from './TrustDistributionChart.svelte';
    import Controls from './Controls.svelte';
    import TrustCircles from './TrustCircles.svelte';
    import IndividualPoints from './IndividualPoints.svelte';
    import DataPanel from './DataPanel.svelte';
    import { institutionColorMap, getInstitutionColor } from '../utils/institutionColors.js';

    // load data
    import trust_circles from '../data/trust_circles.csv';
    import trust_circles_individual from '../data/trust_circles_individual.csv';

    let {
        scrollyIndex,
        selectedDemographic,
        width,
        height,
        isStorySection = false,
        isDashboard = false,
        storySection,
        conclusionVisible = false,
        externalCategory = undefined,
        externalValue = undefined,
        externalHighlight = undefined,
        onInstitutionClick = undefined
    } = $props();

    // Track if story section is in viewport
    let storySectionVisible = $state(false);

    // Track DataPanel collapse state
    let isCollapsed = $state(true);

    const TIMEPOINT = 1;
    const GENDER = 0; // 0=Women/1=Men
    const INST = "TP_Police";

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
    let selectedDemCategory = $state('overall_average');
    let selectedValue = $state("1.0");
    let highlightCircle = $state("");

    // Get available categories and values
    const categories = [...new Set(trust_circles.map(d => d.category))];
    const getValuesForCategory = (cat) => [...new Set(trust_circles.filter(d => d.category === cat).map(d => d.value))];

    // Available demographic categories and their values:
    // - overall_average: 1.0 (baseline)
    // - gender_ord: 0 (Women), 1 (Men)
    // - Dem_Relationship_Status_Single: 0 (Not Single), 1 (Single)
    // - orientation_ord: 0 (Straight), 1 (Bisexual), 2 (Gay), 3 (Other)
    // - race_ord: 0 (White), 1 (Mixed), 2 (POC)
    $effect(() => {
        // If external props are provided (dashboard mode), use those instead of scrollyIndex
        if (externalCategory !== undefined) {
            selectedDemCategory = externalCategory;
            selectedValue = externalValue || "1.0";
            highlightCircle = externalHighlight || "";
            return;
        }

        // Otherwise use scrollyIndex to control state
        switch (scrollyIndex) {
            // missing cases default to overall average.
            case 1:
                selectedDemCategory = 'overall_average';
                selectedValue = "1.0";
                highlightCircle = "TP_Platform";
                break;
            case 2:
                selectedDemCategory = 'multi_platform_ord';
                selectedValue = "1.0";
                highlightCircle = "TP_Platform";
                break;
            case 3:
                selectedDemCategory = 'multi_platform_ord';
                selectedValue = "4.0";
                highlightCircle = "TP_Platform";
                break;
            case 4:
                selectedDemCategory = 'overall_average';
                selectedValue = "1.0";
                highlightCircle = "";
                break;
            case 5:
                selectedDemCategory = 'orientation_ord';
                selectedValue = "0.0";
                highlightCircle = "TP_Police";
                break;
            case 6:
                selectedDemCategory = 'orientation_ord';
                selectedValue = "1.0";
                highlightCircle = "TP_Police";
                break;
            case 7:
                selectedDemCategory = 'orientation_ord';
                selectedValue = "0.0";
                highlightCircle = "TP_Relative";
                break;
            case 8:
                selectedDemCategory = 'orientation_ord';
                selectedValue = "1.0";
                highlightCircle = "TP_Relative";
                break;
            case 9:
                selectedDemCategory = 'overall_average';
                selectedValue = "1.0";
                highlightCircle = "";
                break;
            case 10:
                selectedDemCategory = 'ACES_Compound';
                selectedValue = "1.0";
                highlightCircle = "TP_Relative";
                break;
            case 11:
                selectedDemCategory = 'ACES_Compound';
                selectedValue = "8.0";
                highlightCircle = "TP_Relative";
                break;
            case 12:
                selectedDemCategory = 'ACES_Compound';
                selectedValue = "9.0";
                highlightCircle = "TP_Relative";
                break;
            case 13:
                selectedDemCategory = 'ACES_Compound';
                selectedValue = "9.0";
                highlightCircle = "TP_Acquaintance";
                break;
            case 14:
                selectedDemCategory = 'ACES_Compound';
                selectedValue = "9.0";
                highlightCircle = "TP_NonProf";
                break;
            default:
                selectedDemCategory = 'overall_average';
                selectedValue = "1.0";
                highlightCircle = "";
        }
    })
    
    // Simple filter - return new array (this is fine, flip doesn't depend on this)
    let filteredCircles = $derived.by(() =>
        trust_circles.filter((c) =>
            c.Timepoint == TIMEPOINT && 
                c.value == selectedValue && 
                c.category == selectedDemCategory
        )
    )
    
    // Individual data points for visualization
    const individualPoints = $derived(() => {
        if (scrollyIndex !== 1) return [];

        // Filter for current demographic and institution
        const filteredPoliceData = trust_circles_individual.filter(d => {
            return d.gender_ord == GENDER && d.institution === INST && d.Timepoint == TIMEPOINT;
        });

        // Position each point around the police trust circle
        const positionedPoints = [];

        // Race color mapping
        const raceColors = {
            0: '#3b82f6',  // Blue for White
            1: '#f59e0b',  // Amber for Mixed
            2: '#ef4444'   // Red for POC
        };

        filteredPoliceData.forEach((point, i) => {
            const distance = parseFloat(point.distance);
            const pointRadius = radiusScale(distance);
            const raceValue = point.race_ord;
            const orientationValue = point.orientation_ord;

            // Spread points evenly around the circle at the exact radius for their trust level
            const angle = (i / filteredPoliceData.length) * 2 * Math.PI;

            const x = centerX + Math.cos(angle) * pointRadius;
            const y = centerY + Math.sin(angle) * pointRadius;

            positionedPoints.push({
                ...point,
                x: x,
                y: y,
                baseRadius: pointRadius,
                trustLevel: distance,
                raceColor: raceColors[raceValue] || '#6b7280',
                raceLabel: raceValue === "0" ? 'White' : raceValue === "1" ? 'Mixed' : raceValue === "2" ? 'POC' : 'Unknown',
                orientationLabel: orientationValue === "0" ? 'Straight' :
                                orientationValue === "1" ? 'Bisexual' :
                                orientationValue === "2" ? 'Gay' :
                                orientationValue === "3" ? 'Other' : 'Unknown'
            });
        });

        return positionedPoints;
    });
    
    // TRUST CIRCLES PLOTTING ---

    // Use the responsive width/height from props
    // outerHeight is intentionally larger than viewport to maximize circle size
    const centerX = $derived(width / 2);
    const centerY = $derived(height * 0.6);
    const maxRadius = $derived(height * 0.43);
    
    const zScale = $derived(scaleSequential(interpolateRdYlGn).domain(extent(trust_circles.map(d=>d.distance))));
    
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
                    {@const isHighlighted = circle.institution === highlightCircle}
                    {@const hasHighlight = highlightCircle !== ""}
                    <circle
                        cx={centerX}
                        cy={centerY}
                        r={radiusScale(circle.distance)}
                        fill="none"
                        stroke={institutionColors(circle.institution)}
                        stroke-width={isHighlighted ? "4.0" : "2.0"}
                        opacity={hasHighlight ? (isHighlighted ? "1.0" : "0.3") : "0.6"}
                        style="transition: r 0.8s ease-in-out, stroke-width 0.3s ease, opacity 0.3s ease; pointer-events: none;"
                    />
                {/each}
                <!-- {#if scrollyIndex === 1 && !isCollapsed}
                    <IndividualPoints {scrollyIndex} individualPoints={individualPoints()} />
                {/if} -->
            </svg>
        </div>


        <!-- DataPanel - only during main scrolly story, NOT in dashboard -->
        {#if !isDashboard}
            <div class="data-panel-wrapper"
                class:visible={isStorySection}
                class:fade-out={conclusionVisible}>
                <DataPanel {highlightCircle} {selectedDemCategory} {selectedValue} {isDashboard} bind:isCollapsed />
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
    
    

</style>