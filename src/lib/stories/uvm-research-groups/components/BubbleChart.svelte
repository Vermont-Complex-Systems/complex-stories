<!-- BubbleChart.svelte -->
<script>
  let { data } = $props();

  console.log("Bubble chart loaded with data:", data?.length);

  let width = 800;
  let height = 1000;
  let points = $state([]);

  function createPoint(d, targetY) {
    const ageDiff = +d.age_diff;
    let color = "#20A387FF"; // Same age (green)
    
    if (ageDiff > 7) {
      color = "#404788FF"; // Older (blue)
    } else if (ageDiff < -7) {
      color = "#FDE725FF"; // Younger (yellow)
    }

    const radius = Math.sqrt(+d.all_times_collabo || 1) * 2 + 3;

    return {
      x: 0, // Will be set during placement
      y: targetY,
      r: radius,
      color: color,
      name: d.coauth_name,
      year: d.pub_year,
      date: d.pub_date,
      age_diff: d.age_diff,
      collabs: d.all_times_collabo,
      faculty: d.name
    };
  }

  function checkCollision(testX, testY, point, placedPoints, padding = 2) {
    for (const existing of placedPoints) {
      const dx = testX - existing.x;
      const dy = testY - existing.y;
      const distance = Math.sqrt(dx * dx + dy * dy);
      const minDistance = point.r + existing.r + padding;
      
      if (distance < minDistance) {
        return true; // Collision detected
      }
    }
    return false; // No collision
  }

  function canUseCenter(point, allPoints) {
    const currentRank = allPoints.indexOf(point);
    const totalPoints = allPoints.length;
    return currentRank < totalPoints * 0.2 || point.r > 8;
  }

  function tryHorizontalPlacement(point, placedPoints, centerX, allPoints) {
    const maxOffset = 350;
    const step = 5;
    
    for (let offset = 0; offset <= maxOffset; offset += step) {
      const positions = offset === 0 ? [0] : [offset, -offset];
      
      for (const xOffset of positions) {
        const testX = centerX + xOffset;
        const testY = point.y;
        
        // Check center restrictions
        if (xOffset === 0 && !canUseCenter(point, allPoints)) {
          continue;
        }
        
        if (!checkCollision(testX, testY, point, placedPoints)) {
          point.x = testX;
          return true; // Successfully placed
        }
      }
    }
    return false; // Could not place horizontally
  }

  function tryVerticalPlacement(point, placedPoints, centerX) {
    const step = 5;
    
    // Try moderate vertical offsets with small horizontal adjustments
    for (let yOffset = step; yOffset <= 100; yOffset += step) {
      const yPositions = [yOffset, -yOffset];
      
      for (const yOff of yPositions) {
        const xOffsets = [0, 10, -10, 20, -20];
        
        for (const xOff of xOffsets) {
          const testX = centerX + xOff;
          const testY = point.y + yOff;
          
          if (!checkCollision(testX, testY, point, placedPoints)) {
            point.x = testX;
            point.y = testY;
            return true;
          }
        }
      }
    }
    return false;
  }

  function tryFinalFallback(point, placedPoints, centerX) {
    // Large vertical offsets with random horizontal placement
    for (let yOffset = 105; yOffset <= 200; yOffset += 10) {
      const yPositions = [yOffset, -yOffset];
      
      for (const yOff of yPositions) {
        const testX = centerX + (Math.random() - 0.5) * 100;
        const testY = point.y + yOff;
        
        if (!checkCollision(testX, testY, point, placedPoints)) {
          point.x = testX;
          point.y = testY;
          return true;
        }
      }
    }
    return false;
  }

  function placePoint(point, placedPoints, centerX, allPoints) {
    return tryHorizontalPlacement(point, placedPoints, centerX, allPoints) ||
           tryVerticalPlacement(point, placedPoints, centerX) ||
           tryFinalFallback(point, placedPoints, centerX);
  }

  function processData() {
    if (!data || data.length === 0) {
      console.log("No data to process");
      points = [];
      return;
    }

    console.log("Processing data...", data.length, "items");

    // Get date range for Y positioning
    const allDates = data.map(d => new Date(d.pub_date));
    const minDate = new Date(Math.min(...allDates));
    const maxDate = new Date(Math.max(...allDates));
    console.log("Date range:", minDate.getFullYear(), "to", maxDate.getFullYear());

    // Group by exact publication date
    const byDate = new Map();
    data.forEach(d => {
      const dateKey = d.pub_date;
      if (!byDate.has(dateKey)) byDate.set(dateKey, []);
      byDate.get(dateKey).push(d);
    });

    const margin = 80;
    const chartHeight = height - 2 * margin;
    const centerX = width / 2;

    // Create ALL points first with their target Y positions
    const allPoints = [];
    for (const [dateKey, dateData] of byDate) {
      const pubDate = new Date(dateKey);
      const dateProgress = (pubDate - minDate) / (maxDate - minDate);
      const targetY = margin + dateProgress * chartHeight;
      
      for (const d of dateData) {
        allPoints.push(createPoint(d, targetY));
      }
    }

    // Sort ALL points by collaboration count (largest first globally)
    allPoints.sort((a, b) => b.collabs - a.collabs);

    // Place each point using the modular placement system
    const placedPoints = [];
    for (const point of allPoints) {
      if (placePoint(point, placedPoints, centerX, allPoints)) {
        placedPoints.push(point);
      } else {
        // Emergency fallback - place at center with warning
        console.warn('Could not place point:', point.name);
        point.x = centerX;
        placedPoints.push(point);
      }
    }

    console.log("Created", allPoints.length, "points");
    points = allPoints;
  }

  let hovered = $state(null);

  // Process data when component mounts or data changes
  $effect(() => {
    processData();
  });
