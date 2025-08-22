<script>
    import { 
        Heart, Users, Stethoscope, GraduationCap, Building, 
        FlaskConical, Briefcase, Shield, Smartphone, Store,
        Building2, UserX
    } from '@lucide/svelte';
    
    let { centerX, centerY, trustworthinessColorScale } = $props();
    
    // Institution to icon mapping
    const institutionIcons = {
        'friend': Heart,
        'relative': Users, 
        'medical': Stethoscope,
        'school': GraduationCap,
        'employer': Building,
        'researcher': FlaskConical,
        'worker': Briefcase,
        'police': Shield,
        'social_media_platform': Smartphone,
        'company_customer': Store,
        'company_not_customer': Building2,
        'acquaintance': Users,
        'neighbor': Users,
        'government': Building,
        'non_profit': Heart,
        'financial': Building2,
        'stranger': UserX
    };
    
    // Use the same trust distances as the "all" demographic group
    const trustDistances = {
        'friend': 0.15, 'relative': 0.18, 'medical': 0.22,
        'acquaintance': 0.35, 'neighbor': 0.38, 'researcher': 0.42,
        'non_profit': 0.45, 'school': 0.55, 'employer': 0.58,
        'worker': 0.62, 'financial': 0.70, 'government': 0.75,
        'company_customer': 0.78, 'police': 0.85, 
        'social_media_platform': 0.90, 'company_not_customer': 0.95,
        'stranger': 1.0
    };
    
    // Individual user's trust pattern - one representative person from the "all" demographic
    const userTrustPattern = [
        { institution: 'friend', label: 'Friends', trustLevel: 6 },
        { institution: 'relative', label: 'Family', trustLevel: 7 },
        { institution: 'medical', label: 'Healthcare', trustLevel: 4 },
        { institution: 'acquaintance', label: 'Acquaintance', trustLevel: 4 },
        { institution: 'neighbor', label: 'Neighbor', trustLevel: 4 },
        { institution: 'researcher', label: 'Researcher', trustLevel: 5 },
        { institution: 'non_profit', label: 'Non-profit', trustLevel: 5 },
        { institution: 'school', label: 'Education', trustLevel: 4 },
        { institution: 'employer', label: 'Employer', trustLevel: 3 },
        { institution: 'worker', label: 'Worker', trustLevel: 3 },
        { institution: 'financial', label: 'Financial', trustLevel: 3 },
        { institution: 'government', label: 'Government', trustLevel: 2 },
        { institution: 'company_customer', label: 'Companies (Customer)', trustLevel: 3 },
        { institution: 'police', label: 'Police', trustLevel: 2 },
        { institution: 'social_media_platform', label: 'Social Media', trustLevel: 2 },
        { institution: 'company_not_customer', label: 'Companies (Non-customer)', trustLevel: 1 },
        { institution: 'stranger', label: 'Strangers', trustLevel: 1 }
    ].map(item => ({
        ...item,
        distance: trustDistances[item.institution]
    }));
    
    // Calculate positioning using same logic as People component
    const maxRadius = Math.min(centerX, centerY) - 50;
    
    const positionedInstitutions = $derived(() => {
        return userTrustPattern.map((item, i) => {
            const radius = item.distance * maxRadius;
            
            // Use similar positioning as People component - single person per institution
            // Add some variation to make it look natural like it would in the aggregated plot
            const baseAngle = (i / userTrustPattern.length) * 2 * Math.PI - Math.PI / 2;
            const angleVariation = (Math.random() - 0.5) * 0.3; // Small random variation
            const angle = baseAngle + angleVariation;
            
            // Add slight radius variation like in the aggregated plot
            const radiusVariation = (Math.random() - 0.5) * 0.2 * radius;
            const finalRadius = radius + radiusVariation;
            
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