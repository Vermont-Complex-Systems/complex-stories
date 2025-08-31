<!-- BranchingNetwork.svelte -->
<script>
  // Define nodes with manual positions
  const nodes = [
    // Level 0: 1 node
    { id: 0, x: 200, y: 50, level: 0 },
    
    // Level 1: 2 nodes
    { id: 1, x: 100, y: 150, level: 1 },
    { id: 2, x: 300, y: 150, level: 1 },
    
    // Level 2: 4 nodes
    { id: 3, x: 50, y: 250, level: 2 },
    { id: 4, x: 150, y: 250, level: 2 },
    { id: 5, x: 250, y: 250, level: 2 },
    { id: 6, x: 350, y: 250, level: 2 },
    
    // Level 3: 8 nodes
    { id: 7, x: 25, y: 350, level: 3 },
    { id: 8, x: 75, y: 350, level: 3 },
    { id: 9, x: 125, y: 350, level: 3 },
    { id: 10, x: 175, y: 350, level: 3 },
    { id: 11, x: 225, y: 350, level: 3 },
    { id: 12, x: 275, y: 350, level: 3 },
    { id: 13, x: 325, y: 350, level: 3 },
    { id: 14, x: 375, y: 350, level: 3 }
  ];

  // Define links manually
  const links = [
    // Level 0 to Level 1
    { source: 0, target: 1 },
    { source: 0, target: 2 },
    
    // Level 1 to Level 2
    { source: 1, target: 3 },
    { source: 1, target: 4 },
    { source: 2, target: 5 },
    { source: 2, target: 6 },
    
    // Level 2 to Level 3
    { source: 3, target: 7 },
    { source: 3, target: 8 },
    { source: 4, target: 9 },
    { source: 4, target: 10 },
    { source: 5, target: 11 },
    { source: 5, target: 12 },
    { source: 6, target: 13 },
    { source: 6, target: 14 }
  ];

  const width = 400;
  const height = 400;
</script>

<svg {width} {height}>
  <!-- Links -->
  {#each links as link}
    {@const sourceNode = nodes.find(n => n.id === link.source)}
    {@const targetNode = nodes.find(n => n.id === link.target)}
    <line
      x1={sourceNode.x}
      y1={sourceNode.y}
      x2={targetNode.x}
      y2={targetNode.y}
      stroke="#999"
      stroke-width="2"
    />
  {/each}

  <!-- Nodes as rabbits -->
  {#each nodes as node}
    <g transform="translate({node.x}, {node.y})">
      <!-- Rabbit body (ellipse) -->
      <ellipse
        cx="0"
        cy="0"
        rx="12"
        ry="8"
        fill="white"
        stroke="#e76f51"
        stroke-width="1"
      />
      
      <!-- Rabbit ears -->
      <ellipse
        cx="-6"
        cy="-12"
        rx="3"
        ry="8"
        fill="white"
        stroke="#e76f51"
        stroke-width="1"
      />
      <ellipse
        cx="6"
        cy="-12"
        rx="3"
        ry="8"
        fill="white"
        stroke="#e76f51"
        stroke-width="1"
      />
      
      <!-- Rabbit face -->
      <circle cx="-4" cy="-2" r="1.5" fill="#2a9d8f" />
      <circle cx="4" cy="-2" r="1.5" fill="#2a9d8f" />
      <circle cx="0" cy="2" r="1" fill="#e76f51" />
    </g>
  {/each}
</svg>