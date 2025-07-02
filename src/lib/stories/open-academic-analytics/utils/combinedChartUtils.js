import * as d3 from 'd3';

// Color scales
export const ageColorScale = d3.scaleOrdinal()
  .domain(['older', 'same', 'younger'])
  .range(['#8e6dfb', '#20A387FF', '#dacc55']);

export const acquaintanceColorScale = d3.scaleOrdinal()
  .domain(['new_collab', 'existing_collab'])
  .range(['#FF6B35', '#4682B4']);

export const collaborationColorScale = d3.scaleThreshold()
  .domain([2, 4, 9])
  .range(['#FF6B35', '#4682B4', '#2E8B57', '#1F4E79']);

export function processCoauthorData(coauthorData, width, height, timeScale) {
  if (!coauthorData || coauthorData.length === 0) {
    return [];
  }

  const MARGIN_LEFT = 40;
  const MARGIN_RIGHT = 40;
  const effectiveWidth = width - MARGIN_LEFT - MARGIN_RIGHT;
  const centerX = effectiveWidth / 2;
  
  // Get the actual collaboration range from your data
  const collaborationCounts = coauthorData.map(d => +d.all_times_collabo || 1);
  const [minCollabs, maxCollabs] = d3.extent(collaborationCounts);
  
  // Create a dynamic scale based on your actual data
  const collaborationScale = d3.scaleSqrt()
    .domain([minCollabs, maxCollabs])
    .range([2.5, 12]) // Reasonable min/max sizes for coauthors
    .clamp(true);

  const coauthorPoints = coauthorData.map(d => {
    const parsedDate = parseDate(d.pub_date);
    const targetY = timeScale(parsedDate);
    return createCoauthorPoint(d, targetY, collaborationScale); // Pass the scale
  });

  // Sort by collaboration count (descending) to place important points first
  coauthorPoints.sort((a, b) => d3.descending(+a.all_times_collabo || 0, +b.all_times_collabo || 0));

  const placedPoints = [];
  
  for (const point of coauthorPoints) {
    if (placePointMultiPass(point, placedPoints, centerX, effectiveWidth, coauthorPoints)) {
      placedPoints.push(point);
    } else {
      console.warn('Could not place coauthor point:', point.name);
      point.x = centerX;
      placedPoints.push(point);
    }
  }

  return coauthorPoints;
}

export function createCoauthorPoint(d, targetY, collaborationScale) {
  const ageDiff = +d.age_diff;
  const totalCollabs = +d.all_times_collabo || 1;
  const yearlyCollabs = +d.yearly_collabo || 1;
  
  // Determine age category
  let ageCategory = 'same';
  if (ageDiff > 7) {
    ageCategory = 'older';
  } else if (ageDiff < -7) {
    ageCategory = 'younger';
  }

  // Use the dynamic scale passed from processCoauthorData
  const radius = collaborationScale ? collaborationScale(totalCollabs) : 5; // Fallback if no scale

  return {
    x: 0,
    y: targetY,
    r: radius,
    type: 'coauthor',
    name: d.coauth_name,
    year: d.pub_year,
    date: d.pub_date,
    age_diff: d.age_diff,
    age_category: ageCategory,
    all_times_collabo: d.all_times_collabo,
    yearly_collabo: d.yearly_collabo,
    acquaintance: d.acquaintance,
    coauth_aid: d.coauth_aid,
    aid: d.aid,
    author_name: d.name,
    author_age: d.author_age,
    coauth_age: d.coauth_age,
    institution: d.institution,
    shared_institutions: d.shared_institutions // Add this field
  };
}

export function createPaperPoint(d, targetY, citationScale) {
  const citedBy = +d.cited_by_count || 0;
  const nbCoauthors = +d.nb_coauthors || 1;
  
  const color = "#888888"; // Grey for all papers
  
  // Use the dynamic scale passed from processPaperData
  const radius = citationScale ? citationScale(citedBy) : 5; // Fallback if no scale

  return {
    x: 0,
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
    authors: d.authors,
    ego_aid: d.ego_aid
  };
}

// Improved collision detection with better spacing
export function checkCollision(testX, testY, point, placedPoints, padding = 1) {
  for (const existing of placedPoints) {
    const dx = testX - existing.x;
    const dy = testY - existing.y;
    const distance = Math.sqrt(dx * dx + dy * dy);
    const minDistance = point.r + existing.r + padding; // Reduced padding
    
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
  const step = 2; // Smaller step for denser packing
  const offsets = d3.range(0, maxOffset + 1, step);
  
  for (const offset of offsets) {
    const positions = offset === 0 ? [0] : [offset, -offset];
    
    for (const xOffset of positions) {
      const testX = centerX + xOffset;
      const testY = point.y;
      
      // More permissive center line usage
      if (xOffset === 0 && allPoints && !canUseCenterLine(point, allPoints)) {
        continue;
      }
      
      if (testX < margin || testX > effectiveWidth - margin) continue;
      
      if (!checkCollision(testX, testY, point, placedPoints, 0.5)) { // Tighter collision
        point.x = testX;
        return true;
      }
    }
  }
  return false;
}

// Much more permissive center line usage
export function canUseCenterLine(point, allPoints) {
  const currentRank = allPoints.indexOf(point);
  const totalPoints = allPoints.length;
  // Allow 60% of points on center line, prioritize larger points
  return currentRank < totalPoints * 0.6 || point.r > 4;
}

// Add a multi-pass placement strategy
export function placePointMultiPass(point, placedPoints, centerX, effectiveWidth, allPoints = null) {
  // First pass: try horizontal placement with tight collision
  if (tryHorizontalPlacement(point, placedPoints, centerX, effectiveWidth, allPoints)) {
    return true;
  }
  
  // Second pass: try vertical placement
  if (tryVerticalPlacement(point, placedPoints, centerX, effectiveWidth)) {
    return true;
  }
  
  // Third pass: try horizontal with looser collision
  const step = 1;
  const maxOffset = Math.min(centerX - 5, effectiveWidth - centerX - 5);
  const offsets = d3.range(0, maxOffset + 1, step);
  
  for (const offset of offsets) {
    const positions = offset === 0 ? [0] : [offset, -offset];
    
    for (const xOffset of positions) {
      const testX = centerX + xOffset;
      const testY = point.y;
      
      if (testX < 5 || testX > effectiveWidth - 5) continue;
      
      if (!checkCollision(testX, testY, point, placedPoints, 0.2)) { // Very tight collision
        point.x = testX;
        return true;
      }
    }
  }
  
  return false;
}

// Update the main processing functions to use the new placement
export function processPaperData(paperData, width, height, timeScale) {
  if (!paperData || paperData.length === 0) {
    return [];
  }

  const MARGIN_LEFT = 40;
  const MARGIN_RIGHT = 40;
  const effectiveWidth = width - MARGIN_LEFT - MARGIN_RIGHT;
  const centerX = effectiveWidth / 2;

  // Get the actual citation range from your data
  const citationCounts = paperData.map(d => +d.cited_by_count || 0);
  const [minCitations, maxCitations] = d3.extent(citationCounts);
  
  // Create a dynamic scale based on your actual data
  const citationScale = d3.scaleSqrt()
    .domain([minCitations, maxCitations])
    .range([2, 18]) // Reasonable min/max sizes
    .clamp(true);

  const paperPoints = paperData.map(d => {
    const parsedDate = parseDate(d.pub_date);
    const targetY = timeScale(parsedDate);
    return createPaperPoint(d, targetY, citationScale); // Pass the scale
  });

  // Sort by citation count (descending) to place important points first
  paperPoints.sort((a, b) => d3.descending(+a.cited_by_count || 0, +b.cited_by_count || 0));

  const placedPoints = [];
  
  for (const point of paperPoints) {
    if (placePointMultiPass(point, placedPoints, centerX, effectiveWidth)) {
      placedPoints.push(point);
    } else {
      console.warn('Could not place paper point:', point.title);
      point.x = centerX;
      placedPoints.push(point);
    }
  }

  return paperPoints;
}

// Also update vertical placement to use more space
export function tryVerticalPlacement(point, placedPoints, centerX) {
  const step = 5;
  const maxYOffset = 150; // Increased from 100
  const yOffsets = d3.range(step, maxYOffset + 1, step);
  const xOffsets = [0, 10, -10, 20, -20, 30, -30]; // Added more x offsets
  
  for (const yOffset of yOffsets) {
    const yPositions = [yOffset, -yOffset];
    
    for (const yOff of yPositions) {
      for (const xOff of xOffsets) {
        const testX = centerX + xOff;
        const testY = point.y + yOff;
        
        // Use smaller margins here too
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
  
  // Handle Date objects
  if (dateStr instanceof Date) {
    console.log('📅 parseDate: Date object → returning as-is');
    return dateStr;
  }
  
  // Handle numbers (shouldn't happen anymore, but just in case)
  if (typeof dateStr === 'number') {
    console.log('📅 parseDate: number → converting to Date');
    if (dateStr > 3000) {
      return new Date(dateStr > 1000000000000 ? dateStr : dateStr * 1000);
    } else {
      return new Date(dateStr, 0, 1);
    }
  }
  
  // Convert to string if needed
  if (typeof dateStr !== 'string') {
    console.warn('⚠️ parseDate: non-string value, converting:', typeof dateStr, dateStr);
    dateStr = String(dateStr);
  }
  
  // All dates should now be in YYYY-MM-DD format
  if (dateStr.includes('-')) {
    console.log('📅 parseDate: string with dash → new Date');
    return new Date(dateStr);
  } else {
    console.log('📅 parseDate: fallback to year-only');
    return new Date(parseInt(dateStr), 0, 1);
  }
}

// Get combined date range from both datasets
export function getCombinedDateRange(paperData, coauthorData) {
  const allData = [];
  if (paperData && paperData.length > 0) {
    allData.push(...paperData);
  }
  if (coauthorData && coauthorData.length > 0) {
    allData.push(...coauthorData);
  }
  
  if (allData.length === 0) {
    return [new Date('1990-01-01'), new Date('2025-12-31')];
  }
  
  const allDates = allData.map(d => parseDate(d.pub_date));
  const [minDate, maxDate] = d3.extent(allDates);
  
  // Add padding to the range
  const paddedMinDate = new Date(minDate.getFullYear() - 1, 0, 1);
  const paddedMaxDate = new Date(maxDate.getFullYear() + 1, 11, 31);
  
  return [paddedMinDate, paddedMaxDate];
}