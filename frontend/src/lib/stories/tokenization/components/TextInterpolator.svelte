<script>
  import { interpolateNumber } from 'd3-interpolate';
  import { extractTextElementsFromSVG	 } from "../utils/svgExtract";
import svg1String from '../assets/sentence-diagram-1.svg?raw';
import svg2String from '../assets/sentence-diagram-2.svg?raw';
import svg3String from '../assets/sentence-diagram-3.svg?raw';
import links from '../assets/only-links.svg?raw';
import boxes from '../assets/only-boxes.svg?raw';
// import d3
import { select } from 'd3-selection';

	const svg1Texts = extractTextElementsFromSVG(svg1String);
	const svg2Texts = extractTextElementsFromSVG(svg2String);
    const svg3Texts = extractTextElementsFromSVG(svg3String);

    // words to start at 0 opacity
    // and animate to full opacity
    // as progress increases
    const posWords = ["Adverb", "Verb", "Noun", "Preposition", "Adverb", "Adjective"]

  export let progress = 0; // 0=start, 1=end
  export let currentStep = 0; // current step index

  // function to draw a svg rectangle with x and y as parameters
  function drawRect(x, y, width=100, height=30) {
    return `<rect x="${x}" y="${y}" width="${width}" height="${height}" fill="#FCAEBB" fill-opacity="0" stroke="#333" stroke-width="2"/>`;
  }

  // Remove the getInterpolatedTexts function and replace with a reactive variable
$: interpolatedTexts = (() => {
  if (currentStep >= 0 && currentStep < 1) {
    return svg1Texts;
  } else if (currentStep >= 1 && currentStep < 2) {
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
  } else if (currentStep >= 2 && currentStep < 3) {
    return svg2Texts.map(t2 => {
      const t3 = svg3Texts.find(t => t.id === t2.id);
      if (!t3) return t2;
      return {
        id: t2.id,
        text: t2.text,
        x: interpolateNumber(t2.x, t3.x)(progress),
        y: interpolateNumber(t2.y, t3.y)(progress),
        opacity: 1
      };
    });
  } else if (currentStep >= 3) {
    return svg3Texts;
  } else {
    return svg1Texts;
  }
})();
</script>

<svg width="800" height="600" id="word-chart" style="margin-left: 100px">
    {#if currentStep > 0 && currentStep < 3}
    {@html links}
    {/if}
    {#if currentStep >= 3}
      {#each svg3Texts as t}
        {@html drawRect(t.x - (t.text.length * 8 + 20) / 2, t.y - 20, t.text.length * 8 + 20, 30)}
      {/each}
    {/if}
  {#each interpolatedTexts as t}
  
    {#if posWords.includes(t.text)}
    {#if currentStep > 0 && currentStep < 3}
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