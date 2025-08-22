<script>
import { base } from "$app/paths";
import { scaleSequential } from 'd3-scale';
import { interpolateRdYlGn } from 'd3-scale-chromatic';
import TrustCircles from './TrustCircles.svelte';
import People from './People.svelte';
import CenterEgo from './CenterEgo.svelte';
import Legend from './Legend.svelte';
import TrustDistributionChart from './TrustDistributionChart.svelte';

// Generate data with multiple people per institution showing variation
const generatePeopleByInstitution = () => {
    const institutions = [
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
    ];

    const people = [];
    let personId = 0;

    institutions.forEach(inst => {
        // Generate 8-12 people per institution to show variation
        const numPeople = Math.floor(Math.random() * 5) + 8; // 8-12 people
        
        for (let i = 0; i < numPeople; i++) {
            // Generate trustworthiness with normal distribution around average
            const randomVariation = (Math.random() - 0.5) * 2 * inst.variation;
            const trustworthiness = Math.max(1, Math.min(7, Math.round(inst.avgTrust + randomVariation)));
            
            people.push({
                id: personId++,
                institution: inst.name,
                label: inst.label,
                trustworthiness: trustworthiness,
                gender: ['men', 'women', 'nonbinary'][Math.floor(Math.random() * 3)],
                ethnicity: ['white', 'black', 'asian'][Math.floor(Math.random() * 3)]
            });
        }
    });

    return people;
};

let people = $state(generatePeopleByInstitution());
let selectedGender = $state('all');
let selectedEthnicity = $state('all');


// Layout calculations using D3 - take more screen space
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

    <p>Pitch 1: Are you willing to share your data. Desire for privacy. Is it always through, or maybe it varies across contexts. Mixtures of privacy settings. </p>
    
    <p>Pitch 2: Do younger people care about privacy? </p>

    <p>Plot 1: privacy settings. Share what with whom.</p>

    <p>Plot 1: distance with the people you want to share your data</p>

    <div class="visualization-container">
        <h3>Institutional Trust Landscape</h3>
        <p class="viz-description">How much do you trust different institutions with your personal data? Each institution is positioned around you, with colors showing trustworthiness levels from red (low) to green (high).</p>
        
        <div class="filters">
            <div class="filter-group">
                <label for="gender-filter">Filter by Gender:</label>
                <select id="gender-filter" bind:value={selectedGender}>
                    <option value="all">All</option>
                    <option value="men">Men</option>
                    <option value="women">Women</option>
                    <option value="nonbinary">Non-binary</option>
                </select>
            </div>
            
            <div class="filter-group">
                <label for="ethnicity-filter">Filter by Ethnicity:</label>
                <select id="ethnicity-filter" bind:value={selectedEthnicity}>
                    <option value="all">All</option>
                    <option value="white">White</option>
                    <option value="black">Black</option>
                    <option value="asian">Asian</option>
                </select>
            </div>
        </div>
        
        <svg {width} {height} class="trust-visualization">
            <TrustCircles {width} {height} {centerX} {centerY} />
            <People {people} {selectedGender} {selectedEthnicity} {centerX} {centerY} {trustworthinessColorScale} />
            <CenterEgo {centerX} {centerY} />
            <Legend x={50} y={50} {trustworthinessColorScale} />
            <TrustDistributionChart {people} {selectedGender} {selectedEthnicity} {trustworthinessColorScale} />
        </svg>
    </div>

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

    .visualization-container {
        max-width: 1200px;
        margin: 3rem auto;
        text-align: center;
        padding: 2rem;
    }

    .visualization-container h3 {
        font-family: var(--serif);
        font-size: var(--font-size-large);
        color: var(--color-primary-dark);
        margin-bottom: 0.5rem;
    }

    .viz-description {
        font-size: var(--font-size-medium);
        color: var(--color-secondary-gray);
        margin-bottom: 2rem;
        font-family: var(--sans);
    }

    .trust-visualization {
        display: block;
        margin: 0 auto;
    }

    .filters {
        display: flex;
        gap: 2rem;
        justify-content: center;
        margin-bottom: 2rem;
        padding: 1rem;
        background: white;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }

    .filter-group {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 0.5rem;
    }

    .filter-group label {
        font-family: var(--sans);
        font-size: var(--font-size-small);
        font-weight: 600;
        color: var(--color-primary-dark);
    }

    .filter-group select {
        padding: 0.5rem 1rem;
        border: 2px solid #e5e7eb;
        border-radius: 6px;
        font-family: var(--sans);
        font-size: var(--font-size-small);
        background: white;
        cursor: pointer;
        transition: border-color 0.2s ease;
    }

    .filter-group select:hover {
        border-color: #3b82f6;
    }

    .filter-group select:focus {
        outline: none;
        border-color: #2563eb;
        box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
    }
</style>