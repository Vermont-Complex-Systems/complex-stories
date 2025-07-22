import * as d3 from 'd3';
import { placePointMultiPass, parseDate } from './combinedChartUtils'
import { getEffectiveChartDimensions } from './layout.js';

export function processCoauthorData(coauthorData, width, height, timeScale, radiusScale) {
  if (!coauthorData || coauthorData.length === 0) {
    return [];
  }

  const { width: effectiveWidth, centerX } = getEffectiveChartDimensions(width, height);


  const coauthorPoints = coauthorData.map(d => {
    const parsedDate = parseDate(d.pub_date);
    const targetY = timeScale(parsedDate);
    return createCoauthorPoint(d, targetY, radiusScale);
  });

  // Sort by radius (descending) to place larger points first
  coauthorPoints.sort((a, b) => d3.descending(a.r, b.r));

  const placedPoints = [];
  
  for (const point of coauthorPoints) {
    if (placePointMultiPass(point, placedPoints, centerX, effectiveWidth)) {
      placedPoints.push(point);
    } else {
      console.warn('Could not place coauthor point:', point.name);
      point.x = centerX;
      placedPoints.push(point);
    }
  }

  return placedPoints;
}

export function createCoauthorPoint(d, targetY, radiusScale) {
  const totalCollabs = +d.all_times_collabo || 1;
  const ageCategory = d.age_category || 'same';

  const radius = radiusScale ? radiusScale(d) : 5;

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
    shared_institutions: d.shared_institutions,
    collaboration_intensity: d.collaboration_intensity,
    institution_normalized: d.institution_normalized,
    coauth_institution_normalized: d.coauth_institution_normalized,
    shared_institutions_normalized: d.shared_institutions_normalized
  };
}