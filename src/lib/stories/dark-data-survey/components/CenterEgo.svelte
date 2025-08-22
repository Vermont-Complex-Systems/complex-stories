<script>
    let { centerX, centerY } = $props();
</script>

<g class="center-ego">
    <circle
        cx={centerX}
        cy={centerY}
        r="8"
        fill="#2563eb"
        stroke="#1d4ed8"
        stroke-width="2"
    />
    <text
        x={centerX}
        y={centerY - 15}
        text-anchor="middle"
        font-size="14px"
        font-weight="bold"
        fill="#1d4ed8"
        font-family="var(--sans)"
    >
        You
    </text>
</g>