<script>
    import { fade } from 'svelte/transition';
    import { 
        Heart, Users, Stethoscope, GraduationCap, Building, 
        FlaskConical, Briefcase, Shield, Smartphone, Store,
        Building2, UserX
    } from '@lucide/svelte';
    
    let { people, selectedGender, selectedEthnicity, centerX, centerY, trustworthinessColorScale } = $props();
    
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
    
    // Institution colors (keeping for background or accent)
    const institutionColors = {
        'friend': '#10b981', 'relative': '#059669', 'medical': '#3b82f6',
        'acquaintance': '#8b5cf6', 'neighbor': '#a855f7', 'school': '#06b6d4',
        'employer': '#0891b2', 'researcher': '#0284c7', 'non_profit': '#84cc16',
        'worker': '#65a30d', 'financial': '#eab308', 'government': '#f59e0b',
        'police': '#ef4444', 'social_media_platform': '#f97316',
        'company_customer': '#ec4899', 'company_not_customer': '#be185d',
        'stranger': '#6b7280'
    };
    
    // Define trust distance levels for each institution (0 = center, 1 = furthest)
    const trustDistances = {
        'friend': 0.2,
        'medical': 0.3,
        'relative': 0.35,
        'researcher': 0.4,
        'employer': 0.45,
        'school': 0.5,
        'non_profit': 0.55,
        'acquaintance': 0.6,
        'neighbor': 0.6,
        'worker': 0.65,
        'financial': 0.7,
        'government': 0.75,
        'company_customer': 0.8,
        'police': 0.85,
        'social_media_platform': 0.9,
        'company_not_customer': 0.95,
        'stranger': 1.0
    };
    
    // Calculate max radius for positioning - make it larger
    const maxRadius = Math.min(centerX, centerY) - 50; // Less margin for larger rings
    
    // Filter and position people around trust rings
    const positionedPeople = $derived(() => {
        if (!people || people.length === 0) {
            return [];
        }
        
        const filtered = people.filter(person => {
            const genderMatch = selectedGender === 'all' || person.gender === selectedGender;
            const ethnicityMatch = selectedEthnicity === 'all' || person.ethnicity === selectedEthnicity;
            return genderMatch && ethnicityMatch;
        });
        
        return filtered.map((person, i) => {
            // Get the trust distance for this person's institution
            const trustDistance = trustDistances[person.institution] || 0.8;
            const baseRadius = trustDistance * maxRadius;
            
            // Add some random variation to radius (±15% variation)
            const radiusVariation = (Math.random() - 0.5) * 0.3 * baseRadius;
            const radius = baseRadius + radiusVariation;
            
            // Group people by institution for positioning
            const peopleAtSameInstitution = filtered.filter(p => 
                p.institution === person.institution
            );
            const indexInInstitution = peopleAtSameInstitution.indexOf(person);
            
            // Calculate angle for this person within their institution group
            const angleStep = (2 * Math.PI) / Math.max(peopleAtSameInstitution.length, 1);
            const baseAngle = indexInInstitution * angleStep;
            
            // Add some random variation to angle (±10 degrees)
            const angleVariation = (Math.random() - 0.5) * 0.35; // ~±10 degrees in radians
            const angle = baseAngle + angleVariation;
            
            const x = centerX + radius * Math.cos(angle);
            const y = centerY + radius * Math.sin(angle);
            
            return {
                ...person,
                x,
                y,
                color: trustworthinessColorScale(person.trustworthiness),
                icon: institutionIcons[person.institution] || UserX
            };
        });
    });
    
    let tooltip = $state({ visible: false, x: 0, y: 0, person: null });
    
    function showTooltip(event, person) {
        tooltip = {
            visible: true,
            x: person.x,
            y: person.y,
            person
        };
    }
    
    function hideTooltip() {
        tooltip = { visible: false, x: 0, y: 0, person: null };
    }
</script>

<g class="people">
    {#each positionedPeople() as person (person.id)}
        <!-- Colored icon without background circle -->
        {@const IconComponent = person.icon}
        <foreignObject
            x={person.x - 8}
            y={person.y - 8}
            width="16"
            height="16"
            style="cursor: pointer; pointer-events: all;"
            role="button"
            tabindex="0"
            onmouseenter={(e) => showTooltip(e, person)}
            onmouseleave={hideTooltip}
            in:fade={{ duration: 300 }}
            out:fade={{ duration: 300 }}
        >
            <div style="width: 16px; height: 16px; display: flex; align-items: center; justify-content: center;">
                <IconComponent size="12" fill={person.color} stroke="none" />
            </div>
        </foreignObject>
    {/each}
    
    <!-- Institution labels for each ring - positioned clockwise -->
    {#each Object.keys(trustDistances) as institutionName, i}
        {@const distance = trustDistances[institutionName]}
        {@const radius = distance * maxRadius}
        {@const uniqueDistances = [...new Set(Object.values(trustDistances))].sort((a, b) => a - b)}
        {@const ringIndex = uniqueDistances.indexOf(distance)}
        {@const angle = (ringIndex / uniqueDistances.length) * 2 * Math.PI - Math.PI / 2} // Start at top, go clockwise
        {@const labelRadius = radius} // Position labels directly on the ring
        {@const labelX = centerX + labelRadius * Math.cos(angle)}
        {@const labelY = centerY + labelRadius * Math.sin(angle)}
        {@const institutionPeople = positionedPeople().filter(p => p.institution === institutionName)}
        {#if institutionPeople.length > 0}
            {@const IconComponent = institutionIcons[institutionName] || UserX}
            <!-- Background rectangle for better readability -->
            <rect
                x={labelX - 35}
                y={labelY - 8}
                width="70"
                height="16"
                fill="rgba(255, 255, 255, 0.95)"
                stroke="rgba(0, 0, 0, 0.15)"
                stroke-width="1"
                rx="3"
            />
            <!-- Text label -->
            <text
                x={labelX - 5}
                y={labelY}
                text-anchor="middle"
                dominant-baseline="central"
                font-size="9px"
                fill="#374151"
                font-family="var(--sans)"
                font-weight="600"
            >
                {institutionPeople[0].label}
            </text>
            <!-- Icon after text -->
            <foreignObject
                x={labelX + 15}
                y={labelY - 6}
                width="12"
                height="12"
            >
                <div style="width: 12px; height: 12px; display: flex; align-items: center; justify-content: center;">
                    <IconComponent size="10" fill="#374151" stroke="none" />
                </div>
            </foreignObject>
        {/if}
    {/each}
    
    {#if tooltip.visible && tooltip.person}
        <g class="tooltip" transition:fade={{ duration: 200 }}>
            <rect
                x={tooltip.x + 10}
                y={tooltip.y - 25}
                width="130"
                height="40"
                fill="rgba(0,0,0,0.8)"
                rx="4"
            />
            <text
                x={tooltip.x + 15}
                y={tooltip.y - 10}
                fill="white"
                font-size="11px"
                font-family="var(--sans)"
                font-weight="500"
            >
                {tooltip.person.label}
            </text>
            <text
                x={tooltip.x + 15}
                y={tooltip.y + 2}
                fill="white"
                font-size="10px"
                font-family="var(--sans)"
            >
                Trust: {tooltip.person.trustworthiness}/7
            </text>
            <text
                x={tooltip.x + 15}
                y={tooltip.y + 12}
                fill="white"
                font-size="8px"
                font-family="var(--sans)"
                opacity="0.8"
            >
                {tooltip.person.gender}, {tooltip.person.ethnicity}
            </text>
        </g>
    {/if}
</g>