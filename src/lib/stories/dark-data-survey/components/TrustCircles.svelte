<script>
    let { width, height, centerX, centerY } = $props();
    
    const maxRadius = Math.min(centerX, centerY) - 50;
    
    // Use the same trust distances as the People component
    const trustDistances = {
        'friend': 0.2,
        'medical': 0.3,
        'relative': 0.35,
        'researcher': 0.4,
        'employer': 0.45,
        'school': 0.5,
        'non_profit': 0.55,
        'acquaintance': 0.6,
        'neighbor': 0.6,
        'worker': 0.65,
        'financial': 0.7,
        'government': 0.75,
        'company_customer': 0.8,
        'police': 0.85,
        'social_media_platform': 0.9,
        'company_not_customer': 0.95,
        'stranger': 1.0
    };
    
    // Get unique distance levels for circles
    const uniqueDistances = [...new Set(Object.values(trustDistances))].sort((a, b) => a - b);
</script>

<g class="trust-circles">
    {#each uniqueDistances as distance}
        <circle
            cx={centerX}
            cy={centerY}
            r={distance * maxRadius}
            fill="none"
            stroke="#d1d5db"
            stroke-width="1"
            stroke-dasharray="4,4"
            opacity="0.5"
        />
    {/each}
</g>