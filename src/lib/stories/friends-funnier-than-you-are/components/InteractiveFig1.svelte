<script>
  import * as d3 from 'd3';

  let width = $state(500);
  const height = 425;
  const treeDepth = 6;

  let allBranches = $state([]);
  let generationCircles = $state([]);
  let uniqueId = 0;

  function makeTree(a, orientation, scaleRatio, maxDepth = 5) {
    const p = 0.6;
    let generationIntensities = {}; // Track max intensity per generation
    
    const traverse = (a, orientation, scaleRatio, currentDepth = 0, intensity = 1, isAbsorbed = false, wasReceptive = true) => {
  if (currentDepth > maxDepth) return null;
  
  // Track max intensity for this generation
  if (!generationIntensities[currentDepth] || intensity > generationIntensities[currentDepth]) {
    generationIntensities[currentDepth] = intensity;
  }
  
  const scale = scaleRatio * 100;
  const length = 34;
  const angle = orientation + d3.randomNormal(0, 0.3)();
  
  const b = {
    x: Math.cos(angle) * length + a.x,
    y: Math.sin(angle) * length + a.y
  };

  const tree = {
  a, b,
  color: isAbsorbed ? '#ccc' : (wasReceptive ? '#f97316' : '#3b82f6'), // Changed parentWasReceptive to wasReceptive
  opacity: isAbsorbed ? 0.3 : 1.0,
  depth: currentDepth,
  intensity: intensity,
  isAbsorbed: isAbsorbed,
  wasReceptive: wasReceptive // Changed parentWasReceptive to wasReceptive
};

  // const numBranches = Math.min(Math.max(d3.randomPoisson(1.5)(), 1), 3);
  const numBranches = 1;


  if (numBranches > 0 && currentDepth < maxDepth && !isAbsorbed) {
    tree.branches = [];
    
    for (let i = 0; i < numBranches; i++) {
      // Each child is independently receptive or not
      const childIsReceptive = Math.random() < p;
      
      // Child's intensity is based on THIS node's intensity and child's receptivity
      const childIntensity = childIsReceptive ? intensity + 1 : intensity - 1;
      
      const childAngle = angle + (i - (numBranches - 1) / 2) * (Math.PI / 6);
      
      if (childIntensity <= 0) {
  // Create absorbed child
  const absorbingNode = {
    a: b,
    b: {
      x: Math.cos(childAngle) * length * 0.5 + b.x,
      y: Math.sin(childAngle) * length * 0.5 + b.y
    },
    color: '#999',
    opacity: 0.5,
    depth: currentDepth + 1,
    intensity: 0,
    isAbsorbed: true,
    wasReceptive: false,
    branches: []
  };
  tree.branches.push(absorbingNode);
} else {
  // Create normal child with calculated intensity
  const branch = traverse(b, childAngle, 0.8, currentDepth + 1, childIntensity, false, childIsReceptive);
  if (branch) tree.branches.push(branch);
}
    }
  }

  return tree;
};

    const tree = traverse(a, 0, scaleRatio, 0, 1, false, true);
    
    // Create generation circles based on max intensities
    const circles = [];
    const centerX = a.x;
    const centerY = a.y;
    const baseRadius = 40; // Base radius for generation 0
    
    for (let gen = 0; gen <= maxDepth; gen++) {
      if (generationIntensities[gen]) {
        const radius = baseRadius + (gen * 30); // 30px per generation
        const maxIntensity = generationIntensities[gen];
        
        circles.push({
          x: centerX,
          y: centerY,
          radius: radius,
          generation: gen,
          maxIntensity: maxIntensity,
          color: getIntensityColor(maxIntensity)
        });
      }
    }
    
    generationCircles = circles;
    
    // Find and highlight the cascade path (highest intensity path)
    function findCascadePath(node) {
      if (!node.branches || node.branches.length === 0) return [node];
      
      // Find the branch with highest intensity
      const maxIntensityBranch = node.branches.reduce((max, branch) => 
        branch.intensity > max.intensity ? branch : max
      );
      
      // Only highlight if intensity is building up (>= 3)
      if (maxIntensityBranch.intensity >= 3) {
        const cascadePath = [node, ...findCascadePath(maxIntensityBranch)];
        return cascadePath;
      }
      
      return [node];
    }
    
    const cascadePath = findCascadePath(tree);
    
    // Mark cascade nodes
    function markCascade(node) {
      if (cascadePath.includes(node)) {
        node.isCascade = true;
        node.opacity = 1.0;
      }
      
      if (node.branches) {
        node.branches.forEach(markCascade);
      }
    }
    
    markCascade(tree);
    
    return tree;
  }

  function getIntensityColor(intensity) {
    // Color scale based on intensity
    const colors = ['#64748b', '#3b82f6', '#10b981', '#f59e0b', '#ef4444', 'midnightblue', "green", "purple"];
    const index = Math.min(intensity - 1, colors.length - 1);
    return colors[Math.max(index, 0)];
  }

  function drawTree(tree) {
    const branches = [];
    const nodes = new Map();
    
    if (!tree) return branches;
    
    const traverse = t => {
      const nodeAKey = `${t.a.x.toFixed(1)},${t.a.y.toFixed(1)}`;
      const nodeBKey = `${t.b.x.toFixed(1)},${t.b.y.toFixed(1)}`;
      
      nodes.set(nodeAKey, { 
        x: t.a.x, y: t.a.y, 
        color: t.color,
        opacity: t.opacity,
        isAbsorbed: t.isAbsorbed,
        isCascade: t.isCascade,
        intensity: t.intensity // Add this
      });
      nodes.set(nodeBKey, { 
        x: t.b.x, y: t.b.y, 
        color: t.color,
        opacity: t.opacity,
        isAbsorbed: t.isAbsorbed,
        isCascade: t.isCascade,
        intensity: t.intensity // Add this
      });

      branches.push({
        id: uniqueId++,
        nodeA: { x: t.a.x, y: t.a.y },
        nodeB: { x: t.b.x, y: t.b.y },
        thickness: t.isAbsorbed ? 1 : 2,
        color: t.color,
        opacity: t.opacity,
        isAbsorbed: t.isAbsorbed,
        isCascade: t.isCascade
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
    
    const tree = makeTree(
      { x: width / 2, y: height / 2 },
      0,
      1.0,
      treeDepth
    );
    allBranches = drawTree(tree);
  }

  $effect(() => {
    generateTree();
  });
</script>

<div class="chart-container" bind:clientWidth={width}>
  <svg {width} {height} class="src-network">
    <!-- Generation circles (background) -->
    <g opacity="0.3">
      {#each generationCircles as circle (circle.generation)}
        <circle 
          cx={circle.x} 
          cy={circle.y} 
          r={circle.radius} 
          fill="none" 
          stroke={circle.color} 
          stroke-width="2"
          stroke-dasharray="5,3"
        />
        <!-- Generation label -->
        <text 
          x={circle.x} 
          y={circle.y - circle.radius - 8} 
          text-anchor="middle" 
          font-size="12" 
          font-weight="bold"
          fill={circle.color}
        >
          n={circle.generation}: I_max = {circle.maxIntensity}
        </text>
      {/each}
    </g>

    <!-- Normal branches -->
    <g opacity="0.5">
      {#each allBranches.filter(b => !b.isNode  && !b.isAbsorbed) as branch (branch.id)}
        <line x1={branch.nodeA.x} y1={branch.nodeA.y} x2={branch.nodeB.x} y2={branch.nodeB.y} 
              stroke={branch.color} stroke-width="1" />
      {/each}
      
      {#each allBranches.filter(b => b.isNode && !b.isAbsorbed) as node (node.id)}
        <circle cx={node.x} cy={node.y} r="6" fill={node.color} stroke="white"/>
        <text x={node.x} y={node.y} stroke="black" dx={-3} dy={3} font-size="10">{node.intensity}</text>
      {/each}
    </g>

    <!-- Cascade path (highlighted)
    <g opacity="1.0">
      {#each allBranches.filter(b => !b.isNode && b.isCascade) as branch (branch.id)}
        <line x1={branch.nodeA.x} y1={branch.nodeA.y} x2={branch.nodeB.x} y2={branch.nodeB.y} 
              stroke={"yellow"} stroke-width="1"/>
      {/each}
      
      {#each allBranches.filter(b => b.isNode && b.isCascade) as node (node.id)}
        <circle cx={node.x} cy={node.y} r="4" fill={node.color} stroke="white" stroke-width="1" />
      {/each}
    </g> -->

    <!-- Absorbed branches -->
    <g opacity="0.5">
      {#each allBranches.filter(b => !b.isNode && b.isAbsorbed) as branch (branch.id)}
        <line x1={branch.nodeA.x} y1={branch.nodeA.y} x2={branch.nodeB.x} y2={branch.nodeB.y} 
              stroke={branch.color} stroke-width="1" />
      {/each}
      
      {#each allBranches.filter(b => b.isNode && b.isAbsorbed) as node (node.id)}
        <circle cx={node.x} cy={node.y} r="4" fill={node.color} />
      {/each}
    </g>
  </svg>
  
  <div class="button-ctn">
    <button onclick={generateTree} class="regenerate-btn">
      Generate New Network
    </button>
  </div>
</div>

<style>
  .chart-container {
    width: 100%;
    max-width: 800px;
    position: relative;
  }
  
  .src-network {
    overflow: visible;
  }

  .chart-container .button-ctn {
    position: absolute;
    bottom: 10px;
    right: 10px;
    max-width: fit-content;
    margin: 0;
  }

  .regenerate-btn {
    cursor: pointer;
    padding: 8px 16px;
    margin: 0;
    background: #4a5c3a;
    color: white;
    border: none;
    border-radius: 4px;
    font-size: 14px;
  }
  
  .regenerate-btn:hover {
    background: #3a4c2a;
  }
</style>