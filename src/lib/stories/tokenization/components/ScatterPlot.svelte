<script>
  // Helper to get N unique random indices from an array
  function getRandomIndices(arrLength, n) {
    const indices = [];
    while (indices.length < n && indices.length < arrLength) {
      const idx = Math.floor(Math.random() * arrLength);
      if (!indices.includes(idx)) indices.push(idx);
    }
    return indices;
  }

  import { onMount } from 'svelte';
  import * as d3 from 'd3';
  import data from '../data/embeddings-2d.json'; // Assuming this path is correct

  // Define props with default values for width and height
  import { writable } from 'svelte/store';

  const { stepCount, height = 600 } = $props();

  // Responsive width: 100% of window, max 1000px
  const widthStore = writable(Math.min(window.innerWidth, 1000));
  let width = Math.min(window.innerWidth, 1000);

  function updateWidth() {
    width = Math.min(window.innerWidth, 1000);
    widthStore.set(width);
  }

  onMount(() => {
    window.addEventListener('resize', updateWidth);
    updateWidth();
    return () => window.removeEventListener('resize', updateWidth);
  });

  // Reactive console log for stepCount changes
  $effect(() => {
    console.log('stepCount changed to:', stepCount);
  });

  // Derived reactive data for x and y coordinates based on stepCount
  // Ensure stepCount is a valid index, otherwise default to a safe value like 0
  const currentStepData = $derived.by(() => {
    let step = Math.max(0, Math.min(stepCount, data.svd_2d_results.length - 1));
    step = step + 5;
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
  let textGroup; // For text labels
  let tooltipElement; // Bind this to the tooltip element

  // Effect to update the scatter plot whenever xData or yData changes
  $effect(() => {
    if (!svgElement || !tooltipElement) return;

    const svg = d3.select(svgElement);
    const tooltip = d3.select(tooltipElement);

    // Remove previous text labels
    svg.selectAll('.viz-content').remove();

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
            tooltip.style("left", (event.pageX + 10) + "px")
                   .style("top", (event.pageY + 10) + "px");

            console.log(event)
          })
          .on("mousemove", function(event, d) {
            // Optional: make tooltip follow mouse more precisely
            tooltip.style("left", (event.offsetX - 10) + "px")
                   .style("top", (event.offsetY + 30) + "px");
          })
          .on("mouseout", function() {
            tooltip.style("opacity", 0);
          })
          .transition()
          .duration(1500) // Animation duration
          .attr("r", 4), // Animate to radius 5
        update => update
          .transition()
          .on("end", function(_, i) {
        // Only run once after all transitions
        if (i === xData.length - 1) {
          // Select 3 unique random indices
          const indices = getRandomIndices(xData.length, 3);

          // Remove all previous random labels and lines before adding new ones
          d3.selectAll('.random-label-html').remove();
          d3.selectAll('.random-label-line').remove();

          // Add text labels for those indices
          indices.forEach(idx => {
            // Calculate label position with edge padding
            const labelPadding = 12;
            let x = xscale(xData[idx]);
            let y = yscale(yData[idx]) - labelPadding;

            // Ensure label stays within left/right bounds
            x = Math.max(labelPadding, Math.min(x, width - labelPadding));
            // Ensure label stays within top/bottom bounds
            y = Math.max(labelPadding, Math.min(y, height - labelPadding));

            // Calculate SVG coordinates for the point
            const svgRect = svgElement.getBoundingClientRect();
            const containerRect = document.querySelector('.viz-content').getBoundingClientRect();

            // Convert SVG coordinates to container-relative coordinates
            const labelX = svgRect.left - containerRect.left + xscale(xData[idx]);
            const labelY = svgRect.top - containerRect.top + yscale(yData[idx]);

            // Position label above the point
            const labelOffsetY = 32; // pixels above the point

            // Draw the label as an absolutely positioned div
            d3.select(".viz-content")
              .append("div")
              .attr("class", `random-label-html random-label-html-${idx}`)
              .style("position", "absolute")
              .style("left", `${labelX}px`)
              .style("top", `${labelY - labelOffsetY}px`)
              .style("transform", "translate(-50%, -100%)")
              .style("font-size", "1rem")
              .style("font-weight", "bold")
              .style("color", "#333")
              .style("background", "#fff")
              .style("padding", "2px 8px")
              .style("border-radius", "5px")
              .style("box-shadow", "0 2px 8px rgba(0,0,0,0.1)")
              .style("pointer-events", "none")
              .text(data.utterances[idx]);

            // Draw a line from the label to the point using SVG
            d3.select(svgElement)
              .append("line")
              .attr("class", `random-label-line random-label-line-${idx}`)
              .attr("x1", xscale(xData[idx]))
              .attr("y1", yscale(yData[idx]) - labelOffsetY + 8) // 8px fudge for label height
              .attr("x2", xscale(xData[idx]))
              .attr("y2", yscale(yData[idx]))
              .attr("stroke", "#333")
              .attr("stroke-width", 1.5)
              .attr("opacity", 0.7);
          });
        }
      })
          .duration(750) // Animation duration
          .attr("cx", (d) => xscale(d))
          .attr("cy", (d, i) => yscale(yData[i]))
          .attr("r", 4)
            .on("mouseover", function(event, d) {
            const i = svg.selectAll("circle").nodes().indexOf(this);
            tooltip.style("opacity", 1)
                 .html(`X: ${d.toFixed(2)}, Y: ${yData[i].toFixed(2)}`);
            // Center tooltip vertically over mouse
            const tooltipRect = tooltip.node().getBoundingClientRect();
            tooltip.style("left", (event.clientX + 10) + "px")
                 .style("top", (event.clientY - tooltipRect.height / 2) + "px");
            })
            .on("mousemove", function(event, d) {
            const tooltipRect = tooltip.node().getBoundingClientRect();
            tooltip.style("left", (event.clientX + 10) + "px")
                 .style("top", (event.clientY - tooltipRect.height / 2) + "px");
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