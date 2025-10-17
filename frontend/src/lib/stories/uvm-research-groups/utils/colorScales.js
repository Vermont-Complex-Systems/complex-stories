import * as d3 from 'd3';

export const ageColorScale = d3.scaleOrdinal()
  .domain(['older', 'same', 'younger'])
  .range(['#404788FF', '#20A387FF', '#FDE725FF']);

export const institutionColorScale = d3.scaleOrdinal()
  .domain([
    'University of Vermont',
    'Massachusetts Institute of Technology', 
    'Earth Island Institute',
    'Columbia University',
    'Santa Fe Institute'
  ])
  .range(['#2E8B57', '#FF6B35', '#4682B4', '#4682B4', '#B59410']);

export function getPointColor(point, colorMode) {
  if (point.type === 'paper') return "#888888";
  
  if (colorMode === 'shared_institutions' && point.type === 'coauthor') {
    const sharedInst = point.shared_institutions || 'None';
    if (sharedInst === 'None' || sharedInst === '') return "#D3D3D3";
    
    for (const institution of institutionColorScale.domain()) {
      if (sharedInst.includes(institution)) {
        return institutionColorScale(institution);
      }
    }
    return "#4682B4";
  } else if (colorMode === 'age_diff' && point.type === 'coauthor') {
    const ageDiff = +point.age_diff;
    if (ageDiff > 7) return ageColorScale('older');
    if (ageDiff < -7) return ageColorScale('younger');
    return ageColorScale('same');
  }
  return point.color;
}