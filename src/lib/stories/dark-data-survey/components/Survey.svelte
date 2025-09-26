<script>
import Scrolly from '$lib/components/helpers/Scrolly.svelte';
import RadioQuestion from './RadioQuestion.svelte';
import { postAnswer } from '../data/data.remote.js';
import FingerprintJS from '@fingerprintjs/fingerprintjs';

let { scrollyState } = $props();

// Survey selections
let socialMedia = $state('');
let platformMatters = $state('');
let institutionPreferences = $state('');
let demographicsMatter = $state('');

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
</script>

<section id="survey">
    <div class="scrolly-container survey-scrolly">
        <div class="scrolly-content">
            <div class="spacer"></div>
            <Scrolly bind:value={scrollyState.scrollyIndex}>
                <div class="step" class:active={scrollyState.scrollyIndex === 0}>
                    <div class="step-content">
                        <RadioQuestion 
                            question="How do you typically set your social media privacy?"
                            name="socialMedia"
                            bind:value={socialMedia}
                            options={[
                                { value: 'private', label: 'Private' },
                                { value: 'mixed', label: 'Mixed' },
                                { value: 'public', label: 'Public' }
                            ]}
                            onchange={() => postAnswer({ fingerprint: userFingerprint, value: socialMedia, field: 'socialMediaPrivacy' })}
                        />
                    </div>
                </div>

                <div class="step" class:active={scrollyState.scrollyIndex === 1}>
                    <div class="step-content">
                        <RadioQuestion 
                            question="Does the platform matter for your privacy decisions?"
                            name="platformMatters"
                            bind:value={platformMatters}
                            options={[
                                { value: 'yes', label: 'Yes, platform matters' },
                                { value: 'no', label: 'No, same across platforms' },
                                { value: 'sometimes', label: 'Sometimes' }
                            ]}
                            onchange={() => postAnswer({ fingerprint: userFingerprint, value: platformMatters, field: 'platformMatters' })}
                        />
                    </div>
                </div>

                <div class="step" class:active={scrollyState.scrollyIndex === 2}>
                    <div class="step-content">
                        <RadioQuestion 
                            question="Do your privacy preferences vary by institution type?"
                            name="institutionPreferences"
                            bind:value={institutionPreferences}
                            options={[
                                { value: 'vary-greatly', label: 'Vary greatly' },
                                { value: 'mostly-same', label: 'Mostly the same' },
                                { value: 'depends-context', label: 'Depends on context' }
                            ]}
                            onchange={() => postAnswer({ fingerprint: userFingerprint, value: institutionPreferences, field: 'institutionPreferences' })}
                        />
                    </div>
                </div>

                <div class="step" class:active={scrollyState.scrollyIndex === 3}>
                    <div class="step-content">
                        <RadioQuestion 
                            question="Do demographics (who you are) influence your privacy preferences?"
                            name="demographicsMatter"
                            bind:value={demographicsMatter}
                            options={[
                                { value: 'yes', label: 'Yes, who I am matters' },
                                { value: 'no', label: 'No, preferences are universal' },
                                { value: 'somewhat', label: 'Somewhat' }
                            ]}
                            onchange={() => postAnswer({ fingerprint: userFingerprint, value: demographicsMatter, field: 'demographicsMatter' })}
                        />
                    </div>
                </div>
            </Scrolly>
            <div class="spacer"></div>
        </div>
    </div>
</section>

<style>
    .survey-scrolly .scrolly-content {
        width: 100%;
        display: flex;
        flex-direction: column;
        align-items: center;
    }

    @media (max-width: 768px) {
        .survey-scrolly .scrolly-content .step-content {
            max-width: 300px;
        }
    }

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
        background: #fef9f3;
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
</style>