<script>
import { base } from "$app/paths";
import { scaleSequential } from 'd3-scale';
import { interpolateRdYlGn } from 'd3-scale-chromatic';
import { innerWidth, outerHeight } from 'svelte/reactivity/window';

import FingerprintJS from '@fingerprintjs/fingerprintjs';

import Md from '$lib/components/helpers/MarkdownRenderer.svelte';
import Scrolly from '$lib/components/helpers/Scrolly.svelte';

import TrustEvo from './TrustEvo.svelte';
import Survey from './Survey.svelte';
import ConsentPopup from './ConsentPopup.svelte';
import Dashboard from './Dashboard.svelte';

import { renderContent, scrollyContent } from './Snippets.svelte';
import { postAnswer, upsertAnswer } from '../data/data.remote.js';

let { story, data } = $props();

// Consent state
let hasConsented = $state(false);

// Generate browser fingerprint using FingerprintJS
let userFingerprint = $state('');

$effect(() => {
    if (typeof window !== 'undefined') {
        FingerprintJS.load().then(fp => {
            return fp.get();
        }).then(result => {
            userFingerprint = result.visitorId;
            console.log('Fingerprint loaded:', userFingerprint);
        }).catch(err => {
            console.error('Failed to load fingerprint:', err);
        });
    }
});

// Helper to safely post answers - returns a promise for await usage
function saveAnswer(field, value) {
    if (!userFingerprint) {
        console.warn('Fingerprint not ready yet, skipping save');
        return Promise.resolve();
    }

    // Fields that need string-to-ordinal conversion
    const stringToOrdinalFields = ['consent', 'socialMediaPrivacy', 'institutionPreferences', 'demographicsMatter'];

    // Fields that already have numeric values
    const numericFields = ['relativePreferences', 'govPreferences', 'polPreferences', 'age', 'gender_ord', 'orientation_ord', 'race_ord'];

    // Handle special cases
    if (field === 'platformMatters') {
        // Convert array to comma-separated string for storage
        const stringValue = Array.isArray(value) ? value.join(',') : value;
        return upsertAnswer({ fingerprint: userFingerprint, field, value: stringValue });
    } else if (stringToOrdinalFields.includes(field)) {
        return postAnswer({ fingerprint: userFingerprint, field, value });
    } else if (numericFields.includes(field)) {
        // Convert string numbers to integers
        const numericValue = parseInt(value, 10);
        return upsertAnswer({ fingerprint: userFingerprint, field, value: numericValue });
    } else {
        console.error(`Unknown field: ${field}`);
        return Promise.reject(new Error(`Unknown field: ${field}`));
    }
}

// Generate people data using imported function

let selectedDemographic = $state('white_men');

// Scrolly state management - separate states for survey and story
let surveyScrollyState = $state({
    scrollyIndex: 0,
    isMobile: false,
    isTablet: false
});

let storyScrollyState = $state({ 
    scrollyIndex: undefined,
    isMobile: false,
    isTablet: false
});


// Layout calculations using D3 - responsive width and height
let width = $state(innerWidth.current);
let height = $state(outerHeight.current);

// Reference to story section for visibility detection
let storySection = $state();
let conclusionSection = $state();
let conclusionVisible = $state(false);
let dashboardSection = $state();
let dashboardVisible = $state(false);

// Detect when conclusion section is visible
$effect(() => {
    if (typeof window !== 'undefined' && conclusionSection) {
        const observer = new IntersectionObserver((entries) => {
            conclusionVisible = entries[0].isIntersecting;
        }, { threshold: 0.3 });

        observer.observe(conclusionSection);

        return () => observer.disconnect();
    }
});

// Detect when dashboard section is visible
$effect(() => {
    if (typeof window !== 'undefined' && dashboardSection) {
        const observer = new IntersectionObserver((entries) => {
            dashboardVisible = entries[0].isIntersecting;
        }, { threshold: 0.3 });

        observer.observe(dashboardSection);

        return () => observer.disconnect();
    }
});

</script>

<!-- Consent Popup -->
<ConsentPopup onAccept={() => hasConsented = true} {userFingerprint} {saveAnswer} />

<article id="dark-data-survey">

    <Survey bind:scrollyState={surveyScrollyState} {userFingerprint} {saveAnswer} />

    <div class="title">
        <h1>{data.title}</h1>
        <h2>{data.subtitle}</h2>

        <div class="article-meta">
            <p class="author">
                By <a target=_blank rel=noreferrer href=https://vermont-complex-systems.github.io/complex-stories/author/jonathan-st-onge>Jonathan St-Onge</a> and <a target=_blank rel=noreferrer href=https://vermont-complex-systems.github.io/complex-stories/author/juniper-lisa-lovato>Juniper Lovato</a>
            </p>
            <p class="date">
                {data.date}
            </p>
        </div>
    </div>

    <section id="intro">
        {@render renderContent(data.intro)}
    </section>

    <section id="story">
        <div class="scrolly-container" bind:this={storySection}>
            <div class="scrolly-chart">
                <TrustEvo
                    scrollyIndex={storyScrollyState.scrollyIndex}
                    {width} {height}
                    isStorySection={storyScrollyState.scrollyIndex !== undefined}
                    {storySection}
                    {conclusionVisible} />
            </div>

            {@render scrollyContent(data.steps, storyScrollyState)}
        </div>
    </section>
    
    <h2>Conclusion</h2>
    <section id="conclusion" bind:this={conclusionSection}>
        {@render renderContent(data.conclusion)}
    </section>

    <section id="dashboard" bind:this={dashboardSection}>
        <Dashboard {width} {height} />
    </section>
</article>

<div class="corner-image" class:hidden={conclusionVisible || dashboardVisible}>
    <a href="{base}/">
        <img src="{base}/common/thumbnails/screenshots/underwaterBits2-angler-fish.png" alt="Dark data visualization" />
    </a>
</div>

<style>
/* -----------------------------
   Global Dark Mode Context
----------------------------- */
:global(body:has(#dark-data-survey)) {
    overflow-x: hidden;
    background-color: #2b2b2b;
    color: #ffffff;
    font-family: var(--sans);
}

/* Headings */
:global(body:has(#dark-data-survey)) h1,
:global(body:has(#dark-data-survey)) h2 {
    font-family: var(--serif);
    max-width: 450px;
    margin: 6rem auto 1rem auto;
    text-align: center;
}

:global(body:has(#dark-data-survey)) h1 {
    font-size: var(--font-size-giant);
}

:global(body:has(#dark-data-survey)) h2 {
    font-size: var(--font-size-medium);
    font-weight: 400;
    margin: 0 auto 3rem auto;
}

/* -----------------------------
   Text & Paragraphs
----------------------------- */
:global(#dark-data-survey p) {
    color: whitesmoke;
}

/* Make sure intro & conclusion text remain white */
:global(#intro p),
:global(#conclusion p) {
    color: whitesmoke;
}

/* Scrolly text specifically black for readability */
:global(.scrolly-container .markdown-content),
:global(.scrolly-container .markdown-content p) {
    color: black !important;
}

/* -----------------------------
   Title & Meta Section
----------------------------- */
.title {
    margin: 0 auto 5rem auto;
    text-align: center;
}

.article-meta {
    margin: -1rem auto 2rem auto;
    max-width: 30rem;
    font-family: var(--sans);
    text-align: center;
}

.article-meta .author {
    font-size: var(--font-size-medium);
    margin: -1rem auto 2rem auto;
    max-width: 30rem;
    font-family: var(--sans);
    text-align: center;
}

.article-meta .author a {
    font-size: var(--font-size-medium);
    color: var(--color-gray-300);
    margin: 0 0 0.25rem 0;
    font-weight: 500;
}

.article-meta .date {
    font-size: var(--font-size-small);
    color: var(--color-tertiary-gray);
    margin: 0;
    font-weight: 400;
}

/* -----------------------------
   Scrolly Section
----------------------------- */
.scrolly-container {
    position: relative;
    min-height: 100vh;
}

.scrolly-chart {
    position: sticky;
    top: calc(50vh - 500px);
    height: fit-content;
    z-index: 1;
    pointer-events: none;
}

/* -----------------------------
   Corner Image
----------------------------- */
.corner-image {
    position: fixed;
    bottom: 2rem;
    left: 2rem;
    max-width: 14rem;
    z-index: 10;
    opacity: 1;
    transition: opacity 0.6s ease;
}

.corner-image.hidden {
    opacity: 0;
    pointer-events: none;
}

.corner-image img {
    width: 100%;
    height: auto;
    transition: opacity 0.3s ease;
}

.corner-image:hover img {
    opacity: 1;
}

/* -----------------------------
   Responsive Adjustments
----------------------------- */
@media (max-width: 768px) {
    :global(body:has(#dark-data-survey)) h1 {
        font-size: 4rem;
    }

    :global(body:has(#dark-data-survey)) h2 {
        font-size: 2rem;
    }

    .article-meta .author {
        font-size: var(--font-size-large);
    }

    .article-meta .date {
        font-size: var(--font-size-medium);
    }
}
</style>
