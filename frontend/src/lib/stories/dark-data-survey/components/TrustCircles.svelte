<script>
    let { 
        width, 
        height, 
        filteredCircles, 
        scrollyIndex, 
        centerX, 
        centerY, 
        radiusScale, 
        institutionColors, 
        highlightCircle 
    } = $props();
</script>

<g class="trust-circles">
    {#each filteredCircles as circle}
        <circle
            cx={centerX}
            cy={centerY}
            r={radiusScale(circle.distance)}
            fill="none"
            stroke={institutionColors[circle.institution] || '#6b7280'}
            stroke-width={circle.institution === highlightCircle ? "5.0" : "2.0"}
            stroke-dasharray={circle.value === 0 ? "8,4" : "none"}
            opacity={circle.institution === highlightCircle ? "1.0" : "0.6"}
            style="transition: r 0.8s ease-in-out; pointer-events: none;"
        />
    {/each}
</g>

