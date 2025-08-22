<script>
    import { 
        Heart, Users, Stethoscope, GraduationCap, Building, 
        FlaskConical, Briefcase, Shield, Smartphone, Store,
        Building2, UserX
    } from '@lucide/svelte';
    
    let { people, selectedDemographic, trustworthinessColorScale } = $props();
    
    // Institution to icon mapping (same as People.svelte)
    const institutionIcons = {
        'friend': Heart,
        'relative': Users, 
        'medical': Stethoscope,
        'school': GraduationCap,
        'employer': Building,
        'researcher': FlaskConical,
        'worker': Briefcase,
        'police': Shield,
        'social_media_platform': Smartphone,
        'company_customer': Store,
        'company_not_customer': Building2,
        'acquaintance': Users,
        'neighbor': Users,
        'government': Building,
        'non_profit': Heart,
        'financial': Building2,
        'stranger': UserX
    };
    
    // Chart dimensions
    const chartWidth = 350;
    const chartHeight = 420; // Increased to accommodate all 17 institutions and legend
    const barHeight = 12;
    const barSpacing = 18;
    
    // Trust distances by demographic group (same as other components)
    const trustDistancesByDemographic = {
        all: {
            'friend': 0.15, 'relative': 0.18, 'medical': 0.22,
            'acquaintance': 0.35, 'neighbor': 0.38, 'researcher': 0.42,
            'non_profit': 0.45, 'school': 0.55, 'employer': 0.58,
            'worker': 0.62, 'financial': 0.70, 'government': 0.75,
            'company_customer': 0.78, 'police': 0.85, 
            'social_media_platform': 0.90, 'company_not_customer': 0.95,
            'stranger': 1.0
        },
        white_men: {
            'friend': 0.20, 'relative': 0.25, 'medical': 0.30,
            'acquaintance': 0.40, 'neighbor': 0.42, 'researcher': 0.45,
            'non_profit': 0.50, 'school': 0.48, 'employer': 0.46,
            'worker': 0.52, 'financial': 0.55, 'government': 0.60,
            'company_customer': 0.58, 'police': 0.65, 
            'social_media_platform': 0.75, 'company_not_customer': 0.80,
            'stranger': 0.85
        },
        black_women: {
            'friend': 0.12, 'relative': 0.10, 'medical': 0.45,
            'acquaintance': 0.25, 'neighbor': 0.22, 'researcher': 0.50,
            'non_profit': 0.30, 'school': 0.55, 'employer': 0.65,
            'worker': 0.40, 'financial': 0.80, 'government': 0.90,
            'company_customer': 0.85, 'police': 0.95, 
            'social_media_platform': 0.88, 'company_not_customer': 0.98,
            'stranger': 1.0
        }
    };
    
    // Calculate trust distribution data
    const distributionData = $derived(() => {
        if (!people || people.length === 0) return [];
        
        // Filter people based on selected demographic
        const filtered = people.filter(person => {
            return person.demographic === selectedDemographic;
        });
        
        // Get trust distances for current demographic
        const trustDistances = trustDistancesByDemographic[selectedDemographic] || trustDistancesByDemographic.all;
        
        // Group by institution
        const institutionGroups = {};
        filtered.forEach(person => {
            if (!institutionGroups[person.institution]) {
                institutionGroups[person.institution] = {
                    name: person.label,
                    total: 0,
                    trustCounts: [0, 0, 0, 0, 0, 0, 0] // indices 0-6 for trust levels 1-7
                };
            }
            institutionGroups[person.institution].total += 1;
            institutionGroups[person.institution].trustCounts[person.trustworthiness - 1] += 1;
        });
        
        // Convert to array and sort by trust distance (closest to furthest)
        return Object.entries(institutionGroups)
            .map(([institution, data]) => ({
                ...data,
                institution,
                trustDistance: trustDistances[institution] || 1.0
            }))
            .sort((a, b) => a.trustDistance - b.trustDistance); // Sort by distance (closest first) - show all institutions
    });
</script>

<svg width={chartWidth} height={chartHeight} class="trust-distribution-chart">
    <!-- Chart background -->
    <rect
        x="0"
        y="0"
        width={chartWidth}
        height={chartHeight}
        fill="rgba(255, 255, 255, 0.95)"
        stroke="rgba(0, 0, 0, 0.1)"
        stroke-width="1"
        rx="4"
    />
    
    <!-- Chart title -->
    <text
        x={chartWidth / 2}
        y="20"
        text-anchor="middle"
        font-size="12px"
        font-weight="600"
        fill="#374151"
        font-family="var(--sans)"
    >
        Trust Level Distribution
    </text>
    
    <!-- Institution bars -->
    {#each distributionData() as institution, i}
        {@const yPos = 40 + i * barSpacing}
        {@const maxBarWidth = 200}
        
        <!-- Institution icon -->
        {@const IconComponent = institutionIcons[institution.institution] || UserX}
        <foreignObject
            x="10"
            y={yPos + barHeight / 2 - 6}
            width="12"
            height="12"
        >
            <div style="width: 12px; height: 12px; display: flex; align-items: center; justify-content: center;">
                <IconComponent size="10" fill="#6b7280" stroke="none" />
            </div>
        </foreignObject>
        
        <!-- Institution name -->
        <text
            x="26"
            y={yPos + barHeight / 2}
            text-anchor="start"
            dominant-baseline="central"
            font-size="9px"
            fill="#6b7280"
            font-family="var(--sans)"
        >
            {institution.name}
        </text>
        
        <!-- Stacked bar segments -->
        {#each institution.trustCounts as count, trustLevel}
            {@const proportion = count / institution.total}
            {@const segmentWidth = proportion * maxBarWidth}
            {@const prevProportions = institution.trustCounts.slice(0, trustLevel).reduce((sum, c) => sum + c/institution.total, 0)}
            {@const xPos = 120 + prevProportions * maxBarWidth}
            
            {#if count > 0}
                <rect
                    x={xPos}
                    y={yPos}
                    width={segmentWidth}
                    height={barHeight}
                    fill={trustworthinessColorScale(trustLevel + 1)}
                    opacity="0.8"
                    style="transition: all 0.6s ease-in-out;"
                />
            {/if}
        {/each}
        
        <!-- Total count label -->
        <text
            x="330"
            y={yPos + barHeight / 2}
            text-anchor="end"
            dominant-baseline="central"
            font-size="8px"
            fill="#6b7280"
            font-family="var(--sans)"
        >
            {institution.total}
        </text>
    {/each}
    
    <!-- Legend for trust levels -->
    <g transform="translate(10, {chartHeight - 50})">
        <text
            x="0"
            y="0"
            font-size="9px"
            font-weight="600"
            fill="#374151"
            font-family="var(--sans)"
        >
            Trust Level:
        </text>
        
        {#each [1, 4, 7] as level, i}
            <rect
                x={i * 80 + 10}
                y="8"
                width="12"
                height="8"
                fill={trustworthinessColorScale(level)}
                opacity="0.8"
            />
            <text
                x={i * 80 + 25}
                y="14"
                font-size="8px"
                fill="#6b7280"
                font-family="var(--sans)"
            >
                {level === 1 ? 'Low (1)' : level === 4 ? 'Med (4)' : 'High (7)'}
            </text>
        {/each}
    </g>
</svg>

<style>
    .trust-distribution-chart {
        background: white;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        border: 1px solid rgba(0, 0, 0, 0.1);
    }
</style>