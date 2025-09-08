<script>
  import * as d3 from 'd3';
  import { Leaf } from '@lucide/svelte';
  import { innerWidth, innerHeight } from 'svelte/reactivity/window';
  import { onMount } from 'svelte';

  // Fixed parameters - exactly like original
  const treeDepth = 6;
  const numTrees = 6;
  const numLayers = 3;
  const fogOpacity = 0.8;
  const backgroundColor = '#f8f5e6';
  let width = $state(innerWidth.current);
  let height = 500;

  let allBranches = $state([]);
  let allBlossoms = $state([]);
  let uniqueId = 0;

  // Animation state
  let isVisible = $state(false);
  let container;
  let visibleTrees = $state(0);
  const totalTrees = numTrees * numLayers;
  let treeDepths = $state(Array(totalTrees).fill(0)); // Track depth per tree
  const maxTreeDepth = 6; // Match treeDepth
  let animationComplete = $state(false);

  function makeTree(a, orientation, scaleRatio, maxDepth = 5, isTopLayer = false, layerIndex = 0) {
    const FULL_LENGTH = 300;
    
    const traverse = (a, orientation, scaleRatio, currentDepth = 0) => {
      const scale = scaleRatio * FULL_LENGTH;
      const linearDepth = (maxDepth - currentDepth) / maxDepth;
      const thickness = scaleRatio * linearDepth * 15;
      const numBranches = Math.max(d3.randomNormal(1, 1.5)(), 2);
      const length = Math.max(d3.randomNormal(scale, scale * 0.2)() + 30, 30);
      const angle = d3.randomNormal(orientation, 0.25)();
      const curvature = d3.randomNormal(0, 0.1)();
      
      const b = {
        x: Math.cos(angle) * length + a.x,
        y: Math.sin(angle) * length + a.y
      };
      
      const cp = midOffset(a, b, curvature);
      const bPrime = getQuadraticXY(0.99, a.x, a.y, cp.x, cp.y, b.x, b.y);
      const endAngle = Math.atan2(b.y - bPrime.y, b.x - bPrime.x);

      function getQuadraticXY(t, sx, sy, cp1x, cp1y, ex, ey) {
        return {
          x: (1 - t) * (1 - t) * sx + 2 * (1 - t) * t * cp1x + t * t * ex,
          y: (1 - t) * (1 - t) * sy + 2 * (1 - t) * t * cp1y + t * t * ey
        };
      }

      const tree = {
        a, b, curvature, linearDepth, thickness,
        color: '#333',
        layerIndex: layerIndex,
        depth: currentDepth
      };

      const isTwig = !(maxDepth !== currentDepth && numBranches);

      if (!isTwig) {
        tree.branches = [];
        for (let i = 0; i < numBranches; i++) {
          tree.branches.push(
            traverse(b, endAngle, (length / FULL_LENGTH) * 0.6, currentDepth + 1)
          );
        }

        if (Math.random() > 0.9) { // Removed && isTopLayer
          // Distribute small clusters along the branch
          tree.blossoms = [];
          const numClusters = Math.floor(Math.random() * 2) + 1;
          for (let c = 0; c < numClusters; c++) {
            const t = 0.6 + (c / numClusters) * 0.4; // From 60% to 100% along branch
            const clusterPoint = {
              x: a.x + (b.x - a.x) * t,
              y: a.y + (b.y - a.y) * t
            };
            const cluster = makeBlossomCluster(
              clusterPoint,
              Math.max(d3.randomNormal(0, 1)(), 5), // Smaller spread
              Math.max(d3.randomNormal(0, 1)(), 2), // 2-12 leaves per cluster (8±4, min 2)
              getAutumnLeafColor()
            );
            tree.blossoms.push(...cluster);
          }
        }
      } else {
        if (Math.random() > 0.9) {
          tree.blossoms = makeBlossomCluster(
            tree.b,
            Math.max(d3.randomNormal(0, 8)(), 3),
            Math.max(d3.randomNormal(0, 3)(), 2), // 1-9 leaves per cluster (6±3, min 1)
            getAutumnLeafColor()
          );
        }
      }

      return tree;
    };

    return traverse(a, orientation, scaleRatio);
  }

  function makeBlossomCluster(p, radius, amount, color) {
    const cluster = [];
    for (let i = 0; i < amount; i++) {
      cluster.push({
        x: d3.randomNormal(p.x, radius)(),
        y: d3.randomNormal(p.y, radius)(),
        radius: Math.max(d3.randomNormal(20, 8)(), 5),
        color: varyColor(color)
      });
    }
    return cluster;
  }

  function getAutumnLeafColor() {
    const colors = ['#606c38', '#283618', '#FFC41A', '#dda15e', '#bc6c25', '#F9A80E', '#BD0C0F'];
    return colors[Math.floor(Math.random() * colors.length)];
  }

  function varyColor(color) {
    const hsl = d3.hsl(color);
    hsl.s = Math.min(Math.max(d3.randomNormal(hsl.s, 0.05)(), 0), 1);
    hsl.l = Math.min(Math.max(d3.randomNormal(hsl.l, 0.1)(), 0), 1);
    return hsl.toString();
  }

  function midOffset(a, b, curvature = 0) {
    const mx = (a.x + b.x) / 2;
    const my = (a.y + b.y) / 2;
    const px = a.x - b.x;
    const py = a.y - b.y;
    let nx = -py;
    let ny = px;
    const normalizedLength = Math.sqrt(nx * nx + ny * ny);
    const distance = Math.sqrt(px * px + py * py);
    if (normalizedLength === 0) return { x: mx, y: my };
    nx /= normalizedLength;
    ny /= normalizedLength;
    return {
      x: mx + curvature * distance * nx,
      y: my + curvature * distance * ny
    };
  }

  function drawTree(tree, treeIndex) {
    const traverse = t => {
      const opacity = t.layerIndex === 0 ? 1 : (t.layerIndex === 1 ? 0.8 : 0.4);
      
      allBranches.push({
        id: uniqueId++,
        path: `M ${t.a.x} ${t.a.y} Q ${midOffset(t.a, t.b, t.curvature).x} ${midOffset(t.a, t.b, t.curvature).y} ${t.b.x} ${t.b.y}`,
        thickness: Math.max(10 * t.linearDepth, 0.5),
        color: t.color,
        layerIndex: t.layerIndex,
        treeIndex: treeIndex,
        depth: t.depth
      });

      if (t.blossoms) {
        t.blossoms.forEach(blossom => {
          allBlossoms.push({
            id: uniqueId++,
            x: blossom.x,
            y: blossom.y,
            scale: blossom.radius / 80,
            color: blossom.color,
            rotation: Math.random() * 360,
            opacity: opacity,
            layerIndex: t.layerIndex,
            treeIndex: treeIndex
          });
        });
      }

      if (t.branches) {
        t.branches.forEach(traverse);
      }
    };
    traverse(tree);
  }

  function generateForest() {
    uniqueId = 0;
    allBranches = [];
    allBlossoms = [];
    
    let treeIndex = 0;
    for (let j = 0; j < numLayers; j++) {
      for (let i = 0; i < numTrees; i++) {
        const tree = makeTree(
          {
            x: d3.randomUniform(-width, width * 2)(),
            y: d3.randomUniform(
              height + 10,
              height + (1000 * j) / numLayers + 100
            )()
          },
          -Math.PI / 4,
          j / numLayers + 0.4,
          treeDepth,
          true, // Always true - all trees can have leaves
          j
        );
        drawTree(tree, treeIndex);
        treeIndex++;
      }
    }
  }

  // Animation function - progressive branch-by-branch growth (faster & smoother)
  function animateTreesIn() {
    let currentTree = 0;
    
    const animateNextTree = () => {
      if (currentTree >= totalTrees) {
        // All trees are complete - show the replay button
        animationComplete = true;
        return;
      }
      
      visibleTrees = currentTree + 1; // Show this tree
      treeDepths[currentTree] = 0; // Start with depth 0 (trunk)
      
      // Animate depth progression for current tree
      const animateDepth = () => {
        if (treeDepths[currentTree] < maxTreeDepth) {
          treeDepths[currentTree] += 1;
          setTimeout(animateDepth, 120); // Faster: 120ms per depth level (was 200ms)
        } else {
          // Tree is fully grown, move to next tree
          currentTree += 1;
          setTimeout(animateNextTree, 80); // Faster overlap: 80ms pause (was 300ms)
        }
      };
      
      animateDepth();
    };
    
    animateNextTree();
  }

  // Restart animation function
  function restartAnimation() {
    // Reset all animation state
    visibleTrees = 0;
    treeDepths = Array(totalTrees).fill(0);
    animationComplete = false; // Hide button during animation
    
    // Regenerate forest with new random positions
    generateForest();
    
    // Start animation
    setTimeout(animateTreesIn, 100); // Small delay to let DOM update
  }

  // Set up intersection observer
  onMount(() => {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting && !isVisible) {
          console.log('BranchingNetwork is now visible! Starting animation...');
          isVisible = true;
          animateTreesIn();
        }
      });
    }, { 
      threshold: 0.3,
      rootMargin: '50px'
    });
    
    if (container) {
      observer.observe(container);
    }
    
    return () => {
      if (container) observer.unobserve(container);
    };
  });

  // Generate forest data once on component initialization
  generateForest();
