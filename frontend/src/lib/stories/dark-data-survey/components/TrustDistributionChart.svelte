<script>
    import {
        Heart, Users, Stethoscope, GraduationCap, Building,
        FlaskConical, Briefcase, Shield, Smartphone, Store,
        Building2, UserX
    } from '@lucide/svelte';
    import { flip } from 'svelte/animate';
    import { getInstitutionColor } from '../utils/institutionColors.js';

    let { filteredData, colorScale, highlightCircle = "", onInstitutionClick = undefined, isDashboard = false } = $props();

    // Create a stable Map of institution objects
    const institutionMap = new Map();

    // Track sorted list in state - this array reference stays stable
    let distributionData = $state([]);

    // Initialize or update when filteredData changes
    $effect(() => {
        if (!filteredData || filteredData.length === 0) {
            distributionData = [];
            return;
        }

        // Defer to next frame so flip can measure current positions first
        requestAnimationFrame(() => {
            // Update or create institution objects in the map
            filteredData.forEach(item => {
                if (!institutionMap.has(item.institution)) {
                    institutionMap.set(item.institution, {
                        institution: item.institution,
                        distance: Number(item.distance)
                    });
                } else {
                    // Update distance on existing object
                    institutionMap.get(item.institution).distance = Number(item.distance);
                }
            });

            // Get objects from map and sort them - reuse existing objects
            const items = Array.from(institutionMap.values())
                .filter(item => filteredData.some(fd => fd.institution === item.institution));

            // Sort in place using the same object references
            items.sort((a, b) => a.distance - b.distance);

            // Update state array (triggers reactivity while keeping object refs)
            distributionData = items;
        });
    });

    // Institution to icon mapping - updated for new data format
    const institutionIcons = {
        'TP_Friend': Heart,
        'TP_Relative': Users, 
        'TP_Medical': Stethoscope,
        'TP_School': GraduationCap,
        'TP_Employer': Building,
        'TP_Researcher': FlaskConical,
        'TP_Co_worker': Briefcase,
        'TP_Police': Shield,
        'TP_Platform': Smartphone,
        'TP_Company_cust': Store,
        'TP_Company_notcust': Building2,
        'TP_Acquaintance': Users,
        'TP_Neighbor': Users,
        'TP_Gov': Building,
        'TP_NonProf': Heart,
        'TP_Financial': Building2,
        'TP_Stranger': UserX
    };
    
    // Chart dimensions
    const chartWidth = 350;
    const chartHeight = 500; // Increased to accommodate all 17 institutions and legend

    // Use fixed scale from 1 to 7 for consistency across demographic groups
    const maxDistance = 7;

    // Institution label mapping for display names
    const institutionLabels = {
        'TP_Gov': 'Government',
        'TP_Police': 'Police',
        'TP_Friend': 'Friend',
        'TP_Relative': 'Relative',
        'TP_Employer': 'Employer',
        'TP_Medical': 'Medical Professional',
        'TP_Financial': 'Financial Institution',
        'TP_Neighbor': 'Neighbor',
        'TP_Acquaintance': 'Acquaintance',
        'TP_Co_worker': 'Co-worker',
        'TP_School': 'School',
        'TP_Researcher': 'Researcher',
        'TP_Platform': 'Social Media Platform',
        'TP_NonProf': 'Non-Profit',
        'TP_Company_cust': 'Company (Customer)',
        'TP_Company_notcust': 'Company (Not Customer)',
        'TP_Stranger': 'Stranger'
    };
</script>

