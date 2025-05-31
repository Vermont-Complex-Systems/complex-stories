export function createCoauthorPoint(d, targetY) {
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
    type: 'coauthor',
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

export function createPaperPoint(d, targetY) {
  const citedBy = +d.cited_by_count || 0;
  const nbCoauthors = +d.nb_coauthors || 1;
  
  // Just grey for papers - much simpler
  const color = "#888888"; // Grey for all papers

  // Size based on citations with a maximum cap
  const baseRadius = Math.sqrt(citedBy + 1) * 1.2 + 2;
  const radius = Math.min(baseRadius, 10); // Cap at 15px radius

  return {
    x: 0, // Will be set during placement
    y: targetY,
    r: radius,
    color: color,
    type: 'paper',
    title: d.title,
    year: d.pub_year,
    date: d.pub_date,
    cited_by_count: citedBy,
    nb_coauthors: nbCoauthors,
    work_type: d.work_type,
    doi: d.doi,
    authors: d.authors
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

export function canUseCenterLine(point, allPointsOfType) {
  const currentRank = allPointsOfType.indexOf(point);
  const totalPoints = allPointsOfType.length;
  return currentRank < totalPoints * 0.2 || point.r > 8;
}

export function tryHorizontalPlacement(point, placedPoints, centerX, allPointsOfType) {
  const maxOffset = 150; // Smaller since we have half the space
  const step = 5;
  
  for (let offset = 0; offset <= maxOffset; offset += step) {
    const positions = offset === 0 ? [0] : [offset, -offset];
    
    for (const xOffset of positions) {
      const testX = centerX + xOffset;
      const testY = point.y;
      
      // Check center restrictions
      if (xOffset === 0 && !canUseCenterLine(point, allPointsOfType)) {
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

export function placePoint(point, placedPoints, centerX, allPointsOfType) {
  return tryHorizontalPlacement(point, placedPoints, centerX, allPointsOfType) ||
         tryVerticalPlacement(point, placedPoints, centerX) ||
         tryFinalFallback(point, placedPoints, centerX);
}

export function processCombinedDataPoints(coauthorData, paperData, width, height) {
  if ((!coauthorData || coauthorData.length === 0) && (!paperData || paperData.length === 0)) {
    return [];
  }

  // Constants
  const margin = 80;
  const chartHeight = height - 2 * margin;
  
  // Define center lines - papers closer to the divider
  const leftCenterX = width * 0.25; // Coauthors on left quarter
  const rightCenterX = width * 0.6;  // Papers closer to center

  // Get the actual date range from ALL data and extend the max year (like the working version)
  const allDates = [];
  if (coauthorData) allDates.push(...coauthorData.map(d => new Date(d.pub_date)));
  if (paperData) allDates.push(...paperData.map(d => new Date(d.pub_date)));
  
  const minDate = new Date(Math.min(...allDates));
  const actualMaxDate = new Date(Math.max(...allDates));
  
  // Extend max year by 2 years for visual breathing room (exactly like working version)
  const maxDate = new Date(actualMaxDate.getFullYear() + 2, 11, 31);

  // Group by exact publication date for natural jiggling
  const byDate = new Map();
  
  // Add coauthor data
  if (coauthorData) {
    coauthorData.forEach(d => {
      const dateKey = d.pub_date;
      if (!byDate.has(dateKey)) byDate.set(dateKey, []);
      byDate.get(dateKey).push({ ...d, dataType: 'coauthor' });
    });
  }
  
  // Add paper data
  if (paperData) {
    paperData.forEach(d => {
      const dateKey = d.pub_date;
      if (!byDate.has(dateKey)) byDate.set(dateKey, []);
      byDate.get(dateKey).push({ ...d, dataType: 'paper' });
    });
  }

  // Create ALL points first with their target Y positions based on exact dates (exactly like working version)
  const coauthorPoints = [];
  const paperPoints = [];
  
  for (const [dateKey, dateData] of byDate) {
    const pubDate = new Date(dateKey);
    const dateProgress = (pubDate - minDate) / (maxDate - minDate);
    const targetY = margin + dateProgress * chartHeight;
    
    for (const d of dateData) {
      if (d.dataType === 'coauthor') {
        coauthorPoints.push(createCoauthorPoint(d, targetY));
      } else {
        paperPoints.push(createPaperPoint(d, targetY));
      }
    }
  }

  // Sort each type separately
  coauthorPoints.sort((a, b) => b.collabs - a.collabs);
  paperPoints.sort((a, b) => b.cited_by_count - a.cited_by_count);

  // Place points separately for each type
  const placedPoints = [];
  
  // Place coauthor points on the left
  for (const point of coauthorPoints) {
    if (placePoint(point, placedPoints, leftCenterX, coauthorPoints)) {
      placedPoints.push(point);
    } else {
      console.warn('Could not place coauthor point:', point.name);
      point.x = leftCenterX;
      placedPoints.push(point);
    }
  }
  
  // Place paper points on the right (closer to center)
  for (const point of paperPoints) {
    if (placePoint(point, placedPoints, rightCenterX, paperPoints)) {
      placedPoints.push(point);
    } else {
      console.warn('Could not place paper point:', point.title);
      point.x = rightCenterX;
      placedPoints.push(point);
    }
  }

  return [...coauthorPoints, ...paperPoints];
}

// Helper function to get the date range for grid alignment (exactly like working version)
export function getCombinedDataDateRange(coauthorData, paperData) {
  // Combine all data first
  const allData = [];
  if (coauthorData && coauthorData.length > 0) {
    allData.push(...coauthorData);
  }
  if (paperData && paperData.length > 0) {
    allData.push(...paperData);
  }
  
  if (allData.length === 0) {
    return [new Date('1999-01-01'), new Date('2027-12-31')];
  }
  
  // Use the exact same logic as the working single version
  const allDates = allData.map(d => new Date(d.pub_date));
  const minDate = new Date(Math.min(...allDates));
  const actualMaxDate = new Date(Math.max(...allDates));
  
  // Extend max year by 2 years to match the processDataPoints function (exactly like working version)
  const maxDate = new Date(actualMaxDate.getFullYear() + 2, 11, 31);
  
  return [minDate, maxDate];
}