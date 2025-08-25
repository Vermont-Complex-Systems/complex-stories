import * as d3 from 'd3';

// Parse date values consistently
function parseDate(dateStr) {
  if (!dateStr) return null;
  if (dateStr instanceof Date) return dateStr;
  
  if (typeof dateStr === 'number') {
    return dateStr > 1000000000000 ? new Date(dateStr) : new Date(dateStr * 1000);
  }
  
  return new Date(dateStr);
}

// Check if two circles collide
function checkCollision(x1, y1, r1, x2, y2, r2, padding = 1) {
  const dx = x1 - x2;
  const dy = y1 - y2;
  const distance = Math.sqrt(dx * dx + dy * dy);
  return distance < (r1 + r2 + padding);
}

// Try to place a point horizontally from center
function tryHorizontalPlacement(point, placedPoints, centerX, maxWidth) {
  const margin = 10;
  const step = 2;
  const maxOffset = Math.min(centerX - margin, maxWidth - centerX - margin);
  
  // Try center first, then expand outward
  for (let offset = 0; offset <= maxOffset; offset += step) {
    const positions = offset === 0 ? [0] : [offset, -offset];
    
    for (const xOffset of positions) {
      const testX = centerX + xOffset;
      
      if (testX < margin || testX > maxWidth - margin) continue;
      
      // Check for collisions with placed points
      let hasCollision = false;
      for (const placed of placedPoints) {
        if (checkCollision(testX, point.y, point.r, placed.x, placed.y, placed.r)) {
          hasCollision = true;
          break;
        }
      }
      
      if (!hasCollision) {
        point.x = testX;
        return true;
      }
    }
  }
  
  return false;
}

// Try to place a point with vertical adjustment
function tryVerticalPlacement(point, placedPoints, centerX, maxWidth) {
  const margin = 10;
  const yOffsets = [5, -5, 10, -10, 15, -15, 20, -20, 30, -30];
  const xOffsets = [0, 5, -5, 10, -10, 15, -15];
  
  for (const yOffset of yOffsets) {
    for (const xOffset of xOffsets) {
      const testX = centerX + xOffset;
      const testY = point.y + yOffset;
      
      if (testX < margin || testX > maxWidth - margin) continue;
      
      let hasCollision = false;
      for (const placed of placedPoints) {
        if (checkCollision(testX, testY, point.r, placed.x, placed.y, placed.r)) {
          hasCollision = true;
          break;
        }
      }
      
      if (!hasCollision) {
        point.x = testX;
        point.y = testY;
        return true;
      }
    }
  }
  
  return false;
}

export function dodgeX(data, yField, colorFunction, radiusScale, timeScale, width, height) {
  if (!data || data.length === 0) return [];
  
  // Chart dimensions
  const margin = { left: 40, right: 40 };
  const chartWidth = width - margin.left - margin.right;
  const centerX = chartWidth / 2 + margin.left;
  
  // Create points
  const points = data.map(d => {
    const date = parseDate(d[yField]);
    const y = timeScale(date);
    const r = radiusScale ? radiusScale(d) : 5;
    const color = colorFunction ? colorFunction(d) : '#888888';
    
    return {
      x: centerX, // Will be positioned later
      y,
      r,
      color: color || '#888888', // Fallback if colorFunction returns null/undefined
      data: d // Keep reference to original data
    };
  });
  
  // Sort by radius (largest first) for better placement
  points.sort((a, b) => b.r - a.r);
  
  // Place points
  const placed = [];
  
  for (const point of points) {
    let success = false;
    
    // Try horizontal placement first
    if (tryHorizontalPlacement(point, placed, centerX, chartWidth + margin.left)) {
      success = true;
    }
    // Then try with vertical adjustment
    else if (tryVerticalPlacement(point, placed, centerX, chartWidth + margin.left)) {
      success = true;
    }
    
    if (!success) {
      // Fallback: place at center with small random offset
      point.x = centerX + (Math.random() - 0.5) * 10;
    }
    
    placed.push(point);
  }
  
  return placed;
}