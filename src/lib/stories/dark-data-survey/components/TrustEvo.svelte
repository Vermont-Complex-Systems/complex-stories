<script>
    import { scaleSequential, scaleLinear } from 'd3-scale';
    import { interpolateRdYlGn } from 'd3-scale-chromatic';
    import { extent } from 'd3-array';
    
    import TrustDistributionChart from './TrustDistributionChart.svelte';
    import trust_circles from '../data/trust_circles.csv';
    import trust_circles_individual from '../data/trust_circles_individual.csv';
    

    let { scrollyIndex, selectedDemographic, width, height, isStorySection = false, storySection, conclusionVisible = false } = $props();
    
    // Track if story section is in viewport
    let storySectionVisible = $state(false);
    
    const TIMEPOINT = 1;
    const GENDER = 0; // 0=Women/1=Men
    const INST = "TP_Gov";
    
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
                orientationShape: orientationValue === "0" ? 'circle' : 
                                orientationValue === "1" ? 'square' : 
                                orientationValue === "2" ? 'triangle' : 
                                orientationValue === "3" ? 'diamond' : 'circle',
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
        {#if isInteractivePhase}
            <div class="controls" style="pointer-events: auto; position: relative; z-index: 1000;">
                <label>
                    Category:
                    <select bind:value={selectedCategory}>
                        {#each categories as category}
                            <option value={category}>{category}</option>
                        {/each}
                    </select>
                </label>
                
                <label>
                    Value:
                    <select bind:value={selectedValue}>
                        {#each getValuesForCategory(selectedCategory) as value}
                            <option value={value.toString()}>{value}</option>
                        {/each}
                    </select>
                </label>
            </div>
        {:else}
            <div class="scrolly-info">
                <p>Currently showing: {currentCategory} = {currentValue}</p>
            </div>
        {/if}
        
        <div class="plot-container">
            <svg width={width} height={height} class="trust-visualization" viewBox={`0 0 ${width} ${height}`}>
                <!-- Background average circles (always visible as dotted lines) -->
                <g class="background-circles">
                    {#each backgroundCircles() as circle}
                        <circle
                            cx={centerX}
                            cy={centerY}
                            r={radiusScale(circle.distance)}
                            fill="none"
                            stroke={institutionColors[circle.institution] || '#cccccc'}
                            stroke-width={scrollyIndex === 1 && circle.institution == INST ? "5.0" : "1.0"}
                            stroke-dasharray="4,4"
                            opacity={scrollyIndex === 1 && circle.institution == INST ? "1.0" : "0.2"}
                        />
                    {/each}
                </g>
                
                <g class="trust-circles">
                    {#each filteredCircles() as circle}
                        {console.log(circle)}
                        <circle
                            cx={centerX}
                            cy={centerY}
                            r={radiusScale(circle.distance)}
                            fill="none"
                            stroke={institutionColors[circle.institution] || '#6b7280'}
                            stroke-width={scrollyIndex === 1 && circle.institution == INST ? "5.0" : "1.0"}
                            stroke-dasharray={circle.value === 0 ? "8,4" : "none"}
                            opacity={scrollyIndex === 1 && circle.institution == INST ? "1.0" : "0.2"}
                            style="transition: r 0.8s ease-in-out; pointer-events: none;"
                        />
                    {/each}
                </g>
                
                <!-- Individual data points for scrollyIndex 1 -->
                {#if scrollyIndex === 1}
                    <g class="individual-points">
                        {#each individualPoints() as point}
                            
                            {#if point.orientationShape === 'circle'}
                                <!-- Straight - Circle -->
                                <circle
                                    cx={point.x}
                                    cy={point.y}
                                    r="6"
                                    fill={point.raceColor}
                                    opacity="0.8"
                                    stroke="white"
                                    stroke-width="1.5"
                                />
                            {:else if point.orientationShape === 'square'}
                                <!-- Bisexual - Square -->
                                <rect
                                    x={point.x - 5}
                                    y={point.y - 5}
                                    width="10"
                                    height="10"
                                    fill={point.raceColor}
                                    opacity="0.8"
                                    stroke="white"
                                    stroke-width="1.5"
                                />
                            {:else if point.orientationShape === 'triangle'}
                                <!-- Gay - Triangle -->
                                <polygon
                                    points="{point.x},{point.y - 7} {point.x - 6},{point.y + 5} {point.x + 6},{point.y + 5}"
                                    fill={point.raceColor}
                                    opacity="0.8"
                                    stroke="white"
                                    stroke-width="1.5"
                                />
                            {:else if point.orientationShape === 'diamond'}
                                <!-- Other - Diamond -->
                                <polygon
                                    points="{point.x},{point.y - 6} {point.x + 6},{point.y} {point.x},{point.y + 6} {point.x - 6},{point.y}"
                                    fill={point.raceColor}
                                    opacity="0.8"
                                    stroke="white"
                                    stroke-width="1.5"
                                />
                            {:else}
                                <!-- Fallback - Circle -->
                                <circle
                                    cx={point.x}
                                    cy={point.y}
                                    r="6"
                                    fill={point.raceColor}
                                    opacity="0.8"
                                    stroke="white"
                                    stroke-width="1.5"
                                />
                            {/if}
                        {/each}
                    </g>
                {/if}                
            </svg>
        </div>
        
        
        <!-- Data distribution panel for scrollyIndex 1 -->
        {#if scrollyIndex === 1 && individualPoints().length > 0}
            {@const firstPoint = individualPoints()[0]}
            {@const distribution = firstPoint?.trustDistribution || {}}
            {@const demographicBreakdown = firstPoint?.demographicBreakdown || {}}
            {@const orientationRaceBreakdown = firstPoint?.orientationRaceBreakdown || {}}
            {@const currentDemo = firstPoint?.currentDemographic || 'Current Group'}
            {@const raceColors = {
                "0": "#3b82f6", // Blue for white
                "1": "#f59e0b", // Amber for mixed  
                "2": "#ef4444"  // Red for poc
            }}
            <div class="data-panel">
                <h3>{GENDER == 1 ? "Men" : "Women"}'s Trust in {INST}</h3>
                
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

                <!-- Sexual orientation shape legend -->
                <div class="section">
                    <h4>Orientation (Shape) Legend</h4>
                    
                    <div class="orientation-breakdown">
                        <div class="orientation-item">
                            {#if (orientationRaceBreakdown["0"]?.white + orientationRaceBreakdown["0"]?.mixed + orientationRaceBreakdown["0"]?.poc) > 0}
                                {@const straightTotal = orientationRaceBreakdown["0"].white + orientationRaceBreakdown["0"].mixed + orientationRaceBreakdown["0"].poc}
                                <div class="trust-level-row">
                                    <div class="level-info">
                                        <svg width="14" height="14" style="flex-shrink: 0;">
                                            <circle cx="7" cy="7" r="5" fill="#8b5cf6" stroke="white" stroke-width="1"/>
                                        </svg>
                                        <span>Straight</span>
                                    </div>
                                    <div class="bar-container">
                                        <div class="stacked-bar">
                                            {#if orientationRaceBreakdown["0"].white > 0}
                                                <div class="bar-segment" 
                                                     style="width: {(orientationRaceBreakdown['0'].white / straightTotal) * 100}%; background-color: {raceColors['0']}"
                                                     title="White: {orientationRaceBreakdown['0'].white}">
                                                </div>
                                            {/if}
                                            {#if orientationRaceBreakdown["0"].mixed > 0}
                                                <div class="bar-segment" 
                                                     style="width: {(orientationRaceBreakdown['0'].mixed / straightTotal) * 100}%; background-color: {raceColors['1']}"
                                                     title="Mixed: {orientationRaceBreakdown['0'].mixed}">
                                                </div>
                                            {/if}
                                            {#if orientationRaceBreakdown["0"].poc > 0}
                                                <div class="bar-segment" 
                                                     style="width: {(orientationRaceBreakdown['0'].poc / straightTotal) * 100}%; background-color: {raceColors['2']}"
                                                     title="POC: {orientationRaceBreakdown['0'].poc}">
                                                </div>
                                            {/if}
                                        </div>
                                    </div>
                                    <span class="count">{straightTotal}</span>
                                </div>
                            {/if}
                        </div>
                        
                        <div class="orientation-item">
                            {#if (orientationRaceBreakdown["1"]?.white + orientationRaceBreakdown["1"]?.mixed + orientationRaceBreakdown["1"]?.poc) > 0}
                                {@const bisexualTotal = orientationRaceBreakdown["1"].white + orientationRaceBreakdown["1"].mixed + orientationRaceBreakdown["1"].poc}
                                <div class="trust-level-row">
                                    <div class="level-info">
                                        <svg width="14" height="14" style="flex-shrink: 0;">
                                            <rect x="2" y="2" width="10" height="10" fill="#06b6d4" stroke="white" stroke-width="1"/>
                                        </svg>
                                        <span>Bisexual</span>
                                    </div>
                                    <div class="bar-container">
                                        <div class="stacked-bar">
                                            {#if orientationRaceBreakdown["1"].white > 0}
                                                <div class="bar-segment" 
                                                     style="width: {(orientationRaceBreakdown['1'].white / bisexualTotal) * 100}%; background-color: {raceColors['0']}"
                                                     title="White: {orientationRaceBreakdown['1'].white}">
                                                </div>
                                            {/if}
                                            {#if orientationRaceBreakdown["1"].mixed > 0}
                                                <div class="bar-segment" 
                                                     style="width: {(orientationRaceBreakdown['1'].mixed / bisexualTotal) * 100}%; background-color: {raceColors['1']}"
                                                     title="Mixed: {orientationRaceBreakdown['1'].mixed}">
                                                </div>
                                            {/if}
                                            {#if orientationRaceBreakdown["1"].poc > 0}
                                                <div class="bar-segment" 
                                                     style="width: {(orientationRaceBreakdown['1'].poc / bisexualTotal) * 100}%; background-color: {raceColors['2']}"
                                                     title="POC: {orientationRaceBreakdown['1'].poc}">
                                                </div>
                                            {/if}
                                        </div>
                                    </div>
                                    <span class="count">{bisexualTotal}</span>
                                </div>
                            {/if}
                        </div>
                        
                        <div class="orientation-item">
                            {#if (orientationRaceBreakdown["2"]?.white + orientationRaceBreakdown["2"]?.mixed + orientationRaceBreakdown["2"]?.poc) > 0}
                                {@const gayTotal = orientationRaceBreakdown["2"].white + orientationRaceBreakdown["2"].mixed + orientationRaceBreakdown["2"].poc}
                                <div class="trust-level-row">
                                    <div class="level-info">
                                        <svg width="14" height="14" style="flex-shrink: 0;">
                                            <polygon points="7,2 12,12 2,12" fill="#92400e" stroke="white" stroke-width="1"/>
                                        </svg>
                                        <span>Gay</span>
                                    </div>
                                    <div class="bar-container">
                                        <div class="stacked-bar">
                                            {#if orientationRaceBreakdown["2"].white > 0}
                                                <div class="bar-segment" 
                                                     style="width: {(orientationRaceBreakdown['2'].white / gayTotal) * 100}%; background-color: {raceColors['0']}"
                                                     title="White: {orientationRaceBreakdown['2'].white}">
                                                </div>
                                            {/if}
                                            {#if orientationRaceBreakdown["2"].mixed > 0}
                                                <div class="bar-segment" 
                                                     style="width: {(orientationRaceBreakdown['2'].mixed / gayTotal) * 100}%; background-color: {raceColors['1']}"
                                                     title="Mixed: {orientationRaceBreakdown['2'].mixed}">
                                                </div>
                                            {/if}
                                            {#if orientationRaceBreakdown["2"].poc > 0}
                                                <div class="bar-segment" 
                                                     style="width: {(orientationRaceBreakdown['2'].poc / gayTotal) * 100}%; background-color: {raceColors['2']}"
                                                     title="POC: {orientationRaceBreakdown['2'].poc}">
                                                </div>
                                            {/if}
                                        </div>
                                    </div>
                                    <span class="count">{gayTotal}</span>
                                </div>
                            {/if}
                        </div>
                        
                        <div class="orientation-item">
                            {#if (orientationRaceBreakdown["3"]?.white + orientationRaceBreakdown["3"]?.mixed + orientationRaceBreakdown["3"]?.poc) > 0}
                                {@const otherTotal = orientationRaceBreakdown["3"].white + orientationRaceBreakdown["3"].mixed + orientationRaceBreakdown["3"].poc}
                                <div class="trust-level-row">
                                    <div class="level-info">
                                        <svg width="14" height="14" style="flex-shrink: 0;">
                                            <polygon points="7,2 12,7 7,12 2,7" fill="#6b7280" stroke="white" stroke-width="1"/>
                                        </svg>
                                        <span>Other</span>
                                    </div>
                                    <div class="bar-container">
                                        <div class="stacked-bar">
                                            {#if orientationRaceBreakdown["3"].white > 0}
                                                <div class="bar-segment" 
                                                     style="width: {(orientationRaceBreakdown['3'].white / otherTotal) * 100}%; background-color: {raceColors['0']}"
                                                     title="White: {orientationRaceBreakdown['3'].white}">
                                                </div>
                                            {/if}
                                            {#if orientationRaceBreakdown["3"].mixed > 0}
                                                <div class="bar-segment" 
                                                     style="width: {(orientationRaceBreakdown['3'].mixed / otherTotal) * 100}%; background-color: {raceColors['1']}"
                                                     title="Mixed: {orientationRaceBreakdown['3'].mixed}">
                                                </div>
                                            {/if}
                                            {#if orientationRaceBreakdown["3"].poc > 0}
                                                <div class="bar-segment" 
                                                     style="width: {(orientationRaceBreakdown['3'].poc / otherTotal) * 100}%; background-color: {raceColors['2']}"
                                                     title="POC: {orientationRaceBreakdown['3'].poc}">
                                                </div>
                                            {/if}
                                        </div>
                                    </div>
                                    <span class="count">{otherTotal}</span>
                                </div>
                            {/if}
                        </div>
                    </div>
                </div>

                <!-- Current demographic trust distribution -->
                <div class="section">
                    <h4>Trust Distribution</h4>
                    
                    <!-- Stacked bar chart -->
                    <div class="trust-bars">
                        {#each Object.entries(distribution).sort(([a], [b]) => parseFloat(a) - parseFloat(b)) as [level, totalCount]}
                            {@const trustByOrientationData = firstPoint?.trustByOrientation || {}}
                            {@const maxCount = Math.max(...Object.values(distribution))}
                            {@const orientationColors = {
                                "0": "#8b5cf6", // Purple for straight
                                "1": "#06b6d4", // Cyan for bisexual  
                                "2": "#92400e", // Brown for gay
                                "3": "#6b7280"  // Grey for other
                            }}
                            {@const orientationData = trustByOrientationData[level] || {}}
                            {@const barWidth = (totalCount / maxCount) * 100}
                            
                            <div class="trust-level-row">
                                <span class="trust-label">Trust {level}:</span>
                                <div class="bar-container">
                                    <div class="stacked-bar" style="width: {barWidth}%">
                                        {#each Object.entries(orientationData) as [orientation, count]}
                                            {@const segmentWidth = (count / totalCount) * 100}
                                            <div 
                                                class="bar-segment" 
                                                style="width: {segmentWidth}%; background-color: {orientationColors[orientation] || '#6b7280'}"
                                                title="{orientation === '0' ? 'Straight' : orientation === '1' ? 'Bisexual' : orientation === '2' ? 'Gay' : 'Other'}: {count}"
                                            ></div>
                                        {/each}
                                    </div>
                                </div>
                                <span class="count">{totalCount}</span>
                            </div>
                        {/each}
                    </div>
                    
                    <div class="subtotal">
                        <strong>Total: {demographicBreakdown.gender_ord} {GENDER == 1 ? "Men" : "Women"}</strong>
                    </div>
                </div>
            </div>
        {/if}
        
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
    
    .controls {
        display: flex;
        gap: 1rem;
        margin-bottom: 1rem;
        padding: 1rem;
        background: rgba(255, 255, 255, 0.9);
        border-radius: 8px;
    }
    
    .controls label {
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
    }
    
    .controls select {
        padding: 0.5rem;
        border: 1px solid #ccc;
        border-radius: 4px;
    }
    
    .scrolly-info {
        padding: 1rem;
        text-align: center;
        font-weight: 500;
        color: var(--color-secondary-gray);
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
    
    .plot-container svg {
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
    
    .data-panel {
        position: fixed;
        top: 4rem;
        left: 2rem;
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        z-index: 1000;
        min-width: 280px;
        max-width: 350px;
        max-height: 80vh;
        overflow-y: auto;
        animation: fadeInRight 0.5s ease-out;
    }
    
    .data-panel h3 {
        margin: 0 0 1rem 0;
        font-size: 1rem;
        font-weight: 600;
        color: #374151;
        text-align: center;
    }
    
    .distribution-list {
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
        margin-bottom: 1rem;
    }
    
    .distribution-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 0.875rem;
    }
    
    .trust-level {
        color: #6b7280;
        font-weight: 500;
    }
    
    .count {
        color: #dc2626;
        font-weight: 600;
    }
    
    .total {
        padding-top: 0.75rem;
        border-top: 1px solid #e5e7eb;
        text-align: center;
        font-size: 0.875rem;
        color: #374151;
    }
    
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
        color: #374151;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .subtotal {
        padding-top: 0.5rem;
        border-top: 1px solid #e5e7eb;
        text-align: center;
        font-size: 0.8rem;
        color: #374151;
    }
    
    .breakdown-grid {
        display: flex;
        flex-direction: column;
        gap: 0.75rem;
    }
    
    .breakdown-category {
        border-left: 3px solid #e5e7eb;
        padding-left: 0.75rem;
    }
    
    .category-title {
        display: block;
        font-size: 0.8rem;
        font-weight: 600;
        color: #6b7280;
        margin-bottom: 0.25rem;
    }
    
    .category-items {
        display: flex;
        flex-direction: column;
        gap: 0.25rem;
    }
    
    .category-items span {
        font-size: 0.75rem;
        color: #374151;
        padding-left: 0.5rem;
    }
    
    .race-legend {
        display: flex;
        color: black;
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
        border: 1px solid black;
        flex-shrink: 0;
    }
    
    .orientation-breakdown {
        display: flex;
        flex-direction: column;
        gap: 1rem;
    }
    
    .orientation-item {
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
    }
    
    .orientation-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 1rem;
    }
    
    .orientation-header {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        font-size: 0.875rem;
        color: black;
    }
    
    .race-bar-container {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        height: 30px;
        width: 200px;
        flex-shrink: 0;
    }
    
    .race-bar-container .stacked-bar {
        height: 30px;
        width: 100%;
        display: flex;
        border: 1px solid #ddd;
        border-radius: 4px;
        overflow: hidden;
        background: #f5f5f5;
    }
    
    .race-bar-container .bar-segment {
        height: 100%;
        transition: all 0.2s ease;
        border-right: 1px solid rgba(255,255,255,0.5);
    }
    
    .race-bar-container .bar-segment:last-child {
        border-right: none;
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
        color: #6b7280;
        font-weight: 500;
        min-width: 60px;
        flex-shrink: 0;
    }
    
    .level-info {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        color: #374151;
        font-weight: 500;
        min-width: 80px;
        flex-shrink: 0;
    }
    
    .level-info span {
        color: #374151;
    }
    
    .bar-container {
        flex: 1;
        height: 16px;
        background: #f3f4f6;
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
        transition: all 0.2s ease;
    }
    
    .bar-segment:hover {
        opacity: 0.8;
        cursor: pointer;
    }
    
    .count {
        color: #374151;
        font-weight: 600;
        min-width: 25px;
        text-align: right;
        flex-shrink: 0;
    }
    
    
    @keyframes fadeInRight {
        from {
            opacity: 0;
            transform: translateX(20px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
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