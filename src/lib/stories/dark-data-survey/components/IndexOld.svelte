<script>
import { base } from "$app/paths";
import { scaleSequential } from 'd3-scale';
import { interpolateRdYlGn } from 'd3-scale-chromatic';
import { innerWidth } from 'svelte/reactivity/window';

import Md from '$lib/components/helpers/MarkdownRenderer.svelte';
import Scrolly from '$lib/components/helpers/Scrolly.svelte';
import MobileSettings from '$lib/components/MobileSettings.svelte';

import TrustEvo from './TrustEvo.svelte';

import { generatePeopleByInstitution } from '../data/generatePeople.js';
import { renderContent, scrollyContent, surveyContent } from './Snippets.svelte';
import { submitSurvey } from '../data/data.remote.js';
import FingerprintJS from '@fingerprintjs/fingerprintjs';

let { story, data } = $props();


// Generate people data using imported function

let people = $state(generatePeopleByInstitution());
let selectedDemographic = $state('white_men');

// Scrolly state management - use object for binding  
let scrollyState = $state({ 
    scrollyIndex: undefined,
    isMobile: false,
    isTablet: false
});

// Update derived values in effect
$effect(() => {
    scrollyState.isMobile = innerWidth.current <= 768;
    scrollyState.isTablet = innerWidth.current <= 1200 && innerWidth.current > 768;
});

// Generate browser fingerprint using FingerprintJS
let userFingerprint = $state('');

$effect(() => {
    if (typeof window !== 'undefined') {
        FingerprintJS.load().then(fp => {
            return fp.get();
        }).then(result => {
            userFingerprint = result.visitorId;
        });
    }
});

// Layout calculations using D3 - keep original size
const width = 1000;
const height = 800;

</script>

<article id="dark-data-survey">
        
    <section id="survey">
        <div class="scrolly-container survey-scrolly">
            
            <form {...submitSurvey}>
                <input type="hidden" name="fingerprint" value={userFingerprint} />
                
                <div class="scrolly-content">
                    <div class="spacer"></div>
                    <Scrolly bind:value={scrollyState.scrollyIndex}>
                        <div class="step" class:active={scrollyState.scrollyIndex === 0}>
                            <div class="step-content">
                                <!-- Debug info -->
                                <div style="position: absolute; top: 0; left: 0; background: yellow; padding: 5px; font-size: 12px; z-index: 1000;">
                                    ScrollyIndex: {scrollyState.scrollyIndex}, isMobile: {scrollyState.isMobile}, innerWidth: {innerWidth.current}
                                </div>
                                
                                {#if scrollyState.isMobile}
                                    <div style="border: 2px solid red; padding: 10px;">
                                        <MobileSettings title="Settings & privacy" />
                                    </div>
                                {:else}
                                    <div class="question-text">
                                        <h3>How do you typically set your social media privacy?</h3>
                                    </div>
                                    <div class="survey-controls">
                                        <select name="socialMedia" aria-invalid={!!submitSurvey.issues.socialMedia}>
                                            <option value="">Choose...</option>
                                            <option value="private">Private</option>
                                            <option value="mixed">Mixed</option>
                                            <option value="public">Public</option>
                                        </select>
                                        {#if submitSurvey.issues.socialMedia}
                                            {#each submitSurvey.issues.socialMedia as issue}
                                                <p class="error">{issue.message}</p>
                                            {/each}
                                        {/if}
                                    </div>
                                {/if}
                            </div>
                        </div>

                        <div class="step" class:active={scrollyState.scrollyIndex === 1}>
                            <div class="step-content">
                                <div class="question-text">
                                    <h3>Does the platform matter for your privacy decisions?</h3>
                                </div>
                                <div class="survey-controls">
                                    <select name="platformMatters" aria-invalid={!!submitSurvey.issues.platformMatters}>
                                        <option value="">Choose...</option>
                                        <option value="yes">Yes, platform matters</option>
                                        <option value="no">No, same across platforms</option>
                                        <option value="sometimes">Sometimes</option>
                                    </select>
                                    {#if submitSurvey.issues.platformMatters}
                                        {#each submitSurvey.issues.platformMatters as issue}
                                            <p class="error">{issue.message}</p>
                                        {/each}
                                    {/if}
                                </div>
                            </div>
                        </div>

                        <div class="step" class:active={scrollyState.scrollyIndex === 2}>
                            <div class="step-content">
                                <div class="question-text">
                                    <h3>Do your privacy preferences vary by institution type?</h3>
                                </div>
                                <div class="survey-controls">
                                    <select name="institutionPreferences" aria-invalid={!!submitSurvey.issues.institutionPreferences}>
                                        <option value="">Choose...</option>
                                        <option value="vary-greatly">Vary greatly</option>
                                        <option value="mostly-same">Mostly the same</option>
                                        <option value="depends-context">Depends on context</option>
                                    </select>
                                    {#if submitSurvey.issues.institutionPreferences}
                                        {#each submitSurvey.issues.institutionPreferences as issue}
                                            <p class="error">{issue.message}</p>
                                        {/each}
                                    {/if}
                                </div>
                            </div>
                        </div>

                        <div class="step" class:active={scrollyState.scrollyIndex === 3}>
                            <div class="step-content">
                                <div class="question-text">
                                    <h3>Do demographics (who you are) influence your privacy preferences?</h3>
                                </div>
                                <div class="survey-controls">
                                    <select name="demographicsMatter" aria-invalid={!!submitSurvey.issues.demographicsMatter}>
                                        <option value="">Choose...</option>
                                        <option value="yes">Yes, who I am matters</option>
                                        <option value="no">No, preferences are universal</option>
                                        <option value="somewhat">Somewhat</option>
                                    </select>
                                    {#if submitSurvey.issues.demographicsMatter}
                                        {#each submitSurvey.issues.demographicsMatter as issue}
                                            <p class="error">{issue.message}</p>
                                        {/each}
                                    {/if}
                                </div>
                            </div>
                        </div>
                        
                        <div class="step" class:active={scrollyState.scrollyIndex === 4}>
                            <div class="step-content">
                                <div class="submit-section">
                                    <button type="submit" disabled={submitSurvey.pending || !userFingerprint}>
                                        {submitSurvey.pending ? 'Submitting...' : 'Submit Survey'}
                                    </button>
                                    
                                    {#if submitSurvey.success}
                                        <p class="success">✅ Thank you! Your responses have been saved.</p>
                                    {/if}
                                </div>
                            </div>
                        </div>
                    </Scrolly>
                    <div class="spacer"></div>
                </div>
            </form>
        </div>
    </section>
    
    <div class="logo-container">
        <a href="{base}/" class="logo-link">
            <img src="{base}/octopus-swim-right.png" alt="Home" class="logo" width="200" />
        </a>
    </div>

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
    <section id="intro">
        {@render renderContent(data.intro)}
    </section>

    <h2>{data.ScrolylSectionTitle}</h2>
    <section id="scrolly">
        <div class="scrolly-container">
            
            <div class="scrolly-chart">
                <TrustEvo scrollyIndex={scrollyState.scrollyIndex} {selectedDemographic} {width} {height} />
            </div>

            {@render scrollyContent(data.steps, scrollyState)}
        </div>
    </section>

    <!-- <p>Spoiler: Privacy depends on who you are and and context.</p>

    <p>Privacy depends on who you are and context. Your willingness to share data varies dramatically across different institutions and relationships.</p> -->

    <!-- Scrollytelling Section -->
    <!-- <div class="chart-container-scrolly"> -->
        <!-- <div class="visualization-container" bind:this={visualizationContainer}>
            <svg {width} {height} class="trust-visualization">
                
                <TrustCircles 
                    {width} 
                    {height} 
                    {centerX} 
                    {centerY} 
                    selectedDemographic={currentView() === 'individual' ? 'white_men' : (currentView() === 'white_men' ? 'white_men' : selectedDemographic)} 
                />
                 -->
                <!-- {#if currentView() === 'individual'}
                    <IndividualUserPoints {centerX} {centerY} {trustworthinessColorScale} />
                {:else if currentView() === 'white_men'}
                    <People {people} selectedDemographic="white_men" {centerX} {centerY} {trustworthinessColorScale} />
                {:else if currentView() === 'demographic'}
                    <People {people} selectedDemographic={selectedDemographic} {centerX} {centerY} {trustworthinessColorScale} />
                {/if} -->
                
                <!-- <CenterEgo {centerX} {centerY} /> -->
                <!-- <Legend x={50} y={50} {trustworthinessColorScale} /> -->
                
            <!-- </svg> -->
            
            <!-- {#if currentView() === 'white_men' || currentView() === 'demographic'}
                <div class="chart-overlay">
                    <TrustDistributionChart {people} selectedDemographic={currentView() === 'white_men' ? 'white_men' : selectedDemographic} {trustworthinessColorScale} />
                </div>
            {/if} -->
                
            <!-- {#if currentView() === 'demographic'}
                <div class="demographic-selector">
                    <label for="demographic-select">Compare demographics:</label>
                    <select id="demographic-select" bind:value={selectedDemographic}>
                        <option value="all">All Demographics</option>
                        <option value="white_men">White Men</option>
                        <option value="black_women">Black Women</option>
                    </select>
                </div>
            {/if} -->
        <!-- </div> -->
    <!-- </div> -->

    <!-- Scrolly steps -->
    
    
    

</article>


<style>

    :global(body:has(#dark-data-survey)) {
        overflow-x: hidden; /* Prevent horizontal scroll from full-width components */
    }

    /* Dark mode support */
    :global(.dark body:has(#dark-data-survey)) {
        background-color: var(--color-bg);
        color: var(--color-fg);
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
        margin-top: 3rem;
    }
    
    /* make the plot sticky and to the left - SURVEY SPECIFIC */
    .survey-chart {
        position: sticky;
        top: calc(50vh - 250px);
        display: flex;
        justify-content: center;
        align-items: center;
        height: fit-content;
        z-index: 1;
        pointer-events: none;
        width: 40%;
        float: left;
    }

    .survey-scrolly .scrolly-content {
        width: 60%;
        margin-left: 40%;
        display: flex;
        flex-direction: column;
        align-items: center;
    }



    @media (min-width: 1200px) {
        section#scrolly .scrolly-container,
        section#survey .scrolly-container {
            width: var(--width-column-wide) !important;
            max-width: none !important;
            margin-left: 50% !important;
            transform: translateX(-45%) !important;
        }
    }

    @media (max-width: 768px) {
        :global(body:has(#cascade-story)) h1 {
            font-size: 4rem !important;
        }
        
        :global(body:has(#cascade-story)) h2 {
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

        /* Mobile survey layout */
        #survey {
            position: relative;
        }

        #survey .survey-chart {
            position: fixed !important;
            top: 50% !important;
            left: 50% !important;
            transform: translate(-50%, -50%) !important;
            width: 95vw !important;
            height: 95vh !important;
            z-index: 0 !important;
            max-width: none !important;
            max-height: none !important;
            float: none !important;
        }


        #survey .survey-scrolly {
            position: relative;
            z-index: 1;
        }

        .survey-scrolly .scrolly-content {
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            width: 45vw;
            height: 60vh;
            z-index: 3;
            pointer-events: none;
        }

        .survey-scrolly .scrolly-content .step {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            display: flex;
            align-items: center;
            justify-content: center;
            opacity: 0;
            transition: opacity 500ms ease;
        }

        .survey-scrolly .scrolly-content .step.active {
            opacity: 1;
        }

        .survey-scrolly .scrolly-content .step-content {
            max-width: 220px;
            background: rgba(255, 255, 255, 0.9);
            color: #333;
            border-radius: 8px;
            padding: 1rem;
            pointer-events: auto;
            text-align: center;
        }
    }

    /* Survey-specific styling */
    .scrolly-content .step {
        height: 80vh;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 1rem;
        margin: 0 auto;
    }

    .scrolly-content .step-content {
        padding: 2rem;
        background: #f5f5f5;
        color: #ccc;
        border-radius: 8px;
        box-shadow: 1px 1px 10px rgba(0, 0, 0, 0.2);
        transition: all 500ms ease;
        max-width: 360px;
        margin: 0 auto;
        width: 100%;
    }

    .scrolly-content .step.active .step-content {
        background: white;
        color: black;
    }

    .chart-image {
        /* max-width: 100%; */
        /* max-height: 500px; */
        width: 100%;
        /* height: auto; */
        /* object-fit: contain; */
    }

    .question-text h3 {
        margin: 0 0 1rem 0;
        font-size: 1.2rem;
        font-weight: 600;
        color: #333;
    }

    .survey-controls select {
        width: 100%;
        padding: 0.75rem;
        border: 2px solid #ddd;
        border-radius: 4px;
        font-size: 1rem;
        background: white;
        cursor: pointer;
        transition: border-color 0.2s ease;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }

    .survey-controls select:hover {
        border-color: var(--color-primary, #007acc);
    }

    .survey-controls select:focus {
        outline: none;
        border-color: var(--color-primary, #007acc);
        box-shadow: 0 0 0 3px rgba(0, 122, 204, 0.1);
    }

    .survey-controls select:not([value=""]) {
        background: #f8f9fa;
        border-color: #28a745;
    }

    .submit-section {
        text-align: center;
        padding: 1rem 0;
    }

    .submit-section button {
        background: #007acc;
        color: white;
        border: none;
        padding: 1rem 2rem;
        border-radius: 8px;
        font-size: 1.1rem;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.2s ease;
        min-width: 150px;
    }

    .submit-section button:hover:not(:disabled) {
        background: #0066aa;
        transform: translateY(-1px);
    }

    .submit-section button:disabled {
        background: #ccc;
        cursor: not-allowed;
        transform: none;
    }

    .success {
        background: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #c3e6cb;
        font-weight: 500;
        margin: 1rem 0;
    }

    .error {
        background: #f8d7da;
        color: #721c24;
        padding: 0.5rem;
        border-radius: 4px;
        border: 1px solid #f5c6cb;
        font-size: 0.9rem;
        margin: 0.5rem 0;
    }

    /* Settings screen styling */
    .settings-screen {
        position: relative;
        width: 100%;
        height: 100vh;
        background: #f8f9fa;
        overflow: hidden;
    }

    .settings-header {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        z-index: 10;
        padding: 1rem;
        border-bottom: 1px solid #e0e0e0;
    }

    .settings-header h3 {
        margin: 0;
        font-size: 1.1rem;
        font-weight: 600;
        color: #333;
        text-align: center;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif;
    }

    .settings-content {
        padding-top: 80px;
        transition: transform 0.5s ease;
    }

    .settings-section {
        padding: 20px;
        background: white;
        margin: 10px;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif;
    }

    .settings-section p {
        margin: 0;
        font-size: 1rem;
        color: #333;
    }

</style>