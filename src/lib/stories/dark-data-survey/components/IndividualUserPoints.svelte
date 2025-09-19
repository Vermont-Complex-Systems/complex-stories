<script>
    import { UserX } from '@lucide/svelte';
    import { trustDistancesByDemographic } from '../data/trustDistances.js';
    import { institutionIcons } from '../data/institutionIcons.js';
    import { userTrustPattern as baseUserTrustPattern } from '../data/userTrustPattern.js';
    
    let { centerX, centerY, trustworthinessColorScale, maxRadius } = $props();
    
    // Use the "all" demographic trust distances
    const trustDistances = trustDistancesByDemographic.all;
    
    // Combine user trust pattern with distance data
    const userTrustPattern = baseUserTrustPattern.map(item => ({
        ...item,
        distance: trustDistances[item.institution]
    }));
    
    // Calculate positioning for each institution
    const positionedInstitutions = $derived(() => {
        return userTrustPattern.map((item, i) => {
            const radius = item.distance * maxRadius;
            
            // Distribute institutions evenly around the circle with slight randomization
            const baseAngle = (i / userTrustPattern.length) * 2 * Math.PI - Math.PI / 2;
            const angleVariation = (Math.random() - 0.5) * 0.3;
            const angle = baseAngle + angleVariation;
            
            // Add slight radius variation for natural look
            const radiusVariation = (Math.random() - 0.5) * 0.2 * radius;
            const finalRadius = radius + radiusVariation;
            
            // Calculate final position
            const x = centerX + finalRadius * Math.cos(angle);
            const y = centerY + finalRadius * Math.sin(angle);
            
            return {
                ...item,
                x,
                y,
                color: trustworthinessColorScale(item.trustLevel),
                icon: institutionIcons[item.institution] || UserX
            };
        });
    });
    
    let tooltip = $state({ visible: false, x: 0, y: 0, institution: null });
    
    function showTooltip(event, institution) {
        tooltip = {
            visible: true,
            x: institution.x,
            y: institution.y,
            institution
        };
    }
    
    function hideTooltip() {
        tooltip = { visible: false, x: 0, y: 0, institution: null };
    }
</script>

<g class="individual-user-points">
    {#each positionedInstitutions() as institution}
        {@const IconComponent = institution.icon}
        <foreignObject
            x={institution.x - 10}
            y={institution.y - 10}
            width="20"
            height="20"
            style="cursor: pointer; pointer-events: all;"
            role="button"
            tabindex="0"
            onmouseenter={(e) => showTooltip(e, institution)}
            onmouseleave={hideTooltip}
        >
            <div style="width: 20px; height: 20px; display: flex; align-items: center; justify-content: center;">
                <IconComponent size="16" fill={institution.color} stroke="none" />
            </div>
        </foreignObject>
    {/each}
    
    {#if tooltip.visible && tooltip.institution}
        <g class="tooltip">
            <rect
                x={tooltip.x + 15}
                y={tooltip.y - 30}
                width="140"
                height="45"
                fill="rgba(0,0,0,0.8)"
                rx="4"
            />
            <text
                x={tooltip.x + 20}
                y={tooltip.y - 12}
                fill="white"
                font-size="12px"
                font-family="var(--sans)"
                font-weight="500"
            >
                {tooltip.institution.label}
            </text>
            <text
                x={tooltip.x + 20}
                y={tooltip.y + 2}
                fill="white"
                font-size="11px"
                font-family="var(--sans)"
            >
                Trust: {tooltip.institution.trustLevel}/7
            </text>
            <text
                x={tooltip.x + 20}
                y={tooltip.y + 14}
                fill="white"
                font-size="9px"
                font-family="var(--sans)"
                opacity="0.8"
            >
                Distance: {Math.round(tooltip.institution.distance * 100)}%
            </text>
        </g>
    {/if}
</g>