<script>
    import { 
        Heart, Users, Stethoscope, GraduationCap, Building, 
        FlaskConical, Briefcase, Shield, Smartphone, Store,
        Building2, UserX
    } from '@lucide/svelte';
    import { flip } from 'svelte/animate';
    
    let { filteredData, colorScale, chosen_inst } = $props();
    
    // Institution to icon mapping - updated for new data format
    const institutionIcons = {
        'TP_Friend': Heart,
        'TP_Relative': Users, 
        'TP_Medical': Stethoscope,
        'TP_School': GraduationCap,
        'TP_Employer': Building,
        'TP_Researcher': FlaskConical,
        'TP_Co_worker': Briefcase,
        chosen_inst: Shield,
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
    
    // Calculate trust distribution data from filtered circles
    const distributionData = $derived(() => {
        if (!filteredData || filteredData.length === 0) return [];
        
        // Sort by distance (closest trust = lowest distance first)
        const sorted = [...filteredData].sort((a, b) => Number(a.distance) - Number(b.distance))
            .map(item => ({
                institution: item.institution,
                name: item.institution.replace('TP_', '').replace(/_/g, ' '),
                distance: Number(item.distance),
                trustLevel: Math.round(Number(item.distance)) // Approximate trust level from distance
            }));
        
        return sorted;
    });
    
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
        chosen_inst: '#dc2626',        // Red - authority/government
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
        {#each distributionData() as institution, i (institution.institution)}
            {@const maxBarWidth = 130}
            {@const barWidth = Math.max(2, (institution.distance / maxDistance) * maxBarWidth)}
            {@const IconComponent = institutionIcons[institution.institution] || UserX}
            
            <div class="institution-row" animate:flip={{ duration: 400 }}>
                <!-- Institution icon -->
                <div class="institution-icon" style="opacity: {institution.institution == chosen_inst ? 1.0 : 0.2};">
                    <IconComponent size="10" />
                </div>
                
                <!-- Institution name -->
                <div class="institution-name" style="opacity: {institution.institution == chosen_inst ? 1.0 : 0.2};">
                    {i+1} {institution.name}
                </div>
                
                <!-- Trust distance bar -->
                <div class="bar-container">
                    <!-- Grid lines for trust levels 1-7 -->
                    {#each [1, 2, 3, 4, 5, 6, 7] as gridValue}
                        {@const gridPosition = (gridValue / maxDistance) * maxBarWidth}
                        <div 
                            class="grid-line"
                            style="left: {gridPosition}px; opacity: {institution.institution == chosen_inst ? 1.0 : 0.2};"
                        ></div>
                    {/each}
                    
                    <div 
                        class="trust-bar"
                        style="width: {barWidth}px; background-color: {institutionColors[institution.institution] || '#6b7280'}; opacity: {institution.institution == chosen_inst ? 1.0 : 0.2};  transition: width 0.6s ease-out, background-color 0.6s ease-out;"
                    ></div>
                </div>
                
                <!-- Distance value label -->
                <div class="distance-value" style="opacity: {institution.institution == chosen_inst ? 1.0 : 0.2};">
                    {Number(institution.distance).toFixed(2)}
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
        display: flex;
        align-items: center;
        justify-content: flex-start;
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
        z-index: 2;
        position: relative;
    }
    
    .distance-value {
        width: 40px;
        text-align: right;
        font-size: 15px;
        color: whitesmoke;
    }
    
    .legend {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-top: 8px;
        font-size: 8px;
        color: whitesmoke;
    }
    
    .legend-title {
        font-size: 9px;
        font-weight: 600;
        color: #374151;
    }
    
    .legend-item {
        display: flex;
        align-items: center;
        gap: 4px;
    }
    
    .legend-color {
        width: 12px;
        height: 8px;
        border-radius: 2px;
        opacity: 0.8;
    }
</style>