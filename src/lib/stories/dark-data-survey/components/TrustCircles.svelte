<script>
    let { width, height, centerX, centerY, selectedDemographic } = $props();
    
    const maxRadius = Math.min(centerX, centerY) - 50;
    
    // Define trust distance levels for each demographic group (same as People component)
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
    
    // Get trust distances for current demographic and unique distances for circles
    const uniqueDistances = $derived(() => {
        const trustDistances = trustDistancesByDemographic[selectedDemographic] || trustDistancesByDemographic.all;
        return [...new Set(Object.values(trustDistances))].sort((a, b) => a - b);
    });
</script>

<g class="trust-circles">
    {#each uniqueDistances() as distance}
        <circle
            cx={centerX}
            cy={centerY}
            r={distance * maxRadius}
            fill="none"
            stroke="#d1d5db"
            stroke-width="1"
            stroke-dasharray="4,4"
            opacity="0.9"
            style="transition: r 0.8s ease-in-out;"
        />
    {/each}
</g>