</script>

<div
  class="chart-container"
  bind:clientWidth={width}
  bind:this={container}
>
  <svg {width} {height}>
  {#each Array(numLayers) as _, layerIndex}
    <g opacity={layerIndex === 0 ? 1 : (layerIndex === 1 ? 0.3 : 0.4)}>
      <!-- Tree branches for this layer -->
      {#each allBranches.filter(b => b.layerIndex === layerIndex && b.treeIndex < visibleTrees && b.depth <= (treeDepths[b.treeIndex] || 0)) as branch (branch.id)}
        <path
          d={branch.path}
          stroke={branch.color}
          stroke-width={branch.thickness}
          stroke-linecap="round"
          fill="none"
          style="transition: opacity 0.3s ease-in-out;"
        />
      {/each}

      <!-- Leaves for this layer - only show after tree is fully grown -->
      {#each allBlossoms.filter(l => l.layerIndex === layerIndex && l.treeIndex < visibleTrees && (treeDepths[l.treeIndex] || 0) >= maxTreeDepth) as leaf (leaf.id)}
        <g transform="translate({leaf.x}, {leaf.y}) rotate({leaf.rotation}) scale({leaf.scale})" 
           style="transition: opacity 0.4s ease-in-out;">
          <Leaf 
            size={100} 
            color="black" 
            fill={leaf.color}
            strokeWidth={0.5}
          />
        </g>∂
      {/each}
    </g>
  {/each}
</svg>
  
  {#if animationComplete}
    <div class="button-ctn" style="animation: fadeIn 0.5s ease-in;">
      <button onclick={restartAnimation} class="regenerate-btn">
        Replay
      </button>
    </div>
  {/if}
</div>

<style>
  .chart-container {
    width: 99vw;
    margin-bottom: 3rem;
    margin-top: 3rem;
    border:1px solid black;
    position: relative;
  }
  
  .button-ctn {
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
    font-weight: 500;
  }
  
  .regenerate-btn:hover {
    background: #3a4c2a;
  }

  @keyframes fadeIn {
    from { 
      opacity: 0; 
      transform: translateY(10px);
    }
    to { 
      opacity: 1; 
      transform: translateY(0);
    }
  }
  
</style>