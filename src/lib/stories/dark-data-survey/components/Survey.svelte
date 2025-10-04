<script>
import Scrolly from '$lib/components/helpers/Scrolly.svelte';
import RadioQuestion from './RadioQuestion.svelte';
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
            console.log('Fingerprint loaded:', userFingerprint);
        }).catch(err => {
            console.error('Failed to load fingerprint:', err);
        });
    }
});

// Helper to safely post answers
async function saveAnswer(field, value) {
    if (!userFingerprint) {
        console.warn('Fingerprint not ready yet, skipping save');
        return;
    }
    try {
        const response = await fetch('/api/survey', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ fingerprint: userFingerprint, value, field })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to save');
        }

        console.log(`Successfully saved ${field}: ${value}`);
    } catch (err) {
        console.error(`Failed to save ${field}:`, err);
    }
}
</script>

<!-- GENDER AND RACE AND PLATFORM USAGE -->
<!-- ADVERSE TRAUMA -->

<section id="survey">
    <div class="scrolly-container survey-scrolly">
        <div class="scrolly-content">
            <div class="spacer"></div>
            <Scrolly bind:value={scrollyState.scrollyIndex}>
                <div class="step" class:active={scrollyState.scrollyIndex === 0}>
                    <div class="step-content">
                        <RadioQuestion
                            question="Are your social media profiles typically public or private?"
                            bind:value={socialMedia}
                            options={[
                                { value: 'private', label: 'Private' },
                                { value: 'mixed', label: 'Mixed' },
                                { value: 'public', label: 'Public' }
                            ]}
                            onchange={() => saveAnswer('socialMediaPrivacy', socialMedia)}
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
                            onchange={() => saveAnswer('platformMatters', platformMatters)}
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
                            onchange={() => saveAnswer('institutionPreferences', institutionPreferences)}
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
                            onchange={() => saveAnswer('demographicsMatter', demographicsMatter)}
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
        background: white;
        color: #333;
        border-radius: 2px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.12), 0 1px 2px rgba(0, 0, 0, 0.24);
        transition: all 500ms ease;
        max-width: 360px;
        margin: 0 auto;
        width: 100%;
        opacity: 0.3;
        font-family: 'Georgia', 'Times New Roman', Times, serif;
    }

    .scrolly-content .step.active .step-content {
        opacity: 1;
    }
</style>