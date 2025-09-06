<script>
  import * as d3 from 'd3';

  let width = $state(500);
  const height = 375;
  const treeDepth = 6;

  let allBranches = $state([]);
  let uniqueId = 0;

  function makeTree(a, orientation, scaleRatio, maxDepth = 5) {
    const FULL_LENGTH = 200;
    const MIN_Y = 100;
    
    const traverse = (a, orientation, scaleRatio, currentDepth = 0) => {
      if (a.y < MIN_Y) return null;
      
      const scale = scaleRatio * FULL_LENGTH;
      const linearDepth = (maxDepth - currentDepth) / maxDepth;
      const thickness = scaleRatio * linearDepth * 20;
      
      const numBranches = Math.max(d3.randomNormal(2.0, 0.8)(), 2);
      
      const length = Math.max(d3.randomNormal(scale * 0.6, scale * 0.1)() + 20, 20);
      let angle = d3.randomNormal(orientation, 0.25)();
      
      const b = {
        x: Math.cos(angle) * length + a.x,
        y: Math.sin(angle) * length + a.y
      };

      const tree = {
        a, b, linearDepth, thickness,
        color: '#333',
        opacity: 0.3,
        depth: currentDepth
      };

      if (b.y < MIN_Y) return tree;

      if (currentDepth < maxDepth) {
        tree.branches = [];
        
        for (let i = 0; i < numBranches; i++) {
          const branch = traverse(b, angle + d3.randomNormal(0, 0.3)(), (length / FULL_LENGTH) * 0.7, currentDepth + 1);
          if (branch) tree.branches.push(branch);
        }
      }

      return tree;
    };

    const tree = traverse(a, orientation, scaleRatio);
    
    // Count total branches in tree
    function countBranches(node) {
      let count = 1;
      if (node.branches) {
        node.branches.forEach(branch => count += countBranches(branch));
      }
      return count;
    }

    const totalBranches = countBranches(tree);
    console.log(`Tree has ${totalBranches} total branches`);
    
    // Only create cascade if tree has enough branches
    if (totalBranches >= 20 && totalBranches <= 200) {
      const CASCADE_DEPTH = 1;
      const branchesAtDepth = [];
      
      function findBranchesAtDepth(node) {
        if (node.depth === CASCADE_DEPTH) {
          branchesAtDepth.push(node);
        }
        if (node.branches) {
          node.branches.forEach(findBranchesAtDepth);
        }
      }
      
      findBranchesAtDepth(tree);
      
      if (branchesAtDepth.length > 0) {
        const cascadeBranch = branchesAtDepth.reduce((topmost, current) => 
          current.b.y < topmost.b.y ? current : topmost
        );
        
        function colorCascadePath(node, depth = 0) {
          node.opacity = 1.0;
          
          if (depth < 2 && node.branches) {
            node.branches.forEach(branch => colorCascadePath(branch, depth + 1));
          }
        }
        
        colorCascadePath(cascadeBranch);
        
        const numCascadeBranches = Math.floor(Math.random() * 4) + 6;
        cascadeBranch.branches = [];
        
        for (let i = 0; i < numCascadeBranches; i++) {
          const originalBranchLength = Math.sqrt(
            Math.pow(cascadeBranch.b.x - cascadeBranch.a.x, 2) + 
            Math.pow(cascadeBranch.b.y - cascadeBranch.a.y, 2)
          );

          const cascadeAngle = d3.randomNormal(-Math.PI/2, 0.4)();
          const cascadeLength = Math.max(d3.randomNormal(originalBranchLength * 0.8, originalBranchLength * 0.2)(), 20);
          
          const cascadeEnd = {
            x: Math.cos(cascadeAngle) * cascadeLength + cascadeBranch.b.x,
            y: Math.sin(cascadeAngle) * cascadeLength + cascadeBranch.b.y
          };
          
          const cascadeChild = {
            a: cascadeBranch.b,
            b: cascadeEnd,
            linearDepth: 0.4,
            thickness: 2,
            color: '#333',
            opacity: 1.0,
            depth: CASCADE_DEPTH + 1,
            branches: []
          };
          
          const numSecondLevel = Math.max(d3.randomNormal(2, 1)(), 1);
          for (let j = 0; j < numSecondLevel; j++) {
            const secondAngle = d3.randomNormal(cascadeAngle, 0.4)();
            const secondLength = Math.max(d3.randomNormal(originalBranchLength * 0.5, originalBranchLength * 0.15)(), 15);
            
            const secondEnd = {
              x: Math.cos(secondAngle) * secondLength + cascadeEnd.x,
              y: Math.sin(secondAngle) * secondLength + cascadeEnd.y
            };
            
            cascadeChild.branches.push({
              a: cascadeEnd,
              b: secondEnd,
              linearDepth: 0.3,
              thickness: 1,
              color: '#333',
              opacity: 1.0,
              depth: CASCADE_DEPTH + 2
            });
          }
          
          cascadeBranch.branches.push(cascadeChild);
        }
        
        console.log(`Cascade created after tree developed ${totalBranches} branches`);
      }
    } else {
      console.log(`Tree only has ${totalBranches} branches - no cascade created`);
    }
    
    return tree;
  }

  function drawTree(tree) {
    const branches = [];
    const nodes = new Map(); // Track unique nodes
    
    if (!tree) return branches;
    
    const traverse = t => {
      // Add nodes to track unique positions
      const nodeAKey = `${t.a.x.toFixed(1)},${t.a.y.toFixed(1)}`;
      const nodeBKey = `${t.b.x.toFixed(1)},${t.b.y.toFixed(1)}`;
      
      nodes.set(nodeAKey, { x: t.a.x, y: t.a.y, opacity: t.opacity, color: t.color });
      nodes.set(nodeBKey, { x: t.b.x, y: t.b.y, opacity: t.opacity, color: t.color });

      branches.push({
        id: uniqueId++,
        nodeA: { x: t.a.x, y: t.a.y },
        nodeB: { x: t.b.x, y: t.b.y },
        thickness: 2, // Fixed thickness for network look
        color: t.color,
        opacity: t.opacity
      });

      if (t.branches) {
        t.branches.forEach(traverse);
      }
    };
    
    traverse(tree);
    
    // Add nodes as separate items
    const uniqueNodes = Array.from(nodes.values()).map(node => ({
      id: uniqueId++,
      ...node,
      isNode: true
    }));
    
    return [...branches, ...uniqueNodes];
  }

  function generateTree() {
  uniqueId = 0;
  let attempts = 0;
  let tree;
  
  do {
    attempts++;
    uniqueId = 0; // Reset for each attempt
    
    tree = makeTree(
      { x: width * 0.1, y: height - 50 },
      -Math.PI / 4,
      1.0,
      treeDepth
    );
    
    // Count branches to check if it meets criteria
    function countBranches(node) {
      let count = 1;
      if (node.branches) {
        node.branches.forEach(branch => count += countBranches(branch));
      }
      return count;
    }
    
    const totalBranches = countBranches(tree);
    console.log(`Attempt ${attempts}: Tree has ${totalBranches} branches`);
    
    // Break if we have the right number of branches
    if (totalBranches >= 20 && totalBranches <= 200) {
      break;
    }
    
    // Safety check to prevent infinite loops
    if (attempts > 50) {
      console.log("Max attempts reached, using current tree");
      break;
    }
  } while (true);
  
  allBranches = drawTree(tree);
}

  $effect(() => {
    generateTree();
  });
