import * as d3 from 'd3';

// Improved collision detection with better spacing
export function checkCollision(testX, testY, point, placedPoints, padding = 1) {
  for (const existing of placedPoints) {
    const dx = testX - existing.x;
    const dy = testY - existing.y;
    const distance = Math.sqrt(dx * dx + dy * dy);
    const minDistance = point.r + existing.r + padding;
    
    if (distance < minDistance) {
      return true;
    }
  }
  return false;
}

// More aggressive horizontal placement like Plot's dodgeX
export function tryHorizontalPlacement(point, placedPoints, centerX, effectiveWidth, allPoints = null) {
  const margin = 5;
  const maxOffset = Math.min(centerX - margin, effectiveWidth - centerX - margin);
  const step = 2;
  const offsets = d3.range(0, maxOffset + 1, step);
  
  for (const offset of offsets) {
    const positions = offset === 0 ? [0] : [offset, -offset];
    
    for (const xOffset of positions) {
      const testX = centerX + xOffset;
      const testY = point.y;
      
      if (xOffset === 0 && allPoints && !canUseCenterLine(point, allPoints)) {
        continue;
      }
      
      if (testX < margin || testX > effectiveWidth - margin) continue;
      
      if (!checkCollision(testX, testY, point, placedPoints, 0.5)) {
        point.x = testX;
        return true;
      }
    }
  }
  return false;
}

export function canUseCenterLine(point, allPoints) {
  const currentRank = allPoints.indexOf(point);
  const totalPoints = allPoints.length;
  return currentRank < totalPoints * 0.6 || point.r > 4;
}

export function placePointMultiPass(point, placedPoints, centerX, effectiveWidth, allPoints = null) {
  if (tryHorizontalPlacement(point, placedPoints, centerX, effectiveWidth, allPoints)) {
    return true;
  }
  
  if (tryVerticalPlacement(point, placedPoints, centerX, effectiveWidth)) {
    return true;
  }
  
  const step = 1;
  const maxOffset = Math.min(centerX - 5, effectiveWidth - centerX - 5);
  const offsets = d3.range(0, maxOffset + 1, step);
  
  for (const offset of offsets) {
    const positions = offset === 0 ? [0] : [offset, -offset];
    
    for (const xOffset of positions) {
      const testX = centerX + xOffset;
      const testY = point.y;
      
      if (testX < 5 || testX > effectiveWidth - 5) continue;
      
      if (!checkCollision(testX, testY, point, placedPoints, 0.2)) {
        point.x = testX;
        return true;
      }
    }
  }
  
  return false;
}


export function tryVerticalPlacement(point, placedPoints, centerX) {
  const step = 5;
  const maxYOffset = 150;
  const yOffsets = d3.range(step, maxYOffset + 1, step);
  const xOffsets = [0, 10, -10, 20, -20, 30, -30];
  
  for (const yOffset of yOffsets) {
    const yPositions = [yOffset, -yOffset];
    
    for (const yOff of yPositions) {
      for (const xOff of xOffsets) {
        const testX = centerX + xOff;
        const testY = point.y + yOff;
        
        const margin = 5;
        if (testX < margin || testX > (centerX * 2) - margin) continue;
        
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

export function placePoint(point, placedPoints, centerX, allPoints = null) {
  return tryHorizontalPlacement(point, placedPoints, centerX, allPoints) ||
         tryVerticalPlacement(point, placedPoints, centerX);
}

// Consistent date parsing
export function parseDate(dateStr) {
  if (!dateStr) return null;
  
  if (dateStr instanceof Date) {
    return dateStr;
  }
  
  if (typeof dateStr === 'number') {
    if (dateStr > 3000) {
      return new Date(dateStr > 1000000000000 ? dateStr : dateStr * 1000);
    } else {
      return new Date(dateStr, 0, 1);
    }
  }
  
  if (typeof dateStr !== 'string') {
    dateStr = String(dateStr);
  }
  
  if (dateStr.includes('-')) {
    return new Date(dateStr);
  } else {
    return new Date(parseInt(dateStr), 0, 1);
  }
}

// Get combined date range from both datasets
export function getCombinedDateRange(paperData, coauthorData, dateCol) {
  const allData = [];
  if (paperData && paperData.length > 0) {
    allData.push(...paperData);
  }
  if (coauthorData && coauthorData.length > 0) {
    allData.push(...coauthorData);
  }
  
  const allDates = allData.map(d => parseDate(d[dateCol]));
  const [minDate, maxDate] = d3.extent(allDates);
  
  const paddedMinDate = new Date(minDate.getFullYear() - 1, 0, 1);
  const paddedMaxDate = new Date(maxDate.getFullYear() + 1, 11, 31);
  
  return [paddedMinDate, paddedMaxDate];
}