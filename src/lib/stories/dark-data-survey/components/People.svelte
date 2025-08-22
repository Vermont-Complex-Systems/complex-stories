<script>
    import { fade } from 'svelte/transition';
    import { 
        Heart, Users, Stethoscope, GraduationCap, Building, 
        FlaskConical, Briefcase, Shield, Smartphone, Store,
        Building2, UserX
    } from '@lucide/svelte';
    
    let { people, selectedDemographic, centerX, centerY, trustworthinessColorScale } = $props();
    
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
    
    // Define trust distance levels for each demographic group
    const trustDistancesByDemographic = {
        all: {
            'friend': 0.15, 'relative': 0.18, 'medical': 0.22,
            'acquaintance': 0.35, 'neighbor': 0.38, 'researcher': 0.42,
            'non_profit': 0.45, 'school': 0.55, 'employer': 0.58,
            'worker': 0.62, 'financial': 0.70, 'government': 0.75,
            'company_customer': 0.78, 'police': 0.85, 
            'social_media_platform': 0.90, 'company_not_customer': 0.95,
            'stranger': 1.0
        },
        white_men: {
            'friend': 0.20, 'relative': 0.25, 'medical': 0.30,
            'acquaintance': 0.40, 'neighbor': 0.42, 'researcher': 0.45,
            'non_profit': 0.50, 'school': 0.48, 'employer': 0.46,
            'worker': 0.52, 'financial': 0.55, 'government': 0.60,
            'company_customer': 0.58, 'police': 0.65, 
            'social_media_platform': 0.75, 'company_not_customer': 0.80,
            'stranger': 0.85
        },
        black_women: {
            'friend': 0.12, 'relative': 0.10, 'medical': 0.45,
            'acquaintance': 0.25, 'neighbor': 0.22, 'researcher': 0.50,
            'non_profit': 0.30, 'school': 0.55, 'employer': 0.65,
            'worker': 0.40, 'financial': 0.80, 'government': 0.90,
            'company_customer': 0.85, 'police': 0.95, 
            'social_media_platform': 0.88, 'company_not_customer': 0.98,
            'stranger': 1.0
        }
    };
    
    // Get trust distances for current demographic
    const getTrustDistances = (demographic) => {
        return trustDistancesByDemographic[demographic] || trustDistancesByDemographic.all;
    };
    
    // Calculate max radius for positioning - make it larger  
    const maxRadius = Math.min(centerX, centerY) - 50; // Less margin for larger rings
    
    // Filter and position people around trust rings
    const positionedPeople = $derived(() => {
        if (!people || people.length === 0) {
            return [];
        }
        
        const filtered = people.filter(person => {
            return person.demographic === selectedDemographic;
        });
        
        const trustDistances = getTrustDistances(selectedDemographic);
        
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