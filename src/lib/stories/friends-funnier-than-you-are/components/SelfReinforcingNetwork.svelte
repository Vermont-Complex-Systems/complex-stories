<script>
  import * as d3 from 'd3';
  import { Plot, Dot, Line } from 'svelteplot';

  let width = $state(400);
  const height = 350;
  const treeDepth = 6;
  let tauValue = $state(1.5); // Power law parameter

  let allBranches = $state([]);
  let cascadeSizes = $state([]); // Track all cascade sizes
  let uniqueId = 0;

  // Power law distribution function
  function powerLawSample(tau = 2.5, xMin = 1, xMax = 5000) {
    const u = Math.random();
    const exponent = 1 - tau;
    
    if (Math.abs(exponent) < 1e-10) {
      return xMin * Math.exp(u * Math.log(xMax / xMin));
    } else {
      const numerator = Math.pow(xMax, exponent) - Math.pow(xMin, exponent);
      const base = Math.pow(xMin, exponent) + u * numerator;
      return Math.pow(base, 1 / exponent);
    }
  }

  // Generate cascade with specified size using power law distribution
  function makeBranchingCascade(root, maxDepth = 6) {
    // First, determine target cascade size from power law
    const targetSize = Math.max(1, Math.round(powerLawSample(tauValue, 1, 1000)));
    let nodesCreated = 0;
    const nodesToProcess = [root];
    
    root.cascadeNode = true;
    nodesCreated++;
    
    // Build cascade by breadth-first expansion until we reach target size
    while (nodesToProcess.length > 0 && nodesCreated < targetSize) {
      const currentNode = nodesToProcess.shift();
      
      // Stop if we've reached max depth
      if (currentNode.depth >= maxDepth) continue;
      
      // Determine how many children this node should have
      const remainingNodes = targetSize - nodesCreated;
      const remainingCapacity = Math.min(remainingNodes, 4); // Max 4 children per node
      
      if (remainingCapacity <= 0) break;
      
      // Distribute remaining nodes among potential children
      const numChildren = Math.min(
        remainingCapacity,
        1 + Math.floor(Math.random() * Math.min(3, remainingCapacity))
      );
      
      currentNode.branches = [];
      
      for (let i = 0; i < numChildren && nodesCreated < targetSize; i++) {
        const angle = -Math.PI/2 + (Math.random() - 0.5) * Math.PI/3;
        const length = 40 + Math.random() * 30;
        
        const child = {
          a: currentNode.b,
          b: {
            x: currentNode.b.x + Math.cos(angle) * length,
            y: currentNode.b.y + Math.sin(angle) * length
          },
          linearDepth: (maxDepth - (currentNode.depth || 0)) / maxDepth,
          thickness: Math.max(3 - (currentNode.depth || 0), 0.5),
          color: 'var(--edge-color, #333)',
          opacity: 1.0,
          depth: (currentNode.depth || 0) + 1,
          cascadeNode: true,
          branches: []
        };
        
        currentNode.branches.push(child);
        nodesToProcess.push(child);
        nodesCreated++;
      }
    }
    
    return nodesCreated;
  }

  function makeTree() {
    // Simple base structure
    const root = {
      a: { x: width * 0.3, y: height - 10 },
      b: { x: width * 0.3, y: height - 50},
      linearDepth: 1.0,
      thickness: 3,
      color: 'var(--edge-color, #333)',
      opacity: 0.3,
      depth: 0,
      branches: []
    };
    
    // Generate cascade and track size
    const cascadeSize = makeBranchingCascade(root);
    cascadeSizes.push(cascadeSize);
    
    return root;
  }

  // Rest of the functions stay the same...
  function drawTree(tree) {
    const branches = [];
    const nodes = new Map();
    
    if (!tree) return branches;
    
    const traverse = t => {
      const nodeAKey = `${t.a.x.toFixed(1)},${t.a.y.toFixed(1)}`;
      const nodeBKey = `${t.b.x.toFixed(1)},${t.b.y.toFixed(1)}`;
      
      nodes.set(nodeAKey, { x: t.a.x, y: t.a.y, opacity: t.opacity, color: t.color });
      nodes.set(nodeBKey, { x: t.b.x, y: t.b.y, opacity: t.opacity, color: t.color });

      branches.push({
        id: uniqueId++,
        nodeA: { x: t.a.x, y: t.a.y },
        nodeB: { x: t.b.x, y: t.b.y },
        thickness: 2,
        color: t.color,
        opacity: t.opacity
      });

      if (t.branches) {
        t.branches.forEach(traverse);
      }
    };
    
    traverse(tree);
    
    const uniqueNodes = Array.from(nodes.values()).map(node => ({
      id: uniqueId++,
      ...node,
      isNode: true
    }));
    
    return [...branches, ...uniqueNodes];
  }

  function generateTree() {
    uniqueId = 0;
    const tree = makeTree();
    allBranches = drawTree(tree);
  }
  
  async function generateBulk(count) {
    for (let i = 0; i < count; i++) {
      const tree = makeTree(); // Make the tree to track cascade sizes
      // Update visualization with each tree
      uniqueId = 0;
      allBranches = drawTree(tree);
      
      // Small delay to see the network flash by
      await new Promise(resolve => setTimeout(resolve, 50)); // 50ms delay
    }
  }
  
  // Calculate size distribution for log-log plot
  let sizeDistribution = $derived(() => {
    if (cascadeSizes.length < 3) return [];
    
    const sizeCounts = {};
    cascadeSizes.forEach(size => {
      sizeCounts[size] = (sizeCounts[size] || 0) + 1;
    });
    
    return Object.entries(sizeCounts)
      .map(([size, count]) => ({
        size: parseInt(size),
        frequency: count / cascadeSizes.length
      }))
      .filter(d => d.size > 0) // Remove size 0 for log scale
      .sort((a, b) => a.size - b.size);
  });

  function formatTicks(d) {
        const exp = Math.round(Math.log10(d));
        return `10^${exp}`;
    }
    
  // Clear data when tau changes
  $effect(() => {
    tauValue; // Track tauValue changes
    cascadeSizes = [];
  });

  // Generate initial tree
  generateTree();
