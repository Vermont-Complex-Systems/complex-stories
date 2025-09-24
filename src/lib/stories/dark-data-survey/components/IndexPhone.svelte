<script>
import { base } from "$app/paths";
import { scaleSequential } from 'd3-scale';
import { interpolateRdYlGn } from 'd3-scale-chromatic';
import { innerWidth } from 'svelte/reactivity/window';

import Md from '$lib/components/helpers/MarkdownRenderer.svelte';
import Scrolly from '$lib/components/helpers/Scrolly.svelte';
import UnifiedPhone from './UnifiedPhone.svelte';

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
                    
                    <!-- Fixed phone that stays in position -->
                    <div class="fixed-phone-container">
                        <UnifiedPhone scrollyIndex={scrollyIndex} />
                    </div>
                    
                    <!-- Scrolly steps that trigger content changes -->
                    <Scrolly bind:value={scrollyIndex}>
                        <div class="step">
                            <div class="step-content">
                                <!-- This step triggers Facebook settings (scrollyIndex = 0) -->
                            </div>
                        </div>
                        
                        <div class="step">
                            <div class="step-content">
                                <!-- This step triggers Safari/OpenAI (scrollyIndex = 1) -->
                            </div>
                        </div>
                        
                        <div class="step">
                            <div class="step-content">
                                <!-- This step triggers Government app (scrollyIndex = 2) -->
                            </div>
                        </div>
                        
                        <div class="step">
                            <div class="step-content">
                                <!-- This step triggers Demographics (scrollyIndex = 3) -->
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
        position: relative;
        min-height: 400vh; /* Make it tall enough for 4 scroll steps */
    }
    
    .fixed-phone-container {
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        z-index: 10;
        pointer-events: auto;
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
        .fixed-phone-container {
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            z-index: 10;
            width: 100vw;
            height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .content {
            min-height: 400vh; /* Keep the scroll height for step detection */
        }
    }

    /* Step styling - invisible but trigger scroll changes */
    .step {
        width: 100%;
        height: 100vh;
        display: flex;
        align-items: center;
        justify-content: center;
        /* Make steps invisible since we only need them for scroll detection */
    }

    .step-content {
        width: 100%;
        max-width: 800px;
        display: flex;
        align-items: center;
        justify-content: center;
        text-align: center;
        /* Steps are now just scroll triggers, no content needed */
        opacity: 0;
        pointer-events: none;
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