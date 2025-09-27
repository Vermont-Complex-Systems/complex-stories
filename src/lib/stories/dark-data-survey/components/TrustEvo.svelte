<script>
    import { scaleSequential, scaleLinear } from 'd3-scale';
    import { interpolateRdYlGn } from 'd3-scale-chromatic';
    import { extent } from 'd3-array';
    
    import TrustDistributionChart from './TrustDistributionChart.svelte';
    import Controls from './Controls.svelte';
    import TrustCircles from './TrustCircles.svelte';
    import IndividualPoints from './IndividualPoints.svelte';
    import DataPanel from './DataPanel.svelte';
    import trust_circles from '../data/trust_circles.csv';
    import trust_circles_individual from '../data/trust_circles_individual.csv';
    

    let { scrollyIndex, selectedDemographic, width, height, isStorySection = false, storySection, conclusionVisible = false } = $props();
    
    // Track if story section is in viewport
    let storySectionVisible = $state(false);
    
    const TIMEPOINT = 4;
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
    
    // Phase detection - 1 baseline + 2 gender + 2 relationship + 4 orientation + 3 race = 12 total
    const isInteractivePhase = $derived(scrollyIndex >= 12);
    
    // Manual filter controls for interactive phase
    let selectedCategory = $state('overall_average');
    let selectedValue = $state("1.0");
    
    // Auto-select category based on scroll in phase 1
    const autoSelectedCategory = $derived(() => {
        if (scrollyIndex === 0) return 'overall_average';
        if (scrollyIndex === 1) return 'gender_ord'; 
        if (scrollyIndex === 2) return 'gender_ord';
        if (scrollyIndex === 3) return 'Dem_Relationship_Status_Single';
        if (scrollyIndex === 4) return 'Dem_Relationship_Status_Single';
        if (scrollyIndex === 5) return 'orientation_ord';
        if (scrollyIndex === 6) return 'orientation_ord';
        if (scrollyIndex === 7) return 'orientation_ord';
        if (scrollyIndex === 8) return 'orientation_ord';
        if (scrollyIndex === 9) return 'race_ord';
        if (scrollyIndex === 10) return 'race_ord';
        if (scrollyIndex === 11) return 'race_ord';
        return selectedCategory;
    });
    
    const autoSelectedValue = $derived(() => {
        if (scrollyIndex === 0) return "1.0"; // Overall average
        if (scrollyIndex === 1) return "1.0"; // Gender female (0)
        if (scrollyIndex === 2) return "1.0"; // Gender male (1)
        if (scrollyIndex === 3) return "0.0"; // Relationship not single (0)
        if (scrollyIndex === 4) return "1.0"; // Relationship single (1)
        if (scrollyIndex === 5) return "0.0"; // Orientation 0
        if (scrollyIndex === 6) return "1.0"; // Orientation 1
        if (scrollyIndex === 7) return "2.0"; // Orientation 2
        if (scrollyIndex === 8) return "3.0"; // Orientation 3
        if (scrollyIndex === 9) return "0.0"; // Race 0
        if (scrollyIndex === 10) return "1.0"; // Race 1
        if (scrollyIndex === 11) return "2.0"; // Race 2
        return selectedValue;
    });
    
    // Current active filters
    const currentCategory = $derived(isInteractivePhase ? selectedCategory : autoSelectedCategory());
    const currentValue = $derived(isInteractivePhase ? selectedValue : autoSelectedValue());
    
    // Get available categories and values
    const categories = [...new Set(trust_circles.map(d => d.category))];
    const getValuesForCategory = (cat) => [...new Set(trust_circles.filter(d => d.category === cat).map(d => d.value))];
    
    // Filtered data
    const filteredCircles = $derived(() => {
        const category = isInteractivePhase ? selectedCategory : autoSelectedCategory();
        const value = isInteractivePhase ? selectedValue : autoSelectedValue();
        
        return trust_circles.filter(d => 
            d.category === category && d.value.toString() === value && d.Timepoint == TIMEPOINT
        );
    });
    
    // Background average circles (always visible as dotted lines)
    const backgroundCircles = $derived(() => {
        return trust_circles.filter(d => 
            d.category === 'overall_average' && d.value.toString() === '1.0' && d.Timepoint == TIMEPOINT
        );
    });
    
    // Individual data points with demographic tracking
    const individualPoints = $derived(() => {
        if (scrollyIndex !== 1) return [];
        
        // For scrollyIndex 1, we want to show women's data
        // Filter for women AND police institution
        const filteredPoliceData = trust_circles_individual.filter(d => {
            return d.gender_ord == GENDER && d.institution === INST && d.Timepoint == TIMEPOINT;
        });

        // Count distribution by trust level for current demographic
        const trustDistribution = {};
        const trustByOrientation = {};
        
        filteredPoliceData.forEach(d => {
            const distance = parseFloat(d.distance);
            const orientation = d.orientation_ord.toString();
            
            // Overall trust distribution
            trustDistribution[distance] = (trustDistribution[distance] || 0) + 1;
            
            // Trust distribution by orientation
            if (!trustByOrientation[distance]) {
                trustByOrientation[distance] = {};
            }
            trustByOrientation[distance][orientation] = (trustByOrientation[distance][orientation] || 0) + 1;
        });
        
 
        const demographicBreakdown = {
            gender_ord: filteredPoliceData.length, // Total women count
            orientation: {
                straight: filteredPoliceData.filter(d => d.orientation_ord == 0).length,
                bisexual: filteredPoliceData.filter(d => d.orientation_ord == 1).length,
                gay: filteredPoliceData.filter(d => d.orientation_ord == 2).length,
                other: filteredPoliceData.filter(d => d.orientation_ord == 3).length
            },
            race: {
                white: filteredPoliceData.filter(d => d.race_ord == 0).length,
                mixed: filteredPoliceData.filter(d => d.race_ord == 1).length,
                poc: filteredPoliceData.filter(d => d.race_ord == 2).length
            }
        };
        
        const orientationRaceBreakdown = {
            "0": { // Straight
                white: filteredPoliceData.filter(d => d.orientation_ord == 0 && d.race_ord == 0).length,
                mixed: filteredPoliceData.filter(d => d.orientation_ord == 0 && d.race_ord == 1).length,
                poc: filteredPoliceData.filter(d => d.orientation_ord == 0 && d.race_ord == 2).length
            },
            "1": { // Bisexual
                white: filteredPoliceData.filter(d => d.orientation_ord == 1 && d.race_ord == 0).length,
                mixed: filteredPoliceData.filter(d => d.orientation_ord == 1 && d.race_ord == 1).length,
                poc: filteredPoliceData.filter(d => d.orientation_ord == 1 && d.race_ord == 2).length
            },
            "2": { // Gay
                white: filteredPoliceData.filter(d => d.orientation_ord == 2 && d.race_ord == 0).length,
                mixed: filteredPoliceData.filter(d => d.orientation_ord == 2 && d.race_ord == 1).length,
                poc: filteredPoliceData.filter(d => d.orientation_ord == 2 && d.race_ord == 2).length
            },
            "3": { // Other
                white: filteredPoliceData.filter(d => d.orientation_ord == 3 && d.race_ord == 0).length,
                mixed: filteredPoliceData.filter(d => d.orientation_ord == 3 && d.race_ord == 1).length,
                poc: filteredPoliceData.filter(d => d.orientation_ord == 3 && d.race_ord == 2).length
            }
        };
        
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
                raceColor: raceColors[raceValue] || '#6b7280', // Default gray if race not found
                raceLabel: raceValue === "0" ? 'White' : raceValue === "1" ? 'Mixed' : raceValue === "2" ? 'POC' : 'Unknown',
                orientationLabel: orientationValue === "0" ? 'Straight' : 
                                orientationValue === "1" ? 'Bisexual' : 
                                orientationValue === "2" ? 'Gay' : 
                                orientationValue === "3" ? 'Other' : 'Unknown',
                trustDistribution: trustDistribution,  // Distribution for current demographic
                trustByOrientation: trustByOrientation,  // Trust distribution broken down by orientation
                demographicBreakdown: demographicBreakdown, // All demographic breakdowns
                orientationRaceBreakdown: orientationRaceBreakdown, // Orientation broken down by race
                currentDemographic: GENDER == 1 ? "Men" : "Women"
            });
        });
        
        return positionedPoints;
    });
    
    const centerX = $derived(width / 2);
    const centerY = $derived(height / 2);
    const maxRadius = $derived(height * 0.4);
    
    const zScale = $derived(scaleSequential(interpolateRdYlGn)
        .domain(extent(trust_circles.map(d=>d.distance))));
    
    const radiusScale = $derived(scaleLinear()
        .domain([1, 7])  // Likert scale from 1 to 7
        .range([50, maxRadius]));
    
    // Institution color mapping for consistent visualization (same as bar chart)
    const institutionColors = {
        'TP_Friend': '#10b981',        // Green - high trust category
        'TP_Relative': '#059669',      // Dark green
        'TP_Medical': '#0891b2',       // Teal - professional services
        'TP_School': '#0284c7',        // Blue - educational
        'TP_Employer': '#7c3aed',      // Purple - work related
        'TP_Researcher': '#9333ea',    // Purple variant
        'TP_Co_worker': '#8b5cf6',     // Light purple
        'TP_Police': '#dc2626',        // Red - authority/government
        'TP_Platform': '#ea580c',      // Orange - tech platforms
        'TP_Company_cust': '#f59e0b',  // Amber - business
        'TP_Company_notcust': '#d97706', // Dark amber
        'TP_Acquaintance': '#6b7280',  // Gray - neutral relationships
        'TP_Neighbor': '#9ca3af',      // Light gray
        'TP_Gov': '#ef4444',           // Red - government
        'TP_NonProf': '#22c55e',       // Green - community
        'TP_Financial': '#f97316',     // Orange - financial
        'TP_Stranger': '#374151'       // Dark gray - unknown
    };
    
