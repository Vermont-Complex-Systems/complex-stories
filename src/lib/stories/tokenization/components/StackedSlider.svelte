<svelte:options runes />
<script>
  // Number of divs/words to highlight
  let value = $state(1);
  const min = 1;
  const max = 10;

  // Example text
  const text = "The quick brown fox jumps over the lazy dog in the park.";
  const words = text.split(" ");

  // Clamp value to max number of words
  let highlightCount = $derived(Math.min(value, words.length));
</script>

<div style="margin-bottom: 1.5rem;">
  <label for="slider">Number: {value}</label>
  <input id="slider" type="range" min={min} max={words.length} bind:value />
</div>

<!-- Stacked divs -->
<div style="display: flex; flex-direction: column; gap: 8px; align-items: flex-start; margin-bottom: 1.5rem;">
  {#each Array(value) as _, i}
    <div style="width: 200px; height: 32px; border: 2px solid #888; border-radius: 6px; background: #faf9f6;"></div>
  {/each}
</div>

<!-- Highlighted text -->
<p style="font-size: 1.2rem; line-height: 1.7;">
  {#each words as word, i}
    <span style="background: {i < highlightCount ? '#ffe066' : 'none'}; border-radius: 4px; padding: 0 4px; transition: background 0.2s;">
      {word}
    </span>{i < words.length - 1 ? ' ' : ''}
  {/each}
</p>
