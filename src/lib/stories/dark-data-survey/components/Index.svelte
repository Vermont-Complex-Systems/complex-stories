<script>
import { base } from "$app/paths";
import { scaleSequential } from 'd3-scale';
import { interpolateRdYlGn } from 'd3-scale-chromatic';
import { innerWidth } from 'svelte/reactivity/window';
import Scrolly from '$lib/components/helpers/Scrolly.svelte';
import TrustCircles from './TrustCircles.svelte';
import People from './People.svelte';
import CenterEgo from './CenterEgo.svelte';
import Legend from './Legend.svelte';
import TrustDistributionChart from './TrustDistributionChart.svelte';
import IndividualUserPoints from './IndividualUserPoints.svelte';

// Generate data with demographic-specific trust patterns
const generatePeopleByInstitution = () => {
    // Different trust patterns for each demographic group
    const institutionsByDemographic = {
        all: [
            { name: 'friend', label: 'Friends', avgTrust: 6, variation: 1 },
            { name: 'relative', label: 'Family', avgTrust: 6.5, variation: 1 },
            { name: 'medical', label: 'Healthcare', avgTrust: 4.5, variation: 2 },
            { name: 'school', label: 'Education', avgTrust: 4, variation: 1.5 },
            { name: 'employer', label: 'Employer', avgTrust: 4, variation: 1.5 },
            { name: 'researcher', label: 'Researcher', avgTrust: 4.5, variation: 1.5 },
            { name: 'worker', label: 'Worker', avgTrust: 3.5, variation: 1 },
            { name: 'financial', label: 'Financial', avgTrust: 3, variation: 1.5 },
            { name: 'government', label: 'Government', avgTrust: 2.5, variation: 2 },
            { name: 'police', label: 'Police', avgTrust: 2.5, variation: 2.5 },
            { name: 'social_media_platform', label: 'Social Media', avgTrust: 2, variation: 1.5 },
            { name: 'company_customer', label: 'Companies (Customer)', avgTrust: 3, variation: 1.5 },
            { name: 'company_not_customer', label: 'Companies (Non-customer)', avgTrust: 1.5, variation: 1 },
            { name: 'acquaintance', label: 'Acquaintance', avgTrust: 4, variation: 1 },
            { name: 'neighbor', label: 'Neighbor', avgTrust: 4, variation: 1.5 },
            { name: 'non_profit', label: 'Non-profit', avgTrust: 4.5, variation: 1.5 },
            { name: 'stranger', label: 'Strangers', avgTrust: 1.5, variation: 1 }
        ],
        white_men: [
            { name: 'friend', label: 'Friends', avgTrust: 5.8, variation: 1 },
            { name: 'relative', label: 'Family', avgTrust: 6.2, variation: 1 },
            { name: 'medical', label: 'Healthcare', avgTrust: 5.2, variation: 1.5 },
            { name: 'school', label: 'Education', avgTrust: 4.8, variation: 1.2 },
            { name: 'employer', label: 'Employer', avgTrust: 4.5, variation: 1.2 },
            { name: 'researcher', label: 'Researcher', avgTrust: 5.0, variation: 1.3 },
            { name: 'worker', label: 'Worker', avgTrust: 4.0, variation: 1 },
            { name: 'financial', label: 'Financial', avgTrust: 4.2, variation: 1.3 },
            { name: 'government', label: 'Government', avgTrust: 3.8, variation: 1.8 },
            { name: 'police', label: 'Police', avgTrust: 4.2, variation: 2 },
            { name: 'social_media_platform', label: 'Social Media', avgTrust: 2.5, variation: 1.5 },
            { name: 'company_customer', label: 'Companies (Customer)', avgTrust: 3.8, variation: 1.3 },
            { name: 'company_not_customer', label: 'Companies (Non-customer)', avgTrust: 2.2, variation: 1 },
            { name: 'acquaintance', label: 'Acquaintance', avgTrust: 4.3, variation: 1 },
            { name: 'neighbor', label: 'Neighbor', avgTrust: 4.5, variation: 1.3 },
            { name: 'non_profit', label: 'Non-profit', avgTrust: 4.0, variation: 1.5 },
            { name: 'stranger', label: 'Strangers', avgTrust: 2.0, variation: 1 }
        ],
        black_women: [
            { name: 'friend', label: 'Friends', avgTrust: 6.5, variation: 0.8 },
            { name: 'relative', label: 'Family', avgTrust: 6.8, variation: 0.7 },
            { name: 'medical', label: 'Healthcare', avgTrust: 3.2, variation: 2.5 },
            { name: 'school', label: 'Education', avgTrust: 3.8, variation: 2 },
            { name: 'employer', label: 'Employer', avgTrust: 3.2, variation: 1.8 },
            { name: 'researcher', label: 'Researcher', avgTrust: 4.0, variation: 1.8 },
            { name: 'worker', label: 'Worker', avgTrust: 4.2, variation: 1.2 },
            { name: 'financial', label: 'Financial', avgTrust: 2.0, variation: 1.8 },
            { name: 'government', label: 'Government', avgTrust: 1.8, variation: 1.5 },
            { name: 'police', label: 'Police', avgTrust: 1.2, variation: 1.2 },
            { name: 'social_media_platform', label: 'Social Media', avgTrust: 1.8, variation: 1.3 },
            { name: 'company_customer', label: 'Companies (Customer)', avgTrust: 2.2, variation: 1.5 },
            { name: 'company_not_customer', label: 'Companies (Non-customer)', avgTrust: 1.0, variation: 0.8 },
            { name: 'acquaintance', label: 'Acquaintance', avgTrust: 4.8, variation: 1.2 },
            { name: 'neighbor', label: 'Neighbor', avgTrust: 5.2, variation: 1.5 },
            { name: 'non_profit', label: 'Non-profit', avgTrust: 5.5, variation: 1.2 },
            { name: 'stranger', label: 'Strangers', avgTrust: 1.0, variation: 0.8 }
        ]
        // Add more demographic groups as needed
    };

    const people = [];
    let personId = 0;

    // Generate data for each demographic group
    Object.keys(institutionsByDemographic).forEach(demographic => {
        const institutions = institutionsByDemographic[demographic];
        
        institutions.forEach(inst => {
            // Generate 8-12 people per institution to show variation
            const numPeople = Math.floor(Math.random() * 5) + 8; // 8-12 people
            
            for (let i = 0; i < numPeople; i++) {
                // Generate trustworthiness with normal distribution around average
                const randomVariation = (Math.random() - 0.5) * 2 * inst.variation;
                const trustworthiness = Math.max(1, Math.min(7, Math.round(inst.avgTrust + randomVariation)));
                
                // Extract gender and ethnicity from demographic key
                let gender, ethnicity;
                if (demographic === 'all') {
                    gender = ['men', 'women', 'nonbinary'][Math.floor(Math.random() * 3)];
                    ethnicity = ['white', 'black', 'asian'][Math.floor(Math.random() * 3)];
                } else {
                    const [eth, gen] = demographic.split('_');
                    ethnicity = eth;
                    gender = gen;
                }
                
                people.push({
                    id: personId++,
                    institution: inst.name,
                    label: inst.label,
                    trustworthiness: trustworthiness,
                    gender: gender,
                    ethnicity: ethnicity,
                    demographic: demographic
                });
            }
        });
    });

    return people;
};

