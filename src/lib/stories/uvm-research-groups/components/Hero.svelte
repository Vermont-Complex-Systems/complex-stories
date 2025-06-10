<!-- SimpleHero.svelte -->
<script>
  let { coauthorData, paperData } = $props();

  let svgElement;
  let svgWidth = $state(800);
  let svgHeight = $state(600);

  // Data filtering
  console.log(coauthorData)
  let coauthors = $derived(coauthorData?.filter(c => c.uvm_faculty_2023 === "True"));
  let hasData = $derived(coauthors.length > 0 && paperData.length > 0);

  // Force simulation nodes
  let nodes = $state([]);
  let simulation;

  // Get actual SVG dimensions
  function updateDimensions() {
    if (svgElement) {
      const rect = svgElement.getBoundingClientRect();
      svgWidth = rect.width;
      svgHeight = rect.height;
    }
  }

  function createSimulation() {
    if (!hasData || !svgWidth || !svgHeight) return;

    // Import d3 dynamically
    import('d3-force').then((d3) => {
      const dividerX = svgWidth / 2;
      
      // Create nodes for collaborators (left side - swarm toward divider)
      const coauthorNodes = coauthors.map((d, i) => ({
        id: `coauthor-${i}`,
        type: 'coauthor',
        name: d.coauth_name,
        r:  Math.sqrt(d.all_times_collabo || 1) * 5,
        x: Math.random() * (dividerX - 50) + 25,
        y: 120 + Math.random() * (svgHeight - 200)
      }));

      // Create nodes for paperData (right side - swarm toward divider)
      const paperNodes = paperData.map((d, i) => ({
        id: `paper-${i}`,
        type: 'paper',
        title: d.title,
        r: Math.log(d.cited_by_count + 1 || 1) * 2,
        x: dividerX + 25 + Math.random() * (dividerX - 50),
        y: 120 + Math.random() * (svgHeight - 200)
      }));

      nodes = [...coauthorNodes, ...paperNodes];

      // Create force simulation - bee swarm toward divider from both sides
      simulation = d3.forceSimulation(nodes)
        .force('collision', d3.forceCollide().radius(d => d.r + 1))
        .force('x', d3.forceX().x(d => dividerX).strength(0.03)) // Both sides pull toward divider
        .force('y', d3.forceY(svgHeight / 2).strength(0.05)) // Gentle centering vertically
        // .alphaDecay(0.05) // Much faster decay
        // .velocityDecay(0.5) // Very high friction
        .force('boundary', () => {
          // Keep nodes on their respective sides
          nodes.forEach(d => {
            if (d.type === 'coauthor') {
              // Left side boundary
              d.x = Math.max(d.r, Math.min(dividerX - d.r, d.x));
            } else {
              // Right side boundary
              d.x = Math.max(dividerX + d.r, Math.min(svgWidth - d.r, d.x));
            }
            d.y = Math.max(d.r + 100, Math.min(svgHeight - d.r - 50, d.y));
          });
        })
        .on('tick', () => {
          nodes = [...nodes]; // Trigger reactivity
        });
    });
  }

  // Run simulation when data is ready
  $effect(() => {
    if (hasData && svgWidth && svgHeight) {
      createSimulation();
    }
    
    return () => {
      if (simulation) {
        simulation.stop();
      }
    };
  });

  // Update dimensions when mounted and on resize
  $effect(() => {
    updateDimensions();
    
    const resizeObserver = new ResizeObserver(() => {
      updateDimensions();
    });
    
    if (svgElement) {
      resizeObserver.observe(svgElement);
    }
    
    return () => {
      resizeObserver.disconnect();
    };
  });
</script>

<div class="hero">
  {#if !hasData}
    <div class="loading">Loading...</div>
  {:else}
    <svg bind:this={svgElement} width="100%" height="100%">
        <!-- Title -->
      <text x={svgWidth/2} y="40" text-anchor="middle" class="title">
        How does research and collaboration co-evolve over time?
      </text>
      <!-- Left section: Collaborators -->
      <text x={svgWidth*0.13} y={svgHeight/2} text-anchor="middle" class="section">
        Coauthors
      </text>
      
      <!-- Right section: paperData -->
      <text x={svgWidth*0.9} y={svgHeight/2} text-anchor="middle" class="section">
        Papers
      </text>
      
      <!-- Force-simulated nodes -->
      {#each nodes as node (node.id)}
        <circle
          cx={node.x}
          cy={node.y}
          r={node.r}
          fill={node.type === 'coauthor' ? '#333' : '#666'}
          stroke="#fff"
          stroke-width="1"
          class="node"
        >
          <title>{node.type === 'coauthor' ? node.name : node.title}</title>
        </circle>
      {/each}
      
      <!-- Scroll hint -->
      <text x={svgWidth/2} y={svgHeight-20} text-anchor="middle" class="hint">
        ↓ Scroll to explore a faculty's timeline ↓
      </text>
    </svg>
  {/if}
</div>

<style>
  .hero {
    width: 100%;
    height: 100vh;
  }

  svg {
    display: block;
    width: 100%;
    height: 100%;
  }

  .loading {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100vh;
    font-size: 1.5rem;
    color: #666;
  }

  .title {
    font-size: 24px;
    font-weight: bold;
    fill: #333;
  }

  .section {
    font-size: 18px;
    font-weight: 600;
    fill: #555;
  }

  .hint {
    font-size: 16px;
    fill: #777;
    animation: bounce 2s infinite;
  }

  .node {
    cursor: pointer;
    transition: opacity 0.2s;
  }

  .node:hover {
    opacity: 0.7;
  }

  @keyframes bounce {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-5px); }
  }
</style>