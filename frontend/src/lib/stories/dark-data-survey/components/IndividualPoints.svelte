<script>
    let { scrollyIndex, individualPoints } = $props();
</script>

{#if scrollyIndex === 1}
    <g class="individual-points">
        {#each individualPoints as point}
            <circle
                cx={point.x}
                cy={point.y}
                r="6"
                fill={point.raceColor}
                opacity="0.8"
                stroke="white"
                stroke-width="1.5"
            />
        {/each}
    </g>
{/if}