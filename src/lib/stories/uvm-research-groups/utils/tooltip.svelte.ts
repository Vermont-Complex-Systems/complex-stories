// Tooltip state management
export function createTooltipState() {
  let showTooltip = $state(false);
  let tooltipContent = $state('');
  let mouseX = $state(0);
  let mouseY = $state(0);

  function showPointTooltip(event: MouseEvent, point: any) {
    mouseX = event.clientX;
    mouseY = event.clientY;
    
    if (point.type === 'paper') {
      tooltipContent = `${point.title}\nYear: ${point.year}\nCitations: ${point.cited_by_count}\nCoauthors: ${point.nb_coauthors}`;
    } else {
      tooltipContent = `${point.coauthor_display_name}\nYear: ${point.year}\nAge difference: ${point.age_diff} years\nCollaborations: ${point.collabs}`;
    }
    
    showTooltip = true;
  }

  function hideTooltip() {
    showTooltip = false;
  }

  return {
    get showTooltip() { return showTooltip; },
    get tooltipContent() { return tooltipContent; },
    get mouseX() { return mouseX; },
    get mouseY() { return mouseY; },
    showPointTooltip,
    hideTooltip
  };
}