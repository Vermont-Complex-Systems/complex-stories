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

// Try to place a point horizontally from center - allow overflow for dense collaboration areas
function tryHorizontalPlacement(point, placedPoints, centerX, maxWidth) {
  const step = 1; // Smaller step for stronger gravity effect
  const maxOffset = maxWidth * 2; // Allow much wider placement, can overflow the container
  
  // Try center first, then expand outward
  for (let offset = 0; offset <= maxOffset; offset += step) {
    const positions = offset === 0 ? [0] : [offset, -offset];
    
    for (const xOffset of positions) {
      const testX = centerX + xOffset;
      
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

// Try to place a point with vertical adjustment - allow horizontal overflow
function tryVerticalPlacement(point, placedPoints, centerX, maxWidth) {
  const yOffsets = [8, -8, 16, -16, 25, -25, 35, -35, 50, -50, 65, -65, 80, -80, 100, -100, 120, -120, 150, -150];
  const xOffsets = [0, 3, -3, 6, -6, 10, -10, 15, -15, 20, -20, 25, -25, 30, -30, 40, -40, 50, -50]; // Smaller, more gradual X offsets for stronger gravity
  
  for (const yOffset of yOffsets) {
    for (const xOffset of xOffsets) {
      const testX = centerX + xOffset;
      const testY = point.y + yOffset;
      
      // Remove width constraints - allow overflow
      
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

// Spiral placement as last resort for highly dense areas - allow horizontal overflow
function trySpiralPlacement(point, placedPoints, centerX, centerY, maxWidth) {
  const maxRadius = maxWidth * 1.5; // Allow much larger radius, can overflow horizontally
  const angleStep = Math.PI / 12; // 15 degrees - more positions to try
  const radiusStep = point.r + 2;
  
  for (let radius = radiusStep; radius <= maxRadius; radius += radiusStep) {
    for (let angle = 0; angle < 2 * Math.PI; angle += angleStep) {
      const testX = centerX + radius * Math.cos(angle);
      const testY = centerY + radius * Math.sin(angle);
      
      // Remove width constraints - allow horizontal overflow to show collaboration density
      
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
    const y = timeScale(date) + (Math.random() - 0.5) * 12; // Add small initial vertical jitter
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
    // Try spiral placement as last resort
    else if (trySpiralPlacement(point, placed, centerX, point.y, chartWidth + margin.left)) {
      success = true;
    }
    
    if (!success) {
      // Final fallback: place at center with larger random offset to spread points out more
      const maxOffset = Math.min(50, chartWidth * 0.2); // Allow much larger spread
      point.x = centerX + (Math.random() - 0.5) * maxOffset;
      point.y = point.y + (Math.random() - 0.5) * 80; // Add more vertical jitter
    }
    
    placed.push(point);
  }
  
  return placed;
}