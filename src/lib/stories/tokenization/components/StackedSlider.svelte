<svelte:options runes />
<script>
  import trollImg from '../assets/julia-illos/troll.png?url'

  // Number of divs/words to highlight
  let value = $state(1);
  const min = 1;
  const max = 25;

  // define value of slider as local variable for binding
  let {sliderValue=1, renderMode: renderModeProp, scrollyIndex} = $props();
  
  
  // if scrollyIndex is greater than 2 change renderMode to 'chars'
  let renderMode = $derived(
    scrollyIndex > 2 ? 'chars' : (renderModeProp ?? 'words')
  );

  let charCheck = $derived(
    scrollyIndex > 2 ? true : false
  )

  // Example text
  const text = "We certainly do not forget you so soon as you forget us. It is perhaps our fate rather than our merit. We cannot help ourselves. We live at home, quiet, confined, and our feelings prey upon us. You are forced on exertion.";
  const words = text.split(" ");
  const chars = text.split("");

  // Clamp value to max number of words
  let highlightCount = $derived(Math.min(sliderValue, words.length));

  // Define highlight colors for each group
  const highlightColors = [
    '#ffe066', // yellow
    '#ffb3c6', // pink
    '#b5ead7', // mint
    '#bdb2ff', // purple
    '#ffd6a5', // orange
    '#caffbf', // green
    '#9bf6ff', // blue
    '#fdffb6', // light yellow
    '#ffc6ff', // light pink
    '#a0c4ff'  // light blue
  ];
</script>

<h3>How big is a token?</h3>
<div style="margin-bottom: 1.5rem; margin-top: 15%;display: flex; gap: 2rem; align-items: center;">
  <div>
    <label for="slider">Number: {sliderValue}</label>
    <input id="slider" type="range" min={1} max={25} bind:value={sliderValue} />
  </div>
  <div>
    <img src={trollImg} alt="Troll" style="width: 200px; height: auto;" />
  </div>
</div>


<!-- Highlighted text (words or characters) -->
{#if renderMode === 'words'}
  <p style="font-size: 1.2rem; line-height: 1.7;">
    {#each words as word, i}
      {#if sliderValue > 0}
        <span style="background: {highlightColors[Math.floor(i / sliderValue) % highlightColors.length]}; border-radius: 4px; padding: 0 4px; transition: background 0.8s;">
          {word}
        </span>{i < words.length - 1 ? ' ' : ''}
      {:else}
        <span>{word}</span>{i < words.length - 1 ? ' ' : ''}
      {/if}
    {/each}
  </p>
{:else}
  <p style="font-size: 1.2rem; line-height: 1.7; word-break: break-all;">
    {#each chars as char, i}
      {#if sliderValue > 0}
        <span style="background: {highlightColors[Math.floor(i / sliderValue) % highlightColors.length]}; border-radius: 4px; padding: 0 2px; transition: background 0.8s;">
          {char === ' ' ? '\u00A0' : char}
        </span>
      {:else}
        <span>{char === ' ' ? '\u00A0' : char}</span>
      {/if}
    {/each}
  </p>
{/if}

<!-- Stacked divs -->
 <h4>size of model</h4>
 
{#if !charCheck}
  <div id="slider" style="display: flex; flex-wrap: wrap; gap: 16px; align-items: flex-start; margin-bottom: 1.5rem; max-height: 250px; max-width: 400px; overflow-y: auto;">
    {#each Array(Math.max(1, max - sliderValue + 1)) as _, i}
      <div style="width: 50px; height: 12px; border: 2px solid #888; border-radius: 4px; background: #faf9f6; margin-bottom: 8px;"></div>
    {/each}
  </div>
{/if}

{#if charCheck}
  <div id="slider" style="display: flex; flex-wrap: wrap; gap: 16px; align-items: flex-start; margin-bottom: 1.5rem; max-height: 250px; overflow-y: auto;">
    {#each Array(Math.max(1, 100)) as _, i}
      <div style="width: 50px; height: 12px; border: 2px solid #888; border-radius: 4px; background: #faf9f6; margin-bottom: 8px;"></div>
    {/each}
  </div>
{/if}


