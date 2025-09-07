<script>
  import * as d3 from 'd3';

  let width = $state(600);
  const height = 475;
  const maxDepth = 5;
  const p = 0.6; // Probability of being receptive
  
  let regenerateFlag = $state(0);
  
  let treeData = $derived.by(() => {
    regenerateFlag;
    
    let allNodes = [];
    let allEdges = [];
    let maxIntensityByGen = {};
    let nodeCounter = 0;
    
    const centerX = width / 2;
    const centerY = height / 2;
    
    // Create seed node
    const seed = {
      id: nodeCounter++,
      x: centerX,
      y: centerY,
      intensity: 1,
      generation: 0,
      isAbsorbed: false,
      wasReceptive: true, // Seed is considered receptive
      color: '#f97316' // Orange
    };
    
    allNodes.push(seed);
    maxIntensityByGen[0] = 1;
    
    const queue = [seed];
    
    while (queue.length > 0) {
      const currentNode = queue.shift();
      
      // Skip if at max depth or absorbed
      if (currentNode.generation >= maxDepth || currentNode.isAbsorbed) {
        continue;
      }
      
      const numChildren = Math.min(Math.max(d3.randomPoisson(1.5)(), 1), 3);
      
      for (let i = 0; i < numChildren; i++) {
        const childIsReceptive = Math.random() < p;
        const childIntensity = childIsReceptive ? 
          currentNode.intensity + 1 : 
          currentNode.intensity - 1;
        
        const childGeneration = currentNode.generation + 1;
        
        // Position child
        let branchAngle;
        if (currentNode.generation === 0) {
          const baseAngle = (i / numChildren) * 2 * Math.PI;
          const randomOffset = d3.randomNormal(0, 0.3)();
          branchAngle = baseAngle + randomOffset;
        } else {
          const parentDirection = Math.atan2(currentNode.y - centerY, currentNode.x - centerX);
          const maxSpread = Math.PI / 3;
          const spreadAngle = (i - (numChildren - 1) / 2) * (maxSpread / Math.max(numChildren - 1, 1));
          const randomVariation = d3.randomNormal(0, 0.2)();
          branchAngle = parentDirection + spreadAngle + randomVariation;
        }
        
        // If intensity would be 0 or negative, create absorbing boundary
        const isAbsorbingBoundary = childIntensity <= 0;
        const branchLength = isAbsorbingBoundary ? 25 : 34;
        
        const childX = currentNode.x + Math.cos(branchAngle) * branchLength;
        const childY = currentNode.y + Math.sin(branchAngle) * branchLength;
        
        // Create child node
        const child = {
          id: nodeCounter++,
          x: childX,
          y: childY,
          intensity: childIntensity, // Keep the actual calculated intensity (can be 0)
          generation: childGeneration,
          isAbsorbed: false, // Don't mark as absorbed yet
          wasReceptive: childIsReceptive,
          // Color based on receptiveness, not intensity:
          // - Receptive nodes are orange
          // - Non-receptive nodes are blue
          // We'll handle absorbing boundaries separately
          color: childIsReceptive ? '#f97316' : '#3b82f6'
        };
        
        // If this child has intensity 0, it will create absorbing boundary children
        // but the child itself is still blue (non-receptive) or orange (receptive)
        
        allNodes.push(child);
        
        // Track max intensity for this generation
        if (maxIntensityByGen[childGeneration] === undefined) {
          maxIntensityByGen[childGeneration] = Math.max(0, child.intensity);
        } else {
          maxIntensityByGen[childGeneration] = Math.max(maxIntensityByGen[childGeneration], Math.max(0, child.intensity));
        }
        
        // Create edge
        allEdges.push({
          id: nodeCounter++,
          x1: currentNode.x,
          y1: currentNode.y,
          x2: child.x,
          y2: child.y,
          isAbsorbed: false
        });
        
        // If child has intensity 0 or negative, it should create an absorbing boundary child
        if (childIntensity <= 0) {
          // Create absorbing boundary node
          const absorbingBoundaryAngle = branchAngle; // Same direction
          const absorbingBoundaryLength = 42; // Short distance
          const absorbingX = child.x + Math.cos(absorbingBoundaryAngle) * absorbingBoundaryLength;
          const absorbingY = child.y + Math.sin(absorbingBoundaryAngle) * absorbingBoundaryLength;
          
          const absorbingBoundary = {
            id: nodeCounter++,
            x: absorbingX,
            y: absorbingY,
            intensity: 0,
            generation: childGeneration + 1,
            isAbsorbed: true,
            wasReceptive: false,
            color: '#ccc' // Gray for absorbing boundary
          };
          
          allNodes.push(absorbingBoundary);
          
          // Create dashed edge to absorbing boundary
          allEdges.push({
            id: nodeCounter++,
            x1: child.x,
            y1: child.y,
            x2: absorbingBoundary.x,
            y2: absorbingBoundary.y,
            isAbsorbed: true
          });
          
          // Update max intensity for absorbing boundary generation
          const absorbingGen = childGeneration + 1;
          if (maxIntensityByGen[absorbingGen] === undefined) {
            maxIntensityByGen[absorbingGen] = 0;
          } else {
            maxIntensityByGen[absorbingGen] = Math.max(maxIntensityByGen[absorbingGen], 0);
          }
        } else {
          // Only add to queue if intensity > 0
          queue.push(child);
        }
      }
    }
    
    // Calculate generation circles based on actual node positions
    const generationCircles = [];
    for (let gen = 0; gen <= maxDepth; gen++) {
      if (maxIntensityByGen[gen] !== undefined) {
        const nodesAtGeneration = allNodes.filter(node => node.generation === gen);
        
        if (nodesAtGeneration.length > 0) {
          let totalDistance = 0;
          nodesAtGeneration.forEach(node => {
            const distance = Math.sqrt(
              Math.pow(node.x - centerX, 2) + Math.pow(node.y - centerY, 2)
            );
            totalDistance += distance;
          });
          
          const averageRadius = totalDistance / nodesAtGeneration.length;
          
          generationCircles.push({
            generation: gen,
            x: centerX,
            y: centerY,
            radius: averageRadius,
            maxIntensity: maxIntensityByGen[gen]
          });
        }
      }
    }
    
    return { allNodes, allEdges, generationCircles };
  });

  function regenerateTree() {
    regenerateFlag++;
  }
