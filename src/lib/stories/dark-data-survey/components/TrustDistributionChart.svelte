<script>
    import { 
        Heart, Users, Stethoscope, GraduationCap, Building, 
        FlaskConical, Briefcase, Shield, Smartphone, Store,
        Building2, UserX
    } from '@lucide/svelte';
    import { flip } from 'svelte/animate';
    
    let { filteredData, colorScale } = $props();

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
    
    // Institution color mapping for consistent visualization
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

<div class="trust-distribution-chart" style="width: {chartWidth}px; height: {chartHeight}px; transform">
    <!-- Chart title -->
    <div class="chart-title">Trust Level Distribution</div>
    
    <!-- Institution bars -->
    <div class="chart-content">
        {#each distributionData as item, i (item.institution)}
            {@const maxBarWidth = 130}
            {@const barWidth = Math.max(2, (Number(item.distance) / maxDistance) * maxBarWidth)}
            {@const IconComponent = institutionIcons[item.institution] || UserX}
            {@const name = item.institution.replace('TP_', '').replace(/_/g, ' ')}

            <div class="institution-row"
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
                        style="width: {barWidth}px; background-color: {institutionColors[item.institution] || '#6b7280'}; transition: width 0.5s ease, background-color 0.5s ease;"
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
        width: 130px;
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