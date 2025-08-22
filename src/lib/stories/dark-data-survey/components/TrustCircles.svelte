<script>
    let { width, height, centerX, centerY } = $props();
    
    const maxRadius = Math.min(centerX, centerY) - 50;
    
    // Use the same trust distances as the People component
    // Personal relationships are much closer, formal institutions are further out
    const trustDistances = {
        // Close personal circle
        'friend': 0.15,
        'relative': 0.18,
        'medical': 0.22,
        
        // Semi-personal/professional
        'acquaintance': 0.35,
        'neighbor': 0.38,
        'researcher': 0.42,
        'non_profit': 0.45,
        
        // Formal institutions (closer)
        'school': 0.55,
        'employer': 0.58,
        'worker': 0.62,
        
        // Formal institutions (moderate distance)
        'financial': 0.70,
        'government': 0.75,
        'company_customer': 0.78,
        
        // Distant/untrusted institutions
        'police': 0.85,
        'social_media_platform': 0.90,
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
            opacity="0.9"
        />
    {/each}
</g>