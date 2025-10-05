<script>
import FingerprintJS from '@fingerprintjs/fingerprintjs';
import { surveyScrollyContent } from './Snippets.svelte';
import copy from '../data/copy.json';

let { scrollyState } = $props();

// Answers object - keys match question 'name' fields in copy.json
let answers = $state({
    socialMediaPrivacy: '',
    platformMatters: '',
    institutionPreferences: '',
});

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

<section id="survey">
    <div class="scrolly-container survey-scrolly">
        {@render surveyScrollyContent(copy.survey, scrollyState, userFingerprint, saveAnswer, answers)}
    </div>
</section>