<script>
  import * as d3 from 'd3';

  let width = $state(500);
  const height = 500;
  const treeDepth = 6;
  let tauValue = $state(1.5); // Power law parameter

  let allBranches = $state([]);
  let uniqueId = 0;

  // Power law distribution function
  function powerLawSample(tau = 2.5, xMin = 1, xMax = 50) {
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

  function makeTree(a, orientation, scaleRatio, maxDepth = 5) {
    const FULL_LENGTH = 200;
    const MIN_Y = 100;
    
    const traverse = (a, orientation, scaleRatio, currentDepth = 0) => {
      if (a.y < MIN_Y) return null;
      
      const scale = scaleRatio * FULL_LENGTH;
      const linearDepth = (maxDepth - currentDepth) / maxDepth;
      const thickness = scaleRatio * linearDepth * 20;
      
      const numBranches = Math.max(d3.randomNormal(1.3, 0.5)(), 1);
      
      const length = Math.max(d3.randomNormal(scale * 0.6, scale * 0.1)() + 20, 20);
      let angle = d3.randomNormal(orientation, 0.4)(); // Back to original
      
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
        
        // Back to original simple branching
        for (let i = 0; i < numBranches; i++) {
          const branch = traverse(b, angle + d3.randomNormal(0, 0.3)(), (length / FULL_LENGTH) * 0.7, currentDepth + 1);
          if (branch) tree.branches.push(branch);
        }
      }

      return tree;
    };

    const tree = traverse(a, orientation, scaleRatio);
    
    function countBranches(node) {
      let count = 1;
      if (node.branches) {
        node.branches.forEach(branch => count += countBranches(branch));
      }
      return count;
    }

    const totalBranches = countBranches(tree);
    
    if (totalBranches >= 20 && totalBranches <= 200) { // Back to original thresholds
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
          if (depth >= 1) {
            node.opacity = 1.0;
          }
          
          if (depth < 2 && node.branches) {
            node.branches.forEach(branch => colorCascadePath(branch, depth + 1));
          }
        }
        
        colorCascadePath(cascadeBranch);
        
        // Use power law distribution with slider value
        const numCascadeBranches = Math.round(powerLawSample(tauValue, 3, 25));
        cascadeBranch.branches = [];
        
        console.log(`Power law cascade (α=${tauValue}): ${numCascadeBranches} branches`);
        
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
      }
    }
    
    return tree;
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
    let attempts = 0;
    let tree;
    
    do {
      attempts++;
      uniqueId = 0;
      
      tree = makeTree(
        { x: width * 0.1, y: height - 50},
        -Math.PI / 2,
        1.0,
        treeDepth
      );
      
      function countBranches(node) {
        let count = 1;
        if (node.branches) {
          node.branches.forEach(branch => count += countBranches(branch));
        }
        return count;
      }
      
      const totalBranches = countBranches(tree);
      
      if (totalBranches >= 20 && totalBranches <= 200) {
        break;
      }
      
      if (attempts > 50) {
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
  <div class="controls">
    <input 
    type="range" 
    bind:value={tauValue} 
    min="1.0" 
    max="4.0" 
    step="0.1"
    class="tau-slider"
    />
    <label>τ = {tauValue.toFixed(1)}</label>
  </div>
  
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
  background: #4a5c3a;
  cursor: pointer;
}

.tau-slider::-moz-range-thumb {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: #4a5c3a;
  cursor: pointer;
  border: none;
}

.tau-slider::-moz-range-progress {
  background: #4a5c3a;
  height: 6px;
  border-radius: 3px;
}

.tau-slider::-webkit-slider-runnable-track {
  background: #ddd;
  height: 6px;
  border-radius: 3px;
}

  .controls small {
    color: #666;
    font-style: italic;
  }
  
  .src-network {
    overflow: visible;
  }

 .chart-container .button-ctn {
  position: absolute;
  bottom: 10px;
  right: 10px;
  display: flex;
  align-items: flex-end;
  gap: 15px;
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