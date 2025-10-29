<script>
  import { fade } from 'svelte/transition';

  let { links, nodes } = $props()

  const idToX = new Map(nodes.map(d => [String(d.id), d.x]));
  const idToY = new Map(nodes.map(d => [String(d.id), d.y]));


</script>

<g class="links">
  {#each links as e}
          <line
          x1={idToX.get(e.source?.id ?? e.source)}
          x2={idToX.get(e.target?.id ?? e.target)}
          y1={idToY.get(e.source?.id ?? e.source)}
          y2={idToY.get(e.target?.id ?? e.target)}
          opacity="0.2"
          stroke-width={Math.sqrt(e.value)}
          stroke="hsla(212, 10%, 53%, 1)"
          in:fade={{ duration: 400 }}
          out:fade={{ duration: 400 }}
          ></line>  
  {/each}
</g>