<script>

    let { 
        annotations = [] // Array of {x, y, text, style} objects
    } = $props();
</script>

{#each annotations as annotation}
  <text
    x={xScale(annotation.x)}
    y={yScale(annotation.y)}
    fill={annotation.style?.color || "var(--color-fg)"}
    font-size={annotation.style?.fontSize || "12px"}
    font-weight={annotation.style?.fontWeight || "normal"}
    text-anchor={annotation.style?.textAnchor || "start"}
    dominant-baseline={annotation.style?.dominantBaseline || "middle"}
    opacity={annotation.style?.opacity || 1}
    class="annotation-text"
  >
    {annotation.text}
  </text>
{/each}