let people = $state(generatePeopleByInstitution());
let selectedDemographic = $state('white_men');

// Scrolly state management
let scrollyIndex = $state();
let isMobile = $derived(innerWidth.current <= 768);
let isTablet = $derived(innerWidth.current <= 1200 && innerWidth.current > 768);

// Define scrolly steps
const steps = [
    "Question: How comfortable do you feel sharing PII with the following institution?",
    "Your personal relationship with institutions varies greatly. Each institution sits at a different distance from you, representing how much you trust them with your personal data.",
    "But you're not alone in this landscape. Hundreds of others navigate the same institutional relationships, each with their own trust levels and patterns.",
    "Different demographic groups show strikingly different patterns of institutional trust, reflecting lived experiences and historical relationships with institutions."
];

// Track which visualization to show based on step
let currentView = $derived(() => {
    if (scrollyIndex === undefined || scrollyIndex <= 1) return 'individual';
    if (scrollyIndex === 2) return 'white_men';
    return 'demographic';
});

// Track selected demographic for comparison steps
let currentDemographic = $derived(() => {
    if (scrollyIndex === undefined || scrollyIndex < 3) return 'white_men';
    return 'white_men'; // Start with all, user can change with widget
});

// Track if visualization is in viewport
let visualizationInView = $state(false);
let visualizationContainer;

