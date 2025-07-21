import * as d3 from 'd3';
import { placePointMultiPass, parseDate } from './combinedChartUtils'
import { getEffectiveChartDimensions } from './layout.js';

// paperUtils.js
export function processPaperData(paperData, width, height, timeScale, radiusScale) {
  if (!paperData || paperData.length === 0) {
    return [];
  }

  const { width: effectiveWidth, centerX } = getEffectiveChartDimensions(width, height);

  const paperPoints = paperData.map(d => {
    const parsedDate = parseDate(d.pub_date);
    const targetY = timeScale(parsedDate);
    return createPaperPoint(d, targetY, radiusScale);
  });

  // Sort by radius (descending) to place larger points first
  paperPoints.sort((a, b) => d3.descending(a.r, b.r));

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

  return placedPoints;
}

export function createPaperPoint(d, targetY, radiusScale) {
  const citedBy = +d.cited_by_count || 0;
  const nbCoauthors = +d.nb_coauthors || 1;
  
  const color = "#888888";
  
  // Let the scale function determine the radius
  const radius = radiusScale ? radiusScale(d) : 5;

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
    ego_aid: d.ego_aid,
    citation_percentile: d.citation_percentile,
    citation_category: d.citation_category
  };
}