<div class="trust-distribution-chart" class:dashboard={isDashboard} style="width: {chartWidth}px; height: {chartHeight}px; transform">
    <!-- Chart title -->
    <div class="chart-title">Institution Trust Level</div>
    
    <!-- Institution bars -->
    <div class="chart-content">
        {#each distributionData as item, i (item.institution)}
            {@const maxBarWidth = 100}
            {@const barWidth = Math.max(2, (Number(item.distance) / maxDistance) * maxBarWidth)}
            {@const IconComponent = institutionIcons[item.institution] || UserX}
            {@const name = institutionLabels[item.institution] || item.institution.replace('TP_', '').replace(/_/g, ' ')}
            {@const isHighlighted = item.institution === highlightCircle}

            <div class="institution-row"
                 class:highlighted={isHighlighted}
                 class:clickable={onInstitutionClick !== undefined}
                 onclick={() => onInstitutionClick?.(item.institution)}
                 onkeydown={(e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); onInstitutionClick?.(item.institution); } }}
                 role={onInstitutionClick ? "button" : undefined}
                 tabindex={onInstitutionClick ? 0 : undefined}
                 aria-label={onInstitutionClick ? `Select ${name}` : undefined}
                 animate:flip={{ duration: 600 }}>
                <!-- Institution icon -->
                <div class="institution-icon">
                    <IconComponent size="10" />
                </div>

                <!-- Institution name -->
                <div class="institution-name">
                    {i+1} {name}
                </div>

                <!-- Trust distance bar -->
                <div class="bar-container">
                    <!-- Grid lines for trust levels 1-7 -->
                    {#each [1, 2, 3, 4, 5, 6, 7] as gridValue}
                        {@const gridPosition = (gridValue / maxDistance) * maxBarWidth}
                        <div
                            class="grid-line"
                            style="left: {gridPosition}px;"
                        ></div>
                    {/each}

                    <div
                        class="trust-bar"
                        style="width: {barWidth}px; background-color: {getInstitutionColor(item.institution)}; transition: width 0.5s ease, background-color 0.5s ease;"
                    ></div>
                </div>

                <!-- Distance value label -->
                <div class="distance-value">
                    {Number(item.distance).toFixed(2)}
                </div>
            </div>
        {/each}
    </div>
    
    
</div>

<style>
    .trust-distribution-chart {
        padding: 12px;
        font-family: var(--sans);
    }

    .chart-title {
        text-align: center;
        font-size: 15px;
        font-weight: 600;
        color: #374151;
        margin-bottom: 8px;
    }

    .chart-content {
        display: flex;
        flex-direction: column;
        gap: 10px;
    }

    .institution-row {
        display: flex;
        align-items: center;
        height: 14px;
        gap: 6px;
        transition: all 0.3s ease;
        opacity: 1;
    }

    .institution-row.clickable {
        cursor: pointer;
        padding: 2px 4px;
        margin: -2px -4px;
    }

    .institution-row.clickable:hover {
        background: rgba(255, 255, 255, 0.15);
        border-radius: 4px;
    }

    .institution-row.clickable:focus {
        outline: 2px solid rgba(255, 255, 255, 0.5);
        outline-offset: 2px;
        border-radius: 4px;
    }

    /* When ANY row is highlighted, dim the others */
    .chart-content:has(.highlighted) .institution-row:not(.highlighted) {
        opacity: 0.5;
    }

    .institution-row.highlighted {
        background: rgba(255, 255, 255, 0.2);
        border-radius: 4px;
        opacity: 1;
    }

    .institution-row.highlighted .institution-name,
    .institution-row.highlighted .distance-value {
        font-weight: 700;
        color: white;
    }

    .institution-row.highlighted .trust-bar {
        filter: brightness(1.2);
    }

    .institution-icon {
        width: 12px;
        height: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: whitesmoke;
    }

    .institution-name {
        width: 155px;
        font-size: 15px;
        color: whitesmoke;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        flex-shrink: 0;
    }

    .bar-container {
        flex: 1;
        height: 12px;
        position: relative;
        background: rgba(0, 0, 0, 0.05);
        border-radius: 2px;
    }

    .grid-line {
        position: absolute;
        top: 0;
        height: 100%;
        width: 1px;
        background: white;
        z-index: 1;
    }

    .trust-bar {
        height: 100%;
        border-radius: 2px;
        opacity: 0.8;
        position: relative;
        z-index: 2;
    }

    .distance-value {
        width: 40px;
        text-align: right;
        font-size: 15px;
        color: whitesmoke;
    }
</style>