// src/lib/constants/colorScales.js
import * as d3 from 'd3';

// Age-based color scale for coauthor relationships
export const ageColorScale = d3.scaleOrdinal()
  .domain(['older', 'same', 'younger', null])
  .range(['#8e6dfb', '#20A387FF', '#dacc55', 'lightgrey']);

// Acquaintance/collaboration count color scale
export const acquaintanceColorScale = d3.scaleThreshold()
  .domain([2, 5]) // 1, 2-4, 5+
  .range(['#35B779FF', '#5694c0ff', '#7a0796ff']); // Few -> Some -> Many

// Institution-based color scale (dynamic, so we export a factory function)
export function createInstitutionColorScale(institutions) {
  return d3.scaleOrdinal(d3.schemeTableau10).domain(institutions);
}

// Shared institutions color scale (dynamic, so we export a factory function)
export function createSharedInstitutionColorScale(sharedInstitutions) {
  return d3.scaleOrdinal(d3.schemeTableau10).domain(sharedInstitutions);
}

// Color constants for easy access
export const colorConstants = {
  age: {
    older: '#8e6dfb',
    same: '#20A387FF', 
    younger: '#dacc55'
  },
  acquaintance: {
    few: '#35B779FF',
    some: '#31688EFF',
    many: '#440154FF'
  },
  fallback: '#d9d9d9ff',
  null: '#dcdcdcff'
};

// Helper function to get color for age category
export function getAgeColor(ageCategory) {
  return ageColorScale(ageCategory) || colorConstants.fallback;
}

// Helper function to get color for collaboration count
export function getAcquaintanceColor(collaborationCount) {
  return acquaintanceColorScale(collaborationCount) || colorConstants.fallback;
}