</script>

<div class="chart-container" bind:clientWidth={width}>
  <svg {width} {height} class="src-network">
    <!-- Generation circles -->
    <g opacity="0.3">
      {#each treeData.generationCircles as circle}
        <circle 
          cx={circle.x} 
          cy={circle.y} 
          r={circle.radius} 
          fill="none" 
          stroke="grey" 
          stroke-width="2"
          stroke-dasharray="5,3"
        />
        {#if circle.radius > 5}
          <text 
            x={circle.x} 
            y={circle.y - circle.radius - 8} 
            text-anchor="middle" 
            font-size="12" 
            font-weight="bold"
          >
            n={circle.generation}: I_max = {circle.maxIntensity}
          </text>
        {/if}
      {/each}
    </g>

    <!-- Edges -->
    <g opacity="0.5">
      {#each treeData.allEdges as edge}
        <line 
          x1={edge.x1} 
          y1={edge.y1} 
          x2={edge.x2} 
          y2={edge.y2} 
          stroke={edge.isAbsorbed ? '#999' : '#666'}
          stroke-width={edge.isAbsorbed ? '0.5' : '1'}
        />
      {/each}
    </g>

    <!-- Nodes -->
    <g>
      {#each treeData.allNodes as node}
        <circle 
          cx={node.x} 
          cy={node.y} 
          r={node.isAbsorbed ? 5 : 6}
          fill={node.color}
          stroke="black"
          stroke-width="0.5"
          opacity={node.isAbsorbed ? 0.3 : 1}
        />
        
        <!-- Intensity labels -->
        <text 
          x={node.x} 
          y={node.y}
          dx={-3}
          dy={3}
          font-size={node.isAbsorbed ? 0 : 10}
          stroke={'black'}
          stroke-width="0.5"
        >
          {node.intensity}
        </text>
      {/each}
    </g>
  </svg>
  
  <div class="button-ctn">
    <button onclick={regenerateTree} class="regenerate-btn">
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