</script>

<div bind:clientWidth={width} bind:clientHeight={height} class="chart-wrapper">
     <div class="viz-content">
        <Controls 
            {isInteractivePhase} 
            bind:selectedCategory 
            bind:selectedValue 
            {categories} 
            {getValuesForCategory} 
            {currentCategory} 
            {currentValue} 
        />
        
        <div class="plot-container">
            <svg width={width} height={height} class="trust-visualization" viewBox={`0 0 ${width} ${height}`}>
                <TrustCircles 
                    {width} 
                    {height} 
                    filteredCircles={filteredCircles()} 
                    {scrollyIndex} 
                    {centerX} 
                    {centerY} 
                    {radiusScale} 
                    {institutionColors} 
                    {INST} 
                />
                
                <IndividualPoints {scrollyIndex} individualPoints={individualPoints()} />
            </svg>
        </div>
        
        
        <DataPanel {scrollyIndex} individualPoints={individualPoints()} {GENDER} {INST} />
        
        <!-- Trust Distribution Chart in bottom right - only during main scrolly story -->
        <div class="chart-overlay" 
             class:visible={isStorySection && typeof scrollyIndex === 'number' && scrollyIndex >= 0 && scrollyIndex <= 11 && filteredCircles().length > 0}
             class:fade-out={conclusionVisible}>
            {#if filteredCircles().length > 0}
                <TrustDistributionChart 
                    filteredData={filteredCircles()} 
                    colorScale={zScale} 
                    chosen_inst={INST}/>
            {/if}
        </div>
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
    
    .trust-visualization {
        width: 100%;
        height: 100%;
        position: absolute;
        top: 0;
        left: 0;
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