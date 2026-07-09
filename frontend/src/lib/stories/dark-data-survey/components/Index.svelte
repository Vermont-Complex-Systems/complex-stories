<script>
       
import { base } from "$app/paths";
import { innerWidth, outerHeight } from 'svelte/reactivity/window';
import { ArrowDown, Volume2, VolumeOff } from "@lucide/svelte";
import { fade } from 'svelte/transition';

import { audio } from '../state.svelte.ts';
import Nav from './Nav.svelte';
import TrustEvo from './TrustEvo.svelte';
import Dashboard from './Dashboard.svelte';

import { scrollyContent, renderTextContent } from '$lib/components/helpers/ScrollySnippets.svelte';
import WaffleChart from "./WaffleChart.svelte";

import taste_for_privacy_raw from '../data/taste_for_privacy_aggregated.csv';

let { story, data } = $props();

let storyScrollyState = $state({
    scrollyIndex: undefined,
    isMobile: false,
    isTablet: false
});


// Layout calculations using D3 - responsive width and height
let width = $state(innerWidth.current);
let height = $state(outerHeight.current);

// Responsive breakpoints
let isMobile = $derived(innerWidth.current <= 768);

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
            showScrollIndicator = window.scrollY < 50;
        };

        window.addEventListener('scroll', handleScroll);
        return () => window.removeEventListener('scroll', handleScroll);
    }
});

</script>


{#if isMobile}
<Nav />
{/if}

{#if showScrollIndicator}
    <div class="scroll-indicator" transition:fade={{ duration: 500 }}>
        <ArrowDown size={32} strokeWidth={2} />
    </div>
{/if}

<article id="dark-data-survey">

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

    <div class="audio-notice">
        <p>This story has audio in the form of a data sonification.</p>
        <button
            class="enable-audio"
            type="button"
            onclick={() => audio.toggle()}
            aria-pressed={audio.enabled}
        >
            {#if audio.enabled}
                <VolumeOff size={16} strokeWidth={2} aria-hidden="true" />
                Click here to disable
            {:else}
                <Volume2 size={16} strokeWidth={2} aria-hidden="true" />
                Click here to enable
            {/if}
        </button>
    </div>

    <section id="intro">
        {#each data.intro as item}
            {#if item.value == 'WaffleChart'} 
                <WaffleChart />
            {/if}
            {@render renderTextContent(item)}
        {/each}
    </section>

    <section id="story">
        <div class="scrolly-container" bind:this={storySection}>
            <div class="scrolly-chart">
                <TrustEvo
                    data={taste_for_privacy_raw}
                    scrollyIndex={storyScrollyState.scrollyIndex}
                    {width} {height}
                    isStorySection={storyScrollyState.scrollyIndex !== undefined}
                    {storySection}
                    {conclusionVisible}
                    showACESSlider={storyScrollyState.scrollyIndex >= 11 && storyScrollyState.scrollyIndex <= 15} />
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

    {#if !isMobile}
    <section id="dashboard" bind:this={dashboardSection}>
        <div class="scrolly-container">
            <div class="scrolly-chart">
                <Dashboard data={taste_for_privacy_raw} {width} {height} />
            </div>
        </div>
    </section>
    {/if}
</article>

<button
    class="audio-toggle"
    type="button"
    onclick={() => audio.toggle()}
    aria-pressed={audio.enabled}
    aria-label={audio.enabled ? 'Pause story audio' : 'Play story audio'}
    title={audio.enabled ? 'Pause audio' : 'Play audio'}
>
    {#if audio.enabled}
        <Volume2 size={20} strokeWidth={2} aria-hidden="true" />
    {:else}
        <VolumeOff size={20} strokeWidth={2} aria-hidden="true" />
    {/if}
</button>

{#if !isMobile}
<div class="corner-image" class:hidden={conclusionVisible || dashboardVisible}>
    <a href="{base}/">
        <img src="{base}/common/thumbnails/screenshots/dark-data-survey.png" alt="Dark data visualization" />
    </a>
</div>
{/if}

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
   Audio Notice
----------------------------- */
.audio-notice {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.75rem;
    margin: 0 auto 4rem auto;
    max-width: 30rem;
    text-align: center;
}

/* Global to outrank the `#dark-data-survey p` rule above. */
:global(#dark-data-survey .audio-notice p) {
    margin: 0;
    font-size: var(--font-size-small);
    color: var(--color-tertiary-gray);
}

.enable-audio {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    background: #1d1f26;
    color: #f7f3ea;
    border: 1px solid #3c3f4c;
    border-radius: 999px;
    padding: 0.5rem 0.9rem;
    font-family: var(--sans);
    font-size: 0.85rem;
    letter-spacing: 0.02em;
    cursor: pointer;
}

.enable-audio:hover {
    border-color: #6b7080;
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
    top: calc(50vh - 63%);
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
    pointer-events: none;
    transition: opacity 0.3s ease;
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
   Floating Audio Toggle
----------------------------- */
.audio-toggle {
    position: fixed;
    bottom: 2rem;
    right: 2rem;
    z-index: 2000;
    display: flex;
    align-items: center;
    justify-content: center;
    width: 3rem;
    height: 3rem;
    background: #1d1f26;
    color: #f7f3ea;
    border: 1px solid #3c3f4c;
    border-radius: 50%;
    cursor: pointer;
    transition: border-color 0.3s ease, opacity 0.3s ease;
}

.audio-toggle:hover {
    border-color: #6b7080;
}

.audio-toggle[aria-pressed='false'] {
    opacity: 0.6;
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
        margin-top: 10rem;
        margin-bottom: 2rem;
    }

    .article-meta .author {
        font-size: var(--font-size-xlarge);
    }

    .article-meta .author a {
        font-size: var(--font-size-xlarge);
    }

    .article-meta .date {
        font-size: var(--font-size-large);
    }

    #conclusion {
        margin-top: 0;
    }

    .audio-toggle {
        bottom: 1rem;
        right: 1rem;
        width: 2.5rem;
        height: 2.5rem;
    }

    .scrolly-chart {
        top: calc(50vh - 75%);
    }
}
</style>

