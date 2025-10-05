<script>
import { base } from "$app/paths";
import { scaleSequential } from 'd3-scale';
import { interpolateRdYlGn } from 'd3-scale-chromatic';
import { innerWidth, outerHeight } from 'svelte/reactivity/window';

import Md from '$lib/components/helpers/MarkdownRenderer.svelte';
import Scrolly from '$lib/components/helpers/Scrolly.svelte';

import TrustEvo from './TrustEvo.svelte';
import Survey from './Survey.svelte';

import { renderContent, scrollyContent } from './Snippets.svelte';

let { story, data } = $props();

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

</script>

<article id="dark-data-survey">
    
    <Survey bind:scrollyState={surveyScrollyState} />

    <div class="title">
        <h1>{data.title}</h1>
        <h2>{data.subtitle}</h2>

        <div class="article-meta">
            <p class="author">
                By {@html data.author1} and {@html data.author2}
            </p>
            <p class="date">
                {data.date}
            </p>
        </div>
    </div>

    <!-- Text Intro -->
    <section id="intro">
        {@render renderContent(data.intro)}
    </section>

    <!-- ScrollyPlot -->
    <!-- <h2>{data.ScrolylSectionTitle}</h2> -->
    <section id="story">
        <div class="scrolly-container" bind:this={storySection}>
            <div class="scrolly-chart">
                <TrustEvo
                    scrollyIndex={storyScrollyState.scrollyIndex} 
                    {selectedDemographic} 
                    {width} {height}
                    isStorySection={true}
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
</article>

<div class="corner-image" class:hidden={conclusionVisible}>
    <img src="{base}/common/thumbnails/screenshots/dark-data.png" alt="Dark data visualization" />
</div>

<style>

    :global(body:has(#dark-data-survey)) {
        overflow-x: hidden;
        background-color: #2b2b2b;
        color: #ffffff;
    }

    :global(body:has(#dark-data-survey)) h1, h2 {
        font-family: var(--serif);
        max-width: 450px;
        font-size: var(--font-size-giant);
        margin: 6rem auto 1rem auto;
        text-align: center;
    }    

    :global(body:has(#dark-data-survey)) .title {
        margin: 0 auto 5rem auto;
    }

    :global(body:has(#dark-data-survey)) h2 {
        font-size: var(--font-size-medium);
        font-weight: 400;
        margin: 0 auto 3rem auto;
        text-align: center;
    }    
    
    :global(body:has(#dark-data-survey)) p {
        color: whitesmoke !important;
    }
    
    /* Ensure intro text is white */
    :global(#intro p) {
        color: whitesmoke !important;
    }    
    
    :global(#conclusion p) {
        color: whitesmoke !important;
    }    
    
    /* Make scrolly content black for readability */
    :global(.scrolly-container .markdown-content),
    :global(.scrolly-container .markdown-content p) {
        color: black !important;
    }    

    .logo-container {
        margin: 1rem auto 0 auto;
        max-width: 8rem;
        position: relative;
    }

    .article-meta {
        margin: -1rem auto 2rem auto;
        font-family: var(--sans);
        max-width: 30rem;
        text-align: center;
    }
    
    .article-meta .author {
        font-size: var(--font-size-medium);
        color: var(--color-secondary-gray);
        margin: 0 0 0.25rem 0;
        font-weight: 500;
        text-align: center !important;
    }
    
    .article-meta .date {
        font-size: var(--font-size-small);
        color: var(--color-tertiary-gray);
        margin: 0;
        font-weight: 400;
        text-align: center !important;
    }



    /* -----------------------------

    Scrolly 

    ----------------------------- */

    /* centered layout for text and plot */
    .scrolly-container {
        position: relative;
        min-height: 100vh;

    }
    
    /* make the plot sticky and centered - circle plot */
    .scrolly-chart {
        position: sticky;
        top: calc(50vh - 500px);
        height: fit-content;
        z-index: 1;
        pointer-events: none;
    }

    @media (max-width: 768px) {
        :global(body:has(#dark-data-survey)) h1 {
            font-size: 4rem !important;
        }
        
        :global(body:has(#dark-data-survey)) h2 {
            font-size: 2rem !important;
        }
        
        .article-meta .author {
            font-size: var(--font-size-large) !important;
        }
        
        .article-meta .date {
            font-size: var(--font-size-medium) !important;
        }
        
        .logo-container {
            max-width: 6rem;
        }
    }

    .corner-image {
        position: fixed;
        bottom: 2rem;
        left: 2rem;
        max-width: 10rem;
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

</style>