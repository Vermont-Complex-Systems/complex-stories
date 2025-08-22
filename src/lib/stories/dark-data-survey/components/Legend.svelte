<script>
    let { x = 50, y = 50, trustworthinessColorScale } = $props();
    
    // Create trustworthiness scale legend
    const trustworthinessLevels = [
        { level: 1, label: 'Very Low Trust' },
        { level: 2, label: 'Low Trust' },
        { level: 3, label: 'Somewhat Low Trust' },
        { level: 4, label: 'Neutral' },
        { level: 5, label: 'Somewhat High Trust' },
        { level: 6, label: 'High Trust' },
        { level: 7, label: 'Very High Trust' }
    ];
</script>

<g class="legend" transform="translate({x}, {y})">
    <!-- Legend title -->
    <text
        x="0"
        y="-5"
        font-size="13px"
        font-family="var(--sans)"
        font-weight="600"
        fill="#374151"
    >
        Trustworthiness Scale
    </text>
    
    {#each trustworthinessLevels as level, i}
        <g transform="translate(0, {i * 20 + 15})">
            <!-- Color circle -->
            <circle
                r="8"
                fill={trustworthinessColorScale(level.level)}
                stroke="rgba(0, 0, 0, 0.3)"
                stroke-width="1"
            />
            <!-- Level number -->
            <text
                x="0"
                y="2"
                text-anchor="middle"
                font-size="10px"
                font-family="var(--sans)"
                font-weight="600"
                fill="white"
            >
                {level.level}
            </text>
            <!-- Label -->
            <text
                x="18"
                y="4"
                font-size="11px"
                font-family="var(--sans)"
                fill="#374151"
            >
                {level.label}
            </text>
        </g>
    {/each}
</g>