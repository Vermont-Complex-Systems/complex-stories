<script>
import { renderSurveyContent } from './Snippets.svelte';
import { surveyScrollyContent } from '$lib/components/helpers/ScrollySnippets.svelte';
import DemographicsBox from './Survey.DemographicsBox.svelte';
import copy from '../data/copy.json';

let { scrollyState, userFingerprint, saveAnswer } = $props();

// Answers object - keys match question 'name' fields in copy.json
let answers = $state({
    socialMediaPrivacy: '',
    platformMatters: [],
    relativePreferences: '',
    govPreferences: '',
    polPreferences: '',
});
</script>

{#snippet surveyRenderer(item, active)}
    {@render renderSurveyContent(item, userFingerprint, saveAnswer, answers)}
{/snippet}

<section id="survey">
    {@render surveyScrollyContent(copy.survey, scrollyState, surveyRenderer)}

    <!-- Demographics questions after scrolly -->
    <DemographicsBox {userFingerprint} {saveAnswer} />
</section>