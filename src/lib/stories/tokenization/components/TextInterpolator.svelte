<script>
  import { interpolateNumber } from 'd3-interpolate';
  import { extractTextElementsFromSVG	 } from "../utils/svgExtract";
import svg1String from '../assets/sentence-diagram-1.svg?raw';
import svg2String from '../assets/sentence-diagram-2.svg?raw';
import svg3String from '../assets/sentence-diagram-3.svg?raw';
import links from '../assets/only-links.svg?raw';
import boxes from '../assets/only-boxes.svg?raw';

	const svg1Texts = extractTextElementsFromSVG(svg1String);
	const svg2Texts = extractTextElementsFromSVG(svg2String);
    const svg3Texts = extractTextElementsFromSVG(svg3String);

    // words to start at 0 opacity
    // and animate to full opacity
    // as progress increases
    const posWords = ["Adverb", "Verb", "Noun", "Preposition", "Adverb", "Adjective"]

  export let progress = 0; // 0=start, 1=end
  export let currentStep = 0; // current step index

  // Match texts by id (or text content)
function getInterpolatedTexts() {
    switch (true) {
        case currentStep < 1:
            return svg1Texts; // initial state
        case currentStep === 1:
            // interpolate between svg1Texts and svg2Texts
            return svg1Texts.map(t1 => {
                const t2 = svg2Texts.find(t => t.id === t1.id);
                if (!t2) return t1;
                return {
                    id: t1.id,
                    text: t1.text,
                    x: interpolateNumber(t1.x, t2.x)(progress),
                    y: interpolateNumber(t1.y, t2.y)(progress),
                    opacity: progress
                };
            });
        case currentStep === 2:
            // interpolate between svg2Texts and svg3Texts
            return svg2Texts.map(t2 => {
                const t3 = svg3Texts.find(t => t.id === t2.id);
                if (!t3) return t2;
                return {
                    id: t2.id,
                    text: t2.text,
                    x: interpolateNumber(t2.x, t3.x)(progress),
                    y: interpolateNumber(t2.y, t3.y)(progress),
                    opacity: 0
                };
            });
        default:
            return svg3Texts;
    }
}
</script>

<svg width="800" height="600">
    {#if currentStep == 1}
    {@html links}
    {/if}
    {#if currentStep >= 2}
    {@html boxes}
    {/if}
  {#each getInterpolatedTexts() as t}
  
    {#if posWords.includes(t.text)}
    {#if currentStep == 1}
      <text x={t.x} y={t.y} text-anchor="middle" class="pos-tags" font-size="24" fill="#000" opacity={t.opacity}>
        {t.text}
      </text>
      {/if}
    {:else}
      <text x={t.x} y={t.y} text-anchor="middle" font-size="24" fill="#222">
        {t.text}
      </text>
    {/if}
    
  {/each}
  
</svg>