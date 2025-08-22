<script>
  import { onMount } from 'svelte';
  import * as d3 from 'd3';
  import data from '../data/embeddings-2d.json'; // Assuming this path is correct

  // Define props with default values for width and height
  const { stepCount, width = 600, height = 600 } = $props();

  // Reactive console log for stepCount changes
  $effect(() => {
    console.log('stepCount changed to:', stepCount);
  });

  // Derived reactive data for x and y coordinates based on stepCount
  // Ensure stepCount is a valid index, otherwise default to a safe value like 0
  const currentStepData = $derived.by(() => {
    const step = Math.max(0, Math.min(stepCount, data.svd_2d_results.length - 1));
    return data.svd_2d_results[step] || [];
  });

  // Derived reactive data for x and y coordinates based on stepCount
  // Ensure stepCount is a valid index, otherwise default to a safe value like 0
  const currentTextData = $derived.by(() => {
    const step = Math.max(0, Math.min(stepCount, data.utterances.length - 1));
    return data.utterances[step] || [];
  });

  const xData = $derived.by(() => currentStepData.map((point) => point[0]));
  const yData = $derived.by(() => currentStepData.map((point) => point[1]));
  const tooltipData = $derived.by(() => currentStepData.map((point) => point));

  // Set up scales for x and y axes based on data ranges
  const xscale = $derived.by(() => {
    // Handle cases where xData might be empty to prevent Math.min/max errors
    const minX = xData.length > 0 ? Math.min(...xData) : 0;
    const maxX = xData.length > 0 ? Math.max(...xData) : 1;
    return d3.scaleLinear()
      .domain([minX, maxX])
      .range([15, width - 25]);
  });

  const yscale = $derived.by(() => {
    // Handle cases where yData might be empty to prevent Math.min/max errors
    const minY = yData.length > 0 ? Math.min(...yData) : 0;
    const maxY = yData.length > 0 ? Math.max(...yData) : 1;
    return d3.scaleLinear()
      .domain([minY, maxY])
      .range([height - 25, 15]); // Invert y-axis for typical SVG coordinate system
  });

  let svgElement; // Bind this to the SVG element
  let tooltipElement; // Bind this to the tooltip element

  // Effect to update the scatter plot whenever xData or yData changes
  $effect(() => {
    if (!svgElement || !tooltipElement) return;

    const svg = d3.select(svgElement);
    const tooltip = d3.select(tooltipElement);

    // Join new data with existing circles, update positions with transition
    svg.selectAll("circle")
      .data(xData) // Bind to xData, assuming it drives the number of points
      .join(
        enter => enter.append("circle")
          .attr("cx", (d) => xscale(d))
          .attr("cy", (d, i) => yscale(yData[i]))
          .attr("r", 0) // Start with radius 0 for enter animation
          .attr('opacity', 0.9)
          .style("fill", "steelblue")
          .on("mouseover", function(event, d) {
            const i = svg.selectAll("circle").nodes().indexOf(this);

            tooltip.style("opacity", 1)
                   .html(data.utterances[i]);
            // Position tooltip relative to the circle
            tooltip.style("left", (xscale(d) - 320) + "px") // Adjust for padding/offset
                   .style("top", (yscale(yData[i]) + 20) + "px"); // Adjust for padding/offset
          })
          .on("mousemove", function(event, d) {
            // Optional: make tooltip follow mouse more precisely
            tooltip.style("left", (event.clientX + 10) + "px")
                   .style("top", (event.clientY + 10) + "px");
          })
          .on("mouseout", function() {
            tooltip.style("opacity", 0);
          })
          .transition()
          .duration(750) // Animation duration
          .attr("r", 5), // Animate to radius 5
        update => update
          .transition()
          .duration(750) // Animation duration
          .attr("cx", (d) => xscale(d))
          .attr("cy", (d, i) => yscale(yData[i]))
          .attr("r", 5)
          .on("mouseover", function(event, d) {
            const i = svg.selectAll("circle").nodes().indexOf(this);
            tooltip.style("opacity", 1)
                   .html(`X: ${d.toFixed(2)}, Y: ${yData[i].toFixed(2)}`);
            tooltip.style("left", (xscale(d) + 20) + "px")
                   .style("top", (yscale(yData[i]) + 20) + "px");
          })
          .on("mousemove", function(event, d) {
            tooltip.style("left", (event.clientX + 10) + "px")
                   .style("top", (event.clientY + 10) + "px");
          })
          .on("mouseout", function() {
            tooltip.style("opacity", 0);
          }),
        exit => exit
          .transition()
          .duration(750) // Animation duration
          .attr("r", 0) // Animate to radius 0 for exit
          .remove()
      );
  });

  // Initial plot creation on mount
  onMount(() => {
    // The $effect above will handle initial rendering and subsequent updates.
    // No specific D3 calls needed here as the $effect already runs.
  });

</script>

<div class="viz-content">
  <div id="plot-container">
    <svg width={width} height={height} bind:this={svgElement}></svg>
  </div>
  <!-- Tooltip element -->
  <div id="tooltip" bind:this={tooltipElement}></div>
</div>

<style>
  .viz-content {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 100vh;
    position: relative; /* Needed for absolute positioning of tooltip */
  }
  #plot-container {
    border: 1px solid #ccc;
    
rgb(137, 137, 137)    padding: 10px;
  }
  svg {
    display: block;
    margin: auto;
  }
  #tooltip {
    position: absolute;
    background-color: rgba(0, 0, 0, 0.7);
    color: white;
    padding: 8px 12px;
    border-radius: 5px;
    pointer-events: none; /* Allows mouse events to pass through to the circles */
    opacity: 0;
    transition: opacity 0.2s ease-in-out;
    font-family: sans-serif;
    font-size: 14px;
    z-index: 1000;
  }
</style>