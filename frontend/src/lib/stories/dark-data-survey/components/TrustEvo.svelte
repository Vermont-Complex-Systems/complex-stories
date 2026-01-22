<script>
    import { scaleSequential, scaleLinear, scaleOrdinal } from 'd3-scale';
    import { interpolateRdYlGn } from 'd3-scale-chromatic';
    import { extent } from 'd3-array';
    
    import TrustDistributionChart from './TrustDistributionChart.svelte';
    import Controls from './Controls.svelte';
    import TrustCircles from './TrustCircles.svelte';
    import IndividualPoints from './IndividualPoints.svelte';
    // import DataPanel from './DataPanel.svelte';
    import { institutionColorMap, getInstitutionColor } from '../utils/institutionColors.js';

    // load data
    import taste_for_privacy_raw from '../data/taste_for_privacy_aggregated.csv';
    // import trust_circles_individual from '../data/trust_circles_individual.csv';

    // Transform data: Demographic -> category, Trust_Category -> institution, Average_Trust -> distance
    // Add default Timepoint and value (using Demographic as value for now)
    const trust_circles = taste_for_privacy_raw.map(row => ({
        Timepoint: 1,
        institution: row.Trust_Category,
        distance: parseFloat(row.Average_Trust),
        category: row.Demographic,
        value: row.Demographic
    }));

    let {
        scrollyIndex,
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
    let selectedDemCategory = $state('Dem_Gender_Woman');
    let selectedValue = $state("Dem_Gender_Woman");
    let highlightCircle = $state("");

    // Get available categories and values
    const categories = [...new Set(trust_circles.map(d => d.category))];
    const getValuesForCategory = (cat) => [...new Set(trust_circles.filter(d => d.category === cat).map(d => d.value))];

    // Available demographic values in new format:
    // - Dem_Gender_Woman, Dem_Gender_Man, Dem_Gender_Other
    // - ACES_No, ACES_Yes (ACES_Compound exists in data but not used in storytelling)
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
            // missing cases default to Dem_Gender_Woman baseline
            case 1:
                selectedDemCategory = 'Dem_Gender_Woman';
                selectedValue = "Dem_Gender_Woman";
                highlightCircle = "TP_Platform";
                break;
            case 2:
                selectedDemCategory = 'Dem_Gender_Woman';
                selectedValue = "Dem_Gender_Woman";
                highlightCircle = "TP_Platform";
                break;
            case 3:
                selectedDemCategory = 'Dem_Gender_Man';
                selectedValue = "Dem_Gender_Man";
                highlightCircle = "TP_Platform";
                break;
            case 4:
                selectedDemCategory = 'Dem_Gender_Woman';
                selectedValue = "Dem_Gender_Woman";
                highlightCircle = "";
                break;
            case 5:
                selectedDemCategory = 'Dem_Gender_Woman';
                selectedValue = "Dem_Gender_Woman";
                highlightCircle = "TP_Medical";
                break;
            case 6:
                selectedDemCategory = 'Dem_Gender_Man';
                selectedValue = "Dem_Gender_Man";
                highlightCircle = "TP_Medical";
                break;
            case 7:
                selectedDemCategory = 'Dem_Gender_Woman';
                selectedValue = "Dem_Gender_Woman";
                highlightCircle = "";
                break;
            case 8:
                selectedDemCategory = 'Dem_Gender_Man';
                selectedValue = "Dem_Gender_Man";
                highlightCircle = "TP_Police";
                break;
            case 9:
                selectedDemCategory = 'Dem_Gender_Other';
                selectedValue = "Dem_Gender_Other";
                highlightCircle = "TP_Police";
                break;
            case 10:
                selectedDemCategory = 'Dem_Gender_Woman';
                selectedValue = "Dem_Gender_Woman";
                highlightCircle = "";
                break;
            case 11:
                selectedDemCategory = 'ACES_No';
                selectedValue = "ACES_No";
                highlightCircle = "TP_Relative";
                break;
            case 12:
                selectedDemCategory = 'ACES_Yes';
                selectedValue = "ACES_Yes";
                highlightCircle = "TP_Relative";
                break;
            case 13:
                selectedDemCategory = 'ACES_No';
                selectedValue = "ACES_No";
                highlightCircle = "TP_Medical";
                break;
            case 14:
                selectedDemCategory = 'ACES_Yes';
                selectedValue = "ACES_Yes";
                highlightCircle = "TP_Medical";
                break;
            case 15:
                selectedDemCategory = 'ACES_No';
                selectedValue = "ACES_No";
                highlightCircle = "TP_Police";
                break;
            case 16:
                selectedDemCategory = 'ACES_Yes';
                selectedValue = "ACES_Yes";
                highlightCircle = "TP_Police";
                break;
            case 17:
                selectedDemCategory = 'ACES_No';
                selectedValue = "ACES_No";
                highlightCircle = "TP_NonProf";
                break;
            case 18:
                selectedDemCategory = 'ACES_Yes';
                selectedValue = "ACES_Yes";
                highlightCircle = "TP_NonProf";
                break;
            default:
                selectedDemCategory = 'Dem_Gender_Woman';
                selectedValue = "Dem_Gender_Woman";
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
    const centerY = $derived(isDashboard ? height * 0.5 : height * 0.6);
    const maxRadius = $derived(isDashboard ? height * 0.95 : height * 0.43);
    
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
            </svg>
        </div>
        
        <!-- {#if scrollyIndex === 1 && !isCollapsed}
            <IndividualPoints {scrollyIndex} individualPoints={individualPoints()} />
        {/if} -->

        <!-- DataPanel - only during main scrolly story, NOT in dashboard -->
        <!-- {#if !isDashboard}
            <div class="data-panel-wrapper"
                class:visible={isStorySection}
                class:fade-out={conclusionVisible}>
                <DataPanel {highlightCircle} {selectedDemCategory} {selectedValue} {isDashboard} bind:isCollapsed />
            </div>
        {/if} -->

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