<script>
  import { onMount } from 'svelte';
  import * as d3 from 'd3';
  
  let generationData = [];
  
  // Define the tree data structures for each generation
  const treeSteps = [
    // Gen 0
    { name: "0" },
    
    // Gen 1  
    {
      name: "0",
      children: [
        { name: "1L" },
        { name: "1R" }
      ]
    },
    
    // Gen 2
    {
      name: "0", 
      children: [
        {
          name: "1L",
          children: [
            { name: "2" }
          ]
        },
        { name: "1R" }
      ]
    },
    
    // Gen 3
    {
      name: "0",
      children: [
        {
          name: "1L", 
          children: [
            {
              name: "2",
              children: [
                { name: "3L" },
                { name: "3R" }
              ]
            }
          ]
        },
        { name: "1R" }
      ]
    },
    
    // Gen 4
    {
      name: "0",
      children: [
        {
          name: "1L",
          children: [
            {
              name: "2", 
              children: [
                {
                  name: "3L",
                  children: [
                    { name: "4" }
                  ]
                },
                { name: "3R" }
              ]
            }
          ]
        },
        { name: "1R" }
      ]
    }
  ];
  
  // Process each tree with D3 hierarchy
  function processTreeData() {
    generationData = treeSteps.map((treeData, index) => {
      const width = 120;
      const height = 100;
      
      const treeLayout = d3.tree().size([width - 40, height - 40]);
      const root = d3.hierarchy(treeData);
      treeLayout(root);
      
      // Convert D3 hierarchy to simple node/edge format
      const nodes = root.descendants().map(d => ({
        x: d.y + 20,
        y: d.x + 20,
        name: d.data.name
      }));
      
      const edges = root.links().map(d => ({
        from: root.descendants().indexOf(d.source),
        to: root.descendants().indexOf(d.target)
      }));
      
      return {
        title: `Gen ${index}`,
        nodes,
        edges,
        count: nodes.length
      };
    });
  }
  
  onMount(() => {
    processTreeData();
  });
</script>

<div class="branching-container">
  <h3>Classic Branching Process</h3>
  
  <!-- Generation cards showing cumulative trees -->
  <div class="generation-row">
    {#each generationData as gen}
      <div class="generation-card">
        <h5>{gen.title}</h5>
        <svg viewBox="0 0 120 100" class="gen-svg">
          <!-- Draw edges first -->
          {#each gen.edges as edge}
            <line 
              x1={gen.nodes[edge.from].x}
              y1={gen.nodes[edge.from].y}
              x2={gen.nodes[edge.to].x}
              y2={gen.nodes[edge.to].y}
              stroke="#666"
              stroke-width="2"
            />
          {/each}
          
          <!-- Draw nodes -->
          {#each gen.nodes as node}
            <circle 
              cx={node.x}
              cy={node.y}
              r="4"
              fill="#3498db"
              stroke="#2980b9"
              stroke-width="2"
            />
          {/each}
        </svg>
        <div class="node-count">{gen.count} nodes</div>
      </div>
    {/each}
  </div>
  
  <p class="description">Classic branching process: 1 → 2 → 1 → 2 → 1 pattern</p>
</div>

<style>
    .branching-container {
        margin: 2rem 0;
        text-align: center;
    }
    
    .branching-container h3 {
        font-family: var(--serif);
        font-size: 1.5rem;
        margin-bottom: 1rem;
        color: var(--color-primary-black);
    }
    
    .generation-row {
        display: flex;
        gap: 1rem;
        justify-content: center;
        flex-wrap: wrap;
        margin: 2rem 0;
    }
    
    .generation-card {
        border: 1px solid #ddd;
        border-radius: 8px;
        background: #fafafa;
        padding: 1rem;
        min-width: 140px;
        text-align: center;
    }
    
    .generation-card h5 {
        margin: 0 0 0.5rem 0;
        font-size: 1rem;
        color: var(--color-primary-black);
        font-family: var(--sans);
    }
    
    .gen-svg {
        width: 100%;
        height: 80px;
        margin: 0.5rem 0;
    }
    
    .node-count {
        font-size: 0.8rem;
        color: var(--color-secondary-gray);
        margin: 0.5rem 0 0 0;
    }
    
    .description {
        margin-top: 1rem;
        font-style: italic;
        color: var(--color-secondary-gray);
        font-size: 0.9rem;
        font-weight: bold;
        text-align: center;
    }
    
    @media (max-width: 768px) {
        .side-by-side {
            flex-direction: column;
            gap: 1rem;
        }
        
        .tree-svg {
            width: 100%;
            height: auto;
        }
    }
</style>