// Set up intersection observer to track when visualization is in view
$effect(() => {
    if (!visualizationContainer) return;
    
    const observer = new IntersectionObserver(
        (entries) => {
            visualizationInView = entries[0].isIntersecting;
        },
        { threshold: 0.3 } // Show chart when 30% of visualization is visible
    );
    
    observer.observe(visualizationContainer);
    
    return () => observer.disconnect();
});

// Layout calculations using D3 - keep original size
const width = 1000;
const height = 800;
const centerX = width / 2;
const centerY = height / 2;

// Color scale for trustworthiness (1-7 scale)
// Red (low trust) to Yellow to Green (high trust)
const trustworthinessColorScale = scaleSequential(interpolateRdYlGn)
    .domain([1, 7]);

</script>

<section id="story"  class="story">
    <div class="logo-container">
            <a href="{base}/" class="logo-link">
                <img src="{base}/octopus-swim-right.png" alt="Home" class="logo" width="200" />
            </a>
    </div>

    <h1>Do younger folks care about privacy?</h1>
    <div class="article-meta">
        <p class="author">By <a href="{base}/author/juniper-lisa-lovato">Juniper Lovato</a></p>
        <p class="date">Aug 13, 2025</p>
    </div>



    <p>Spoiler: Privacy depends on who you are and and context.</p>

    <p>Privacy depends on who you are and context. Your willingness to share data varies dramatically across different institutions and relationships.</p>

    <!-- Scrollytelling Section -->
    <div class="chart-container-scrolly">
        <!-- Sticky visualization -->
        <div class="visualization-container" bind:this={visualizationContainer}>
            <svg {width} {height} class="trust-visualization">
                <TrustCircles 
                    {width} 
                    {height} 
                    {centerX} 
                    {centerY} 
                    selectedDemographic={currentView() === 'individual' ? 'white_men' : (currentView() === 'white_men' ? 'white_men' : selectedDemographic)} 
                />
                
                {#if currentView() === 'individual'}
                    <IndividualUserPoints {centerX} {centerY} {trustworthinessColorScale} />
                {:else if currentView() === 'white_men'}
                    <People {people} selectedDemographic="white_men" {centerX} {centerY} {trustworthinessColorScale} />
                {:else if currentView() === 'demographic'}
                    <People {people} selectedDemographic={selectedDemographic} {centerX} {centerY} {trustworthinessColorScale} />
                {/if}
                
                <CenterEgo {centerX} {centerY} />
                <Legend x={50} y={50} {trustworthinessColorScale} />
                
            </svg>
            
            <!-- Chart overlay for demographic comparisons -->
            {#if currentView() === 'white_men' || currentView() === 'demographic'}
                <div class="chart-overlay">
                    <TrustDistributionChart {people} selectedDemographic={currentView() === 'white_men' ? 'white_men' : selectedDemographic} {trustworthinessColorScale} />
                </div>
            {/if}
                
            <!-- Demographic selector widget - only in demographic view -->
            {#if currentView() === 'demographic'}
                <div class="demographic-selector">
                    <label for="demographic-select">Compare demographics:</label>
                    <select id="demographic-select" bind:value={selectedDemographic}>
                        <option value="all">All Demographics</option>
                        <option value="white_men">White Men</option>
                        <option value="black_women">Black Women</option>
                    </select>
                </div>
            {/if}
        </div>
    </div>

    <!-- Scrolly steps -->
    <div class="stepContainer">
        <Scrolly bind:value={scrollyIndex} top={isMobile ? 50 : 0} bottom={isMobile ? 50 : 0}>
            {#each steps as text, i}
                {@const active = scrollyIndex === i || (scrollyIndex === undefined && i === 0)}
                <div class="scrolly-step" class:active class:mobile={isMobile} class:tablet={isTablet}>
                    <p>{text}</p>
                </div>
            {/each}
        </Scrolly>
    </div>
    
    
</section>

<section>

    <p>Data</p>

    <ul>
        <li>undergrad</li>
    </ul>
    
</section>


<style>
    .article-meta {
        margin: -1rem auto 2rem auto; /* Negative margin to pull closer to title */
        font-family: var(--sans);
        max-width: 700px;
        text-align: center;
    }

    .article-meta .author {
        font-size: var(--font-size-medium);
        color: var(--color-secondary-gray);
        margin: 0 0 0.25rem 0;
        font-weight: 500;
    }

    .article-meta .date {
        font-size: var(--font-size-small);
        color: var(--color-tertiary-gray);
        margin: 0;
        font-weight: 400;
    }

    :global(#story) {
        max-width: 1200px;
        margin: 2rem auto;
        padding: 0 2rem;
    }

    :global(#story) h1 {
        font-size: var(--font-size-xlarge);
        margin: 2rem auto 3rem auto;
        text-align: center;
        font-family: var(--serif);
        max-width: 700px;
    }

	section p {
      font-size: 22px;
      max-width: 800px;
      line-height: 1.3;
      margin: 1rem auto;
  }

    section img {
        display: block;
        margin: 2rem auto;
        max-width: 100%;
        height: auto;
    }

    /* Scrollytelling Layout - similar to allotax-scrolly */
    .chart-container-scrolly {
        margin-top: 3rem;
        width: 100%;
        position: sticky;
        top: calc(50vh - 400px);
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 1;
    }

    .visualization-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        width: 100%;
        position: relative;
    }

    .trust-visualization {
        display: block;
        margin: 0 auto;
    }

    .stepContainer {
        /* Steps take up the full width and scroll over the visualization */
        position: relative;
        z-index: 2;
        width: 100%;
        display: flex;
        flex-direction: column;
        align-items: center;
    }

    .chart-overlay {
        position: fixed !important;
        bottom: 20px !important;
        right: 20px !important;
        z-index: 1000 !important;
        pointer-events: auto !important;
        /* Override any global constraints */
        max-width: none !important;
        margin: 0 !important;
        padding: 0 !important;
        /* Smooth fade in/out */
        animation: fadeIn 0.3s ease-in-out;
    }

    .demographic-selector {
        position: absolute;
        bottom: 20px;
        left: 20px;
        z-index: 100;
        pointer-events: auto;
        animation: fadeIn 0.3s ease-in-out;
        background: rgba(255, 255, 255, 0.95);
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(0, 0, 0, 0.1);
    }

    .demographic-selector label {
        display: block;
        font-size: 0.9rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
        color: #374151;
        font-family: var(--sans);
    }

    .demographic-selector select {
        width: 100%;
        padding: 0.5rem;
        border: 1px solid #d1d5db;
        border-radius: 4px;
        background: white;
        font-size: 0.9rem;
        font-family: var(--sans);
        color: #374151;
        cursor: pointer;
    }

    .demographic-selector select:focus {
        outline: none;
        border-color: #3b82f6;
        box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.1);
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }

    .scrolly-step {
        min-height: 80vh;
        padding: 4rem 2rem;
        display: flex;
        align-items: center;
        justify-content: center;
        width: 100%;
        max-width: 800px;
        margin: 0 auto;
    }

    .scrolly-step p {
        font-size: 1.4rem;
        line-height: 1.6;
        max-width: 600px;
        margin: 0 auto;
        text-align: center;
        background: rgba(255, 255, 255, 0.95);
        padding: 2rem;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(0, 0, 0, 0.05);
    }

    .scrolly-step.active p {
        opacity: 1;
        transform: translateY(0);
    }

    .scrolly-step:not(.active) p {
        opacity: 0.6;
        transform: translateY(10px);
        transition: all 0.4s ease;
    }

    /* Mobile responsiveness */
    @media (max-width: 1200px) {
        .chart-container-scrolly {
            position: sticky;
            top: calc(50vh - 300px);
            width: 100%;
            margin: 2rem auto;
            display: flex;
            justify-content: center;
            align-items: center;
        }

        .scrolly-step {
            min-height: 60vh;
            padding: 2rem 1rem;
        }

        .scrolly-step p {
            font-size: 1.2rem;
            max-width: 90%;
            padding: 1.5rem;
        }

        .demographic-selector {
            position: static;
            margin-top: 1rem;
            width: 100%;
            box-sizing: border-box;
        }

        .chart-overlay {
            position: static;
            margin-top: 1rem;
        }
    }

    @media (max-width: 768px) {
        .chart-container-scrolly {
            position: sticky;
            top: calc(50vh - 200px);
            width: 100%;
            margin: 1rem auto;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        
        .scrolly-step p {
            font-size: 1.1rem;
            padding: 1rem;
        }
    }
</style>