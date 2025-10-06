<script>
import { surveyScrollyContent } from './Snippets.svelte';
import DemographicsBox from './DemographicsBox.svelte';
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

<section id="survey">
    <div class="scrolly-container survey-scrolly">
        {@render surveyScrollyContent(copy.survey, scrollyState, userFingerprint, saveAnswer, answers)}
    </div>

    <!-- Demographics questions after scrolly -->
    <DemographicsBox {userFingerprint} {saveAnswer} />
</section>