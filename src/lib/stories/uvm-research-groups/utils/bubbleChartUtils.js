// bubbleChartUtils.js

export function createPoint(d, targetY) {
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
    faculty: d.name,
    shared_institutions: d.shared_institutions,
    coauth_aid: d.coauth_aid
  };
}

export function checkCollision(testX, testY, point, placedPoints, padding = 2) {
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

export function canUseCenter(point, allPoints) {
  const currentRank = allPoints.indexOf(point);
  const totalPoints = allPoints.length;
  return currentRank < totalPoints * 0.2 || point.r > 8;
}

export function tryHorizontalPlacement(point, placedPoints, centerX, allPoints) {
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

export function tryVerticalPlacement(point, placedPoints, centerX) {
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

export function tryFinalFallback(point, placedPoints, centerX) {
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

export function placePoint(point, placedPoints, centerX, allPoints) {
  return tryHorizontalPlacement(point, placedPoints, centerX, allPoints) ||
         tryVerticalPlacement(point, placedPoints, centerX) ||
         tryFinalFallback(point, placedPoints, centerX);
}

export function processDataPoints(data, width, height) {
  if (!data || data.length === 0) {
    return [];
  }

  // Constants - declare once
  const margin = 80;
  const chartHeight = height - 2 * margin;
  const centerX = width / 2;

  // Get date range for Y positioning - add padding around actual data
  const allDates = data.map(d => new Date(d.pub_date));
  const actualMinDate = new Date(Math.min(...allDates));
  const actualMaxDate = new Date(Math.max(...allDates));
  
  // Add 5 years padding on each side
  const minDate = new Date(actualMinDate.getFullYear() - 5, 0, 1); // 5 years before
  const maxDate = new Date(actualMaxDate.getFullYear() + 5, 11, 31); // 5 years after

  // Group by exact publication date
  const byDate = new Map();
  data.forEach(d => {
    const dateKey = d.pub_date;
    if (!byDate.has(dateKey)) byDate.set(dateKey, []);
    byDate.get(dateKey).push(d);
  });

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

  return allPoints;
}