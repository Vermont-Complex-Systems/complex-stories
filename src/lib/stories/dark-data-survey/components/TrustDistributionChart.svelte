<script>
    let { people, selectedGender, selectedEthnicity, trustworthinessColorScale, x = 600, y = 450 } = $props();
    
    // Chart dimensions
    const chartWidth = 350;
    const chartHeight = 300;
    const barHeight = 12;
    const barSpacing = 18;
    
    // Calculate trust distribution data
    const distributionData = $derived(() => {
        if (!people || people.length === 0) return [];
        
        // Filter people based on selected criteria
        const filtered = people.filter(person => {
            const genderMatch = selectedGender === 'all' || person.gender === selectedGender;
            const ethnicityMatch = selectedEthnicity === 'all' || person.ethnicity === selectedEthnicity;
            return genderMatch && ethnicityMatch;
        });
        
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
        
        // Convert to array and sort by total count (descending)
        return Object.values(institutionGroups)
            .sort((a, b) => b.total - a.total)
            .slice(0, 10); // Show top 10 institutions
    });
</script>

<g class="trust-distribution-chart" transform="translate({x}, {y})">
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
    {#each distributionData as institution, i}
        {@const yPos = 40 + i * barSpacing}
        {@const maxBarWidth = 200}
        
        <!-- Institution name -->
        <text
            x="10"
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
    <g transform="translate(10, {chartHeight - 60})">
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
</g>