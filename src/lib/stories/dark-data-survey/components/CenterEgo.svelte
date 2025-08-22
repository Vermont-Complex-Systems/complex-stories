<script>
    import { User } from '@lucide/svelte';
    
    let { centerX, centerY } = $props();
</script>

<g class="center-ego">
    <!-- Background circle for the icon -->
    <circle
        cx={centerX}
        cy={centerY}
        r="20"
        fill="#f3f4f6"
        stroke="#6b7280"
        stroke-width="2"
    />
    
    <!-- User icon -->
    <foreignObject
        x={centerX - 12}
        y={centerY - 12}
        width="24"
        height="24"
    >
        <div style="width: 24px; height: 24px; display: flex; align-items: center; justify-content: center;">
            <User size="16" fill="#374151" stroke="none" />
        </div>
    </foreignObject>
    
    <!-- Label -->
    <text
        x={centerX}
        y={centerY - 30}
        text-anchor="middle"
        font-size="14px"
        font-weight="bold"
        fill="#374151"
        font-family="var(--sans)"
    >
    </text>
</g>