</script>

<div>
  <h2>Peter Sheridan Dodds's Coauthors</h2>
  
  <svg {width} {height} style="border: 1px solid #eee; background: white; border-radius: 4px;">
    <!-- Center line -->
    <line 
      x1={width/2} 
      x2={width/2} 
      y1="0" 
      y2={height} 
      stroke="#e0e0e0" 
      stroke-width="1"
      stroke-dasharray="5,5"
    />
    
    <!-- Grid lines for years -->
    {#each Array.from({length: 13}, (_, i) => 1999 + i * 2) as year}
      {@const yearProgress = (year - 1999) / (2023 - 1999)}
      {@const y = 80 + yearProgress * 840}
      <line 
        x1="0" 
        x2={width} 
        y1={y} 
        y2={y} 
        stroke="#f0f0f0" 
        stroke-width="1"
      />
      <text x="10" y={y + 4} text-anchor="start" font-size="11" fill="#666">
        {year}
      </text>
    {/each}
    
    <!-- Data points -->
    {#each points as point}
      <circle
        cx={point.x}
        cy={point.y}
        r={point.r}
        fill={point.color}
        stroke="black"
        stroke-width="0.3"
        fill-opacity={hovered && hovered !== point ? 0.3 : 0.9}
        style="cursor: pointer; transition: opacity 0.2s;"
        onmouseover={() => hovered = point}
        onmouseleave={() => hovered = null}
      >
        <title>{point.name} ({point.year}) - {point.faculty}</title>
      </circle>
    {/each}
  </svg>
  
  <!-- Legend -->
  <div style="text-align: center; margin-top: 15px; font-family: system-ui, sans-serif;">
    <div style="display: flex; justify-content: center; gap: 20px; align-items: center;">
      <span style="display: flex; align-items: center; gap: 5px; font-size: 14px;">
        <span style="display: inline-block; width: 14px; height: 14px; background: #FDE725FF; border-radius: 50%; border: 1px solid #333;"></span>
        younger (7+ years)
      </span>
      <span style="display: flex; align-items: center; gap: 5px; font-size: 14px;">
        <span style="display: inline-block; width: 14px; height: 14px; background: #20A387FF; border-radius: 50%; border: 1px solid #333;"></span>
        similar age (±7 years)
      </span>
      <span style="display: flex; align-items: center; gap: 5px; font-size: 14px;">
        <span style="display: inline-block; width: 14px; height: 14px; background: #404788FF; border-radius: 50%; border: 1px solid #333;"></span>
        older (7+ years)
      </span>
    </div>
    <div style="margin-top: 10px; font-size: 12px; color: #666;">
      Circle size represents total collaborations
    </div>
  </div>

  <!-- Tooltip -->
  {#if hovered}
    <div style="
      position: fixed;
      background: rgba(0,0,0,0.9);
      color: white;
      padding: 8px 12px;
      border-radius: 4px;
      font-size: 12px;
      pointer-events: none;
      z-index: 1000;
      top: 10px;
      left: 50%;
      transform: translateX(-50%);
      font-family: system-ui, sans-serif;
    ">
      <strong>{hovered.name}</strong> ({hovered.year})<br>
      Age difference: {hovered.age_diff} years<br>
      Total collaborations: {hovered.collabs}
    </div>
  {/if}
</div>

<style>
  h2 {
    text-align: center;
    margin: 0 0 20px 0;
    color: #666;
    font-family: system-ui, sans-serif;
    font-weight: 400;
    font-size: 18px;
  }
</style>