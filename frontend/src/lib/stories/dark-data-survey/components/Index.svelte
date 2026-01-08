<script>
import { base } from "$app/paths";
import { innerWidth, outerHeight } from 'svelte/reactivity/window';
import { ArrowDown } from "@lucide/svelte";

import { generateFingerprint } from '$lib/utils/browserFingerprint.js';

import TrustEvo from './TrustEvo.svelte';
import ConsentPopup from './ConsentPopup.svelte';
import Dashboard from './Dashboard.svelte';
import DemographicsBox from './Survey.DemographicsBox.svelte';

import { scrollyContent, renderTextContent } from '$lib/components/helpers/ScrollySnippets.svelte';
import { surveyScrollyContent } from '$lib/components/survey/SurveyScrolly.svelte';
import { postAnswer, upsertAnswer } from '../data/data.remote.js';

let { story, data } = $props();

// Consent state
let hasConsented = $state(false);

// Generate browser fingerprint AFTER consent (GDPR/CCPA compliance)
let userFingerprint = $state('');
let saveAnswer = $derived(createSaveAnswerHandler(userFingerprint));


async function handleConsentAccept() {
    hasConsented = true;

    try {
        userFingerprint = await generateFingerprint();
        console.log('Fingerprint loaded:', userFingerprint);

        // Save consent after fingerprint is ready
        if (userFingerprint) {
            await saveAnswer('consent', 'accepted');
        }
    } catch (err) {
        console.error('Failed to load fingerprint:', err);
    }
}

// Survey answers - keys match question 'name' fields in copy.json
let surveyAnswers = $state({
    socialMediaPrivacy: '',
    platformMatters: [],
    relativePreferences: '',
    govPreferences: '',
    polPreferences: '',
});

/**
 * Story-specific saveAnswer adapter
 * Maps form field names to appropriate API calls based on field type
 * Kept here to ensure field mapping stays in sync with surveyAnswers definition above
 */
function createSaveAnswerHandler(userFingerprint) {
	return function saveAnswer(field, value) {
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
	};
}

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

// Scroll indicator visibility
let showScrollIndicator = $state(true);

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

// Hide scroll indicator when user scrolls
$effect(() => {
    if (typeof window !== 'undefined') {
        const handleScroll = () => {
            showScrollIndicator = window.scrollY < 100;
        };

        window.addEventListener('scroll', handleScroll);
        return () => window.removeEventListener('scroll', handleScroll);
    }
});

</script>


<!-- Consent Popup -->
<ConsentPopup onAccept={handleConsentAccept} {userFingerprint} {saveAnswer} />

<!-- Scroll indicator -->
{#if showScrollIndicator}
    <div class="scroll-indicator">
        <ArrowDown size={32} strokeWidth={2} />
    </div>
{/if}

<article id="dark-data-survey">

    <!-- Survey Section -->
    <section id="survey">
        {@render surveyScrollyContent(data.survey, surveyScrollyState, userFingerprint, saveAnswer, surveyAnswers)}

        <!-- Demographics questions after scrolly -->
        <DemographicsBox {userFingerprint} {saveAnswer} />
    </section>

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
        {#each data.intro as item}
            {@render renderTextContent(item)}
        {/each}
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
        {#each data.conclusion as item}
            {@render renderTextContent(item)}
        {/each}
    </section>

    <section id="dashboard" bind:this={dashboardSection}>
        <Dashboard {width} {height} />
    </section>
</article>

<div class="corner-image" class:hidden={conclusionVisible || dashboardVisible}>
    <a href="{base}/">
        <img src="{base}/common/thumbnails/screenshots/dark-data-survey.png" alt="Dark data visualization" />
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

/* Survey styling override */
:global(#dark-data-survey #survey .survey-scrolly .step-content) {
    font-family: 'Georgia', 'Times New Roman', Times, serif;
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
   NOTE: This story uses a dark theme. All text is whitesmoke by default,
   with specific sections overriding to black for readability.
   This is scoped to #dark-data-survey so it won't affect other stories.
----------------------------- */
:global(#dark-data-survey p) {
    color: whitesmoke;
}

/* Make sure intro & conclusion text remain white - MUST scope to this story! */
:global(#dark-data-survey #intro p),
:global(#dark-data-survey #conclusion p) {
    color: whitesmoke;
}

/* Scrolly text specifically black for readability against light backgrounds */
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

/* Override shared ScrollySnippets styling for this story's dark theme */
:global(#dark-data-survey .scrolly-content .step > *) {
    padding: 1rem;
    background: #f5f5f5;
    color: #ccc;
    border-radius: 5px;
    box-shadow: 1px 1px 10px rgba(0, 0, 0, 0.2);
    transition: all 500ms ease;
    text-align: center;
    max-width: 600px;
    margin: 0 auto;
}

:global(#dark-data-survey .scrolly-content .step.active > *) {
    background: white;
    color: black;
}

/* -----------------------------
   Scroll Indicator
----------------------------- */
.scroll-indicator {
    position: fixed;
    bottom: 2rem;
    left: 50%;
    transform: translateX(-50%);
    z-index: 100;
    color: whitesmoke;
    opacity: 0.7;
    animation: bounce 2s infinite ease-in-out;
    cursor: pointer;
    transition: opacity 0.3s ease;
}

.scroll-indicator:hover {
    opacity: 1;
}

@keyframes bounce {
    0%, 100% {
        transform: translateX(-50%) translateY(0);
    }
    50% {
        transform: translateX(-50%) translateY(-10px);
    }
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