</script>

<div class="container">
  <div class="main-layout">
    <div class="network-section">
      <svg {width} {height} class="src-network">
        <g opacity="0.3">
          {#each allBranches.filter(b => !b.isNode && b.opacity !== 1.0) as branch (branch.id)}
            <line x1={branch.nodeA.x} y1={branch.nodeA.y} x2={branch.nodeB.x} y2={branch.nodeB.y} 
                  stroke={branch.color} stroke-width={branch.thickness} />
          {/each}
        </g>

        <g opacity="1.0">
          {#each allBranches.filter(b => !b.isNode && b.opacity === 1.0) as branch (branch.id)}
            <line x1={branch.nodeA.x} y1={branch.nodeA.y} x2={branch.nodeB.x} y2={branch.nodeB.y} 
                  stroke={branch.color} stroke-width={branch.thickness} />
          {/each}
        </g>

        <g opacity="0.3">
          {#each allBranches.filter(b => b.isNode && b.opacity !== 1.0) as node (node.id)}
            <circle cx={node.x} cy={node.y} r="3" fill={node.color} stroke="grey"/>
          {/each}
        </g>

        <g opacity="1.0">
          {#each allBranches.filter(b => b.isNode && b.opacity === 1.0) as node (node.id)}
            <circle cx={node.x} cy={node.y} r="4" fill={node.color} stroke="grey" />
          {/each}
        </g>
      </svg>
      
    </div>
    
    <div class="right-section">
      <div class="plot-area">
        <p>Cascade Size Distribution (τ = {tauValue.toFixed(1)})</p>
        <Plot 
          x={{
            type: 'log',
            label: "Cascade size s →"
          }} 
          y={{
            type: 'log',
            tickFormat: formatTicks,
            label: "↑ Frequency"
          }} 
          grid 
          frame
          width={340}
          height={280}
          marginLeft={33}
          marginRight={10}
          marginBottom={30}
        >
          <Dot
            data={sizeDistribution()}
            x="size"
            y="frequency" 
            fill="#7a8c6a"
            r={3}
          />
          
        </Plot>
      </div>
      
      <div class="button-ctn">
        <div class="controls">
          <input 
          type="range" 
          bind:value={tauValue} 
          min="1.0" 
          max="4.0" 
          step="0.1"
          class="tau-slider"
          />
          <label for="id">τ = {tauValue.toFixed(1)}</label>
        </div>
        
        <button onclick={generateTree} class="regenerate-btn">
          Generate New
        </button>
        
        <button onclick={() => generateBulk(100)} class="bulk-btn">
          Generate 100
        </button>
      </div>
    </div>
  </div>
  <small>Notes: cascade sizes are sampled from power law distribution, then visualized as tree networks (max depth: 6, cutoff: 1,000)</small>
</div>

<style>
  .container {
    width: 100%;
    max-width: 700px;
    margin: 0;
    padding: 0;
    --edge-color: #333;
  }
  
  :global(.dark) .container {
    --edge-color: whitesmoke;
  }
  
  .main-layout {
    display: flex;
    gap: 5px;
    align-items: flex-start;
  }
  
  .network-section {
    flex: 0.8;
    position: relative;
    margin: 50px 0 0 0;
    padding: 0;
  }
  
  .right-section {
    flex: 1.2;
    display: flex;
    flex-direction: column;
    gap: 0;
    margin-top: 30px; /* Align with seed node area */
  }


  
  @media (max-width: 768px) {
    .main-layout {
      flex-direction: column;
      position: relative;
    }
    
    .network-section {
      position: absolute;
      top: 60px;
      right: 10px;
      width: 110px;
      height: 170px;
      z-index: 10;
      margin: 0;
      background: #f8f5e6;
      border: 1px solid #ddd;
      border-radius: 4px;
      padding: 4px;
      overflow: hidden;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1)
    }
    
    .network-section svg {
      width: 400px !important;
      height: 350px !important;
      transform: scale(0.32) translate(-60%, -60%);
      transform-origin: center center;
    }
    
    .right-section {
      flex: none;
      width: 100%;
      margin-top: 0;
    }
    
    .plot-area {
      margin-top: 0;
    }
  }
  
  .plot-area {
    text-align: left;
  }
   
  .controls {
    display: flex;
    flex-direction: column;
    align-items: center;
    margin: 0;
    padding: 0;
    background: none;
    border-radius: 0;
  }

  
  .controls label {
    font-size: 12px;
    color: #666;
    margin: 0 0 3px 0;
    font-weight: normal;
  }

  .tau-slider {
    width: 120px;
    margin: 0;
    -webkit-appearance: none;
    appearance: none;
    height: 6px;
    border-radius: 3px;
    background: #ddd;
    outline: none;
  }

  .tau-slider::-webkit-slider-thumb {
    -webkit-appearance: none;
    appearance: none;
    width: 16px;
    height: 16px;
    border-radius: 50%;
    background: #7a8c6a;
    cursor: pointer;
  }

  .tau-slider::-moz-range-thumb {
    width: 16px;
    height: 16px;
    border-radius: 50%;
    background: #7a8c6a;
    cursor: pointer;
    border: none;
  }

  .tau-slider::-moz-range-progress {
    background: #7a8c6a;
    height: 6px;
    border-radius: 3px;
  }

  .tau-slider::-webkit-slider-runnable-track {
    background: #ddd;
    height: 6px;
    border-radius: 3px;
  }

  .src-network {
    overflow: visible;
  }

 .button-ctn {
    display: flex;
    justify-content: center;
    align-items: flex-end;
    gap: 10px;
    margin-top: 10px;
  }

  .regenerate-btn, .bulk-btn {
    cursor: pointer;
    padding: 8px 16px;
    margin: 0 0 0 10px;
    background: #7a8c6a;
    color: white;
    border: none;
    border-radius: 4px;
    font-size: 14px;
  }

  .regenerate-btn:hover, .bulk-btn:hover {
    background: #6a7c5a;
  }

  .bulk-btn {
    margin: 0 0 0 10px;
    padding: 8px 16px;
    font-size: 14px;
  }
</style>