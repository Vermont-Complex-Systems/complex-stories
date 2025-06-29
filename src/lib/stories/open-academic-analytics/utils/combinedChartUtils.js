import * as d3 from 'd3';

// Color scales
export const ageColorScale = d3.scaleOrdinal()
  .domain(['older', 'same', 'younger'])
  .range(['#404788FF', '#20A387FF', '#FDE725FF']);

export const acquaintanceColorScale = d3.scaleOrdinal()
  .domain(['new_collab', 'repeat_collab', 'long_term_collab'])
  .range(['#FF6B35', '#4682B4', '#2E8B57']);

// New collaboration-based color scale
export const collaborationColorScale = d3.scaleThreshold()
  .domain([2, 4, 9])  // 0-1: new, 2-3: repeat, 4+: long-term
  .range(['#FF6B35', '#4682B4', '#2E8B57', '#1F4E79']); // red, blue, green, dark blue

// Paper point creation
export function createPaperPoint(d, targetY) {
  const citedBy = +d.cited_by_count || 0;
  const nbCoauthors = +d.nb_coauthors || 1;
  
  const color = "#888888"; // Grey for all papers

  const citationScale = d3.scaleSqrt()
    .domain([0, 1000])
    .range([3, 15])
    .clamp(true);
  
  const radius = citationScale(citedBy);

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

// Coauthor point creation
export function createCoauthorPoint(d, targetY) {
  const ageDiff = +d.age_diff;
  const totalCollabs = +d.all_times_collabo || 1;
  
  // Determine age category
  let ageCategory = 'same';
  if (ageDiff > 7) {
    ageCategory = 'older';
  } else if (ageDiff < -7) {
    ageCategory = 'younger';
  }

  const radiusScale = d3.scaleSqrt()
    .domain([1, 20])
    .range([3, 12]);
  
  const radius = radiusScale(totalCollabs);

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
    institution: d.institution
  };
}

// Shared collision detection
export function checkCollision(testX, testY, point, placedPoints, padding = 2) {
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

// Shared placement logic
export function tryHorizontalPlacement(point, placedPoints, centerX, allPoints = null) {
  // Use more of the available width - reduce margins from 20px to 5px
  const margin = 5;
  const maxOffset = centerX - margin;
  const step = 4;
  const offsets = d3.range(0, maxOffset + 1, step);
  
  for (const offset of offsets) {
    const positions = offset === 0 ? [0] : [offset, -offset];
    
    for (const xOffset of positions) {
      const testX = centerX + xOffset;
      const testY = point.y;
      
      // Be more permissive with center line usage
      if (xOffset === 0 && allPoints && !canUseCenterLine(point, allPoints)) {
        continue;
      }
      
      // Use smaller margins to allow more space
      if (testX < margin || testX > (centerX * 2) - margin) continue;
      
      if (!checkCollision(testX, testY, point, placedPoints)) {
        point.x = testX;
        return true;
      }
    }
  }
  return false;
}

// Make center line usage more permissive
export function canUseCenterLine(point, allPoints) {
  const currentRank = allPoints.indexOf(point);
  const totalPoints = allPoints.length;
  // Increase from 20% to 40% of points allowed on center line
  return currentRank < totalPoints * 0.4 || point.r > 6; // Also lowered radius threshold
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
// In combinedChartUtils.js
export function parseDate(dateStr) {
  // DETAILED DEBUG - catch what's breaking
  console.log('🔍 parseDate called with:', {
    value: dateStr,
    type: typeof dateStr,
    isNull: dateStr === null,
    isUndefined: dateStr === undefined,
    constructor: dateStr?.constructor?.name,
    stackTrace: new Error().stack.split('\n').slice(1, 4) // Show where it was called from
  });
  
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

// Process paper data
export function processPaperData(paperData, width, height, timeScale) {
  if (!paperData || paperData.length === 0) {
    return [];
  }

  const centerX = width / 2;
  
  const paperPoints = paperData.map(d => {
    const parsedDate = parseDate(d.pub_date);
    const targetY = timeScale(parsedDate);
    return createPaperPoint(d, targetY);
  });

  paperPoints.sort((a, b) => d3.descending(+a.cited_by_count || 0, +b.cited_by_count || 0));

  const placedPoints = [];
  
  for (const point of paperPoints) {
    if (placePoint(point, placedPoints, centerX)) {
      placedPoints.push(point);
    } else {
      console.warn('Could not place paper point:', point.title);
      point.x = centerX;
      placedPoints.push(point);
    }
  }

  return paperPoints;
}

// Process coauthor data
export function processCoauthorData(coauthorData, width, height, timeScale) {
  if (!coauthorData || coauthorData.length === 0) {
    return [];
  }

  const centerX = width / 2;
  
  const coauthorPoints = coauthorData.map(d => {
    const parsedDate = parseDate(d.pub_date);
    const targetY = timeScale(parsedDate);
    return createCoauthorPoint(d, targetY);
  });

  coauthorPoints.sort((a, b) => d3.descending(+a.all_times_collabo || 0, +b.all_times_collabo || 0));

  const placedPoints = [];
  
  for (const point of coauthorPoints) {
    if (placePoint(point, placedPoints, centerX, coauthorPoints)) {
      placedPoints.push(point);
    } else {
      console.warn('Could not place coauthor point:', point.name);
      point.x = centerX;
      placedPoints.push(point);
    }
  }

  return coauthorPoints;
}

// Color helper for coauthors
export function getCoauthorColor(point, colorMode) {
  if (colorMode === 'age_diff') {
    return ageColorScale(point.age_category);
  } else if (colorMode === 'acquaintance') {
    // Use collaboration count instead of acquaintance string
    const collabCount = +point.all_times_collabo || 0;
    return collaborationColorScale(collabCount);
  }
  return '#20A387FF';
}