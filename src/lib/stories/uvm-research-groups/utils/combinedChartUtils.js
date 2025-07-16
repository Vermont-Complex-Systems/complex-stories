import * as d3 from 'd3';

export function createCoauthorPoint(d, targetY) {
  const ageDiff = +d.age_diff;
  
  // Use D3 color scale for age differences
  const ageColorScale = d3.scaleOrdinal()
    .domain(['older', 'same', 'younger'])
    .range(['#404788FF', '#20A387FF', '#FDE725FF']);
  
  let color = ageColorScale('same'); // Default same age
  if (ageDiff > 7) {
    color = ageColorScale('older');
  } else if (ageDiff < -7) {
    color = ageColorScale('younger');
  }

  // Use D3 scale for radius based on collaborations
  const radiusScale = d3.scaleSqrt()
    .domain([1, 20]) // Typical collaboration range
    .range([3, 9]); // Min and max radius
  
  const radius = radiusScale(+d.all_times_collabo || 1);

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
  
  const color = "#888888"; // Grey for all papers

  // Use D3 scale for paper radius based on citations
  const citationScale = d3.scaleSqrt()
    .domain([0, 1000]) // Typical citation range
    .range([3, 15])    // Min and max radius
    .clamp(true);      // Clamp to max radius
  
  const radius = citationScale(citedBy);

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
  // Use D3 range for cleaner step generation
  const maxOffset = 150;
  const step = 5;
  const offsets = d3.range(0, maxOffset + 1, step);
  
  for (const offset of offsets) {
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
  const maxYOffset = 100;
  const yOffsets = d3.range(step, maxYOffset + 1, step);
  const xOffsets = [0, 10, -10, 20, -20];
  
  for (const yOffset of yOffsets) {
    const yPositions = [yOffset, -yOffset];
    
    for (const yOff of yPositions) {
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
  // Use D3 range for fallback positioning
  const yOffsets = d3.range(105, 201, 10);
  
  for (const yOffset of yOffsets) {
    const yPositions = [yOffset, -yOffset];
    
    for (const yOff of yPositions) {
      // Use D3 random for horizontal placement
      const randomScale = d3.scaleLinear()
        .domain([0, 1])
        .range([-50, 50]);
      
      const testX = centerX + randomScale(Math.random());
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

export function processCombinedDataPoints(coauthorData, paperData, width, height, timeScale) {
  if ((!coauthorData || coauthorData.length === 0) && (!paperData || paperData.length === 0)) {
    return [];
  }

  const xScale = d3.scaleLinear()
    .domain([0, 1])
    .range([0, width]);
  
  const leftCenterX = xScale(0.25);  // Coauthors on left quarter
  const rightCenterX = xScale(0.6);  // Papers closer to center

  const parseDate = (dateStr) => {
    // Handle both YYYY-MM-DD and YYYY formats
    if (dateStr.includes('-')) {
      return new Date(dateStr);
    } else {
      return new Date(parseInt(dateStr), 0, 1); // January 1st of the year
    }
  };

  // Combine all data and parse dates consistently
  const allData = [];
  if (coauthorData) {
    allData.push(...coauthorData.map(d => ({...d, parsedDate: parseDate(d.pub_date), type: 'coauthor'})));
  }
  if (paperData) {
    allData.push(...paperData.map(d => ({...d, parsedDate: parseDate(d.pub_date), type: 'paper'})));
  }

  const coauthorPoints = [];
  const paperPoints = [];
  
  // Process each data point
  for (const d of allData) {
    const targetY = timeScale(d.parsedDate);
    
    if (d.type === 'coauthor') {
      coauthorPoints.push(createCoauthorPoint(d, targetY));
    } else {
      paperPoints.push(createPaperPoint(d, targetY));
    }
  }

  // Sort by importance
  coauthorPoints.sort((a, b) => d3.descending(+a.collabs || 0, +b.collabs || 0));
  paperPoints.sort((a, b) => d3.descending(+a.cited_by_count || 0, +b.cited_by_count || 0));

  const placedPoints = [];
  
  // Place coauthor points
  for (const point of coauthorPoints) {
    if (placePoint(point, placedPoints, leftCenterX, coauthorPoints)) {
      placedPoints.push(point);
    } else {
      console.warn('Could not place coauthor point:', point.name);
      point.x = leftCenterX;
      placedPoints.push(point);
    }
  }
  
  // Place paper points
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

// FIXED: Simplified date range calculation
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
    return [new Date('1999-01-01'), new Date('2025-12-31')];
  }
  
  // Consistent date parsing
  const parseDate = (dateStr) => {
    if (dateStr.includes('-')) {
      return new Date(dateStr);
    } else {
      return new Date(parseInt(dateStr), 0, 1);
    }
  };
  
  // Use D3 extent for clean min/max calculation
  const allDates = allData.map(d => parseDate(d.pub_date));
  const [minDate, maxDate] = d3.extent(allDates);
  
  // Add some padding to the range
  const paddedMinDate = new Date(minDate.getFullYear() - 1, 0, 1);
  const paddedMaxDate = new Date(maxDate.getFullYear() + 1, 11, 31);
  
  return [paddedMinDate, paddedMaxDate];
}