</script>

<div class="chart-container" bind:clientWidth={width}>
  <svg {width} {height} class="src-network">
    <!-- Draw edges (branches) with pale opacity -->
    <g opacity="0.3">
      {#each allBranches.filter(b => !b.isNode && b.opacity !== 1.0) as branch (branch.id)}
        <line x1={branch.nodeA.x} y1={branch.nodeA.y} x2={branch.nodeB.x} y2={branch.nodeB.y} 
              stroke={branch.color} stroke-width={branch.thickness} />
      {/each}
    </g>

    <!-- Draw cascade edges with full opacity -->
    <g opacity="1.0">
      {#each allBranches.filter(b => !b.isNode && b.opacity === 1.0) as branch (branch.id)}
        <line x1={branch.nodeA.x} y1={branch.nodeA.y} x2={branch.nodeB.x} y2={branch.nodeB.y} 
              stroke={branch.color} stroke-width={branch.thickness} />
      {/each}
    </g>

    <!-- Draw nodes -->
    <g opacity="0.3">
      {#each allBranches.filter(b => b.isNode && b.opacity !== 1.0) as node (node.id)}
        <circle cx={node.x} cy={node.y} r="3" fill={node.color} stroke="white"/>
      {/each}
    </g>

    <g opacity="1.0">
      {#each allBranches.filter(b => b.isNode && b.opacity === 1.0) as node (node.id)}
        <circle cx={node.x} cy={node.y} r="4" fill={node.color} stroke="white" />
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