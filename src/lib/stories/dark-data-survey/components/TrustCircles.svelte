<script>
    let { distances, centerX, centerY, maxRadius } = $props();
</script>
<g class="trust-circles">
    {#each distances as distance}
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