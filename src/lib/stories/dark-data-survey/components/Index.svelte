<script>
import { base } from "$app/paths";
import { scaleSequential } from 'd3-scale';
import { interpolateRdYlGn } from 'd3-scale-chromatic';
import { innerWidth } from 'svelte/reactivity/window';

import Md from '$lib/components/helpers/MarkdownRenderer.svelte';
import Scrolly from '$lib/components/helpers/Scrolly.svelte';
import MobileSettings from './MobileSettings.svelte';
import OpenAIPolicy from './OpenAIPolicy.svelte';
import GovernmentApp from './GovernmentApp.svelte';

import TrustEvo from './TrustEvo.svelte';

import { generatePeopleByInstitution } from '../data/generatePeople.js';
import { renderContent, scrollyContent, surveyContent } from './Snippets.svelte';
import { submitSurvey } from '../data/data.remote.js';
import FingerprintJS from '@fingerprintjs/fingerprintjs';

let { story, data } = $props();

let scrollyIndex = $state();

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
        <div class="container">
            <form {...submitSurvey}>
                <input type="hidden" name="fingerprint" value={userFingerprint} />
                
                <div class="content">
                    <!-- Debug info -->
                    <div style="position: fixed; top: 10px; left: 10px; background: yellow; padding: 5px; z-index: 9999;">
                        ScrollyIndex: {scrollyIndex}
                    </div>
                    
                    <Scrolly bind:value={scrollyIndex}>
                        <div class="step">
                            <div class="step-content">
                                <MobileSettings title="Settings & privacy" />
                            </div>
                        </div>
                        
                        <div class="step">
                            <div class="step-content">
                                <OpenAIPolicy />
                            </div>
                        </div>
                        
                        <div class="step">
                            <div class="step-content">
                                <GovernmentApp />
                            </div>
                        </div>
                    </Scrolly>
                </div>
            </form>
        </div>
    </section>

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
    :global(body:has(#dark-data-survey)) .title {
        margin: 0 auto 5rem auto;
    }
    
    
    /* -----------------------------

    Survey Layout 

    ----------------------------- */

    .container {
        max-width: 1200px;
        margin: 0 auto;
        padding: 2rem;
    }
    
    .content {
        display: flex;
        justify-content: center;
        align-items: center;
        min-height: 100vh;
    }



    @media (min-width: 1200px) {
        section#survey .scrolly-container {
            width: var(--width-column-wide) !important;
            max-width: none !important;
            margin-left: 50% !important;
            transform: translateX(-45%) !important;
        }
    }

    @media (max-width: 768px) {
        
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

    /* Step styling */
    .step {
        width: 100%;
        height: 100vh;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .step-content {
        width: 100%;
        max-width: 800px;
        display: flex;
        align-items: center;
        justify-content: flex-start;
        text-align: left;
    }

    .chart-image {
        /* max-width: 100%; */
        /* max-height: 500px; */
        width: 100%;
        /* height: auto; */
        /* object-fit: contain; */
    }

    
    .submit-section {
        text-align: center;
        padding: 1rem 0;
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

   

</style>