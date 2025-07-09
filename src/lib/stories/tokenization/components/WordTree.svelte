<script>
  import { onMount, onDestroy } from 'svelte';
  import * as d3 from 'd3';

  export let wordArray = [];
  export let progress = 1;

  /**
   * @type {HTMLDivElement}
   */
  let container;
  let updateFn;

  // Helper to clear SVG
  function clearSVG() {
    if (container) {
      container.innerHTML = '';
    }
  }

  function createWordTree(wordArray, progress) {
    // Parse the array into a hierarchical structure
    const parseWords = (wordArray) => {
      const posGroups = {};
      wordArray.forEach(({ word, pos }) => {
        if (!posGroups[pos]) {
          posGroups[pos] = [];
        }
        posGroups[pos].push({ name: word });
      });

      return {
        name: 'Sentence',
        children: Object.keys(posGroups).map(pos => ({
          name: pos,
          children: posGroups[pos]
        }))
      };
    };

    const data = parseWords(wordArray);

    let width = 600;
    let height = 500;

    // Increase bottom margin for space below tree
    const margin = { top: 40, right: 40, bottom: 120, left: 60 };
    const containerWidth = container.clientWidth || width;
    const containerHeight = container.clientHeight || height;
    const innerWidth = containerWidth - margin.left - margin.right;
    const innerHeight = containerHeight - margin.top - margin.bottom;

    // Create an SVG container
    const svg = d3.select(container)
      .append('svg')
      .attr('width', innerWidth + margin.left + margin.right)
      .attr('height', innerHeight + margin.top + margin.bottom)
      .append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`);

    // Add the sentence text as individual SVG text elements
    const sentenceGroup = svg.append('g')
      .attr('class', 'sentence-group');

    const sentenceText = sentenceGroup.selectAll('text')
      .data(wordArray)
      .enter()
      .append('text')
      .attr('id', (d, i) => `word-${i}`)
      .attr('x', (d) => d.sentenceOrder * (innerWidth / wordArray.length))
      .attr('y', -20)
      .attr('text-anchor', 'middle')
      .style('font-size', '16px')
      .style('font-weight', 'bold')
      .text(d => d.word);

    // Create a tree layout
    const treeLayout = d3.tree().size([innerWidth, innerHeight - 40]);

    // Convert the data to a hierarchy
    const root = d3.hierarchy(data);

    // Generate the tree structure
    treeLayout(root);

    // Define a color scale for parts of speech
    const colorScale = d3.scaleOrdinal()
      .domain(data.children.map(child => child.name))
      .range(d3.schemeCategory10);

    // Add links between nodes
    const links = svg.selectAll('.link')
      .data(root.links())
      .enter()
      .append('path')
      .attr('class', 'link')
      .attr('fill', 'none')
      .attr('stroke', '#555')
      .attr('stroke-width', 1.5)
      .attr('d', d3.linkVertical()
        .x(d => d.x)
        .y(d => d.y))
      .style('opacity', 0);

    // Add nodes
    const nodes = svg.selectAll('.node')
      .data(root.descendants())
      .enter()
      .append('g')
      .attr('class', d => 'node' + (d.children ? ' node--internal' : ' node--leaf'))
      .attr('transform', d => `translate(${width / 2},${-20})`);

    nodes.append('circle')
      .attr('r', 5)
      .attr('fill', d => colorScale(d.data.name))
      .style('opacity', 0);

    nodes.append('text')
      .attr('dy', 3)
      .attr('x', (d) => 0)
      .style('text-anchor', d => d.children ? 'end' : 'start')
      .style('fill', d => d.children ? '#000' : colorScale(d.parent?.data.name))
      .text(d => d.data.name)
      .style('opacity', 0);

    // Add labels for each part of speech
    nodes.filter(d => d.children)
      .append('text')
      .attr('dy', -10)
      .attr('x', 0)
      .attr('text-anchor', 'middle')
      .style('font-size', '12px')
      .style('font-weight', 'bold')
      .text(d => d.data.name);

    // Update positions based on progress
    function update(progress) {
      const transitionDuration = 50;

      // Transition links
      links.transition()
        .duration(transitionDuration)
        .style('opacity', progress);

      // Transition nodes
      nodes.transition()
        .duration(transitionDuration)
        .attr('transform', d => `translate(${d.x},${d.y * progress})`)
        .style('opacity', progress);

      // Animate words from sentence order to grouped by POS as progress increases
      // At progress=0, use sentenceOrder; at progress=1, use grouped x positions
      // Compute target x for each word in grouped layout
      // 1. Get POS groups and their order
      const posList = data.children.map(child => child.name);
      // 2. For each POS, get words in that group
      const posWordMap = {};
      posList.forEach(pos => {
        posWordMap[pos] = wordArray.filter(w => w.pos === pos);
      });
      // 3. Compute grouped x positions for each word
      let groupOffsets = {};
      let currentX = 0;
      const gap = 5; // gap between groups
      posList.forEach(pos => {
        groupOffsets[pos] = currentX;
        currentX += posWordMap[pos].length;
        currentX += 1; // add gap
      });

      // 4. For each word, compute its grouped x position
      const groupedX = {};
      posList.forEach(pos => {
        posWordMap[pos].forEach((w, i) => {
          // Spread words in group
          const idx = groupOffsets[pos] + i;
          groupedX[w.word + '-' + w.sentenceOrder] = idx * (innerWidth / wordArray.length);
        });
      });

      // 5. Animate x from sentenceOrder to groupedX as progress goes 0->1
      sentenceText.transition()
        .duration(transitionDuration)
        .attr('x', (d, i) => {
          const key = d.word + '-' + d.sentenceOrder;
          const startX = d.sentenceOrder * (innerWidth / wordArray.length);
          const endX = groupedX[key] !== undefined ? groupedX[key] : startX;
          return startX * (1 - progress) + endX * progress;
        })
        .attr('y', (d, i) => {
          const targetNode = root.descendants().find(node => node.data.name === d.word);
          return targetNode ? targetNode.y * progress : -2;
        });
    }

    // Initial update
    update(progress);

    return update;
  }

  // Mount and update logic
  onMount(() => {
    clearSVG();
    if (wordArray && wordArray.length) {
      updateFn = createWordTree(wordArray, progress);
    }
    return () => clearSVG();
  });

  // Reactively update on prop changes
  $: if (updateFn && wordArray && wordArray.length) {
    updateFn(progress);
  }
</script>

<div bind:this={container} id="word-branch"></div>