// src/lib/constants/layout.js
// Pure constants and calculation helpers - NO reactive dependencies

// ========================================
// BREAKPOINTS
// ========================================
export const breakpoints = {
  mobile: 768,
  tablet: 1024,
  desktop: 1200,
  wide: 1600
};

// ========================================
// SIDEBAR DIMENSIONS
// ========================================
export const sidebar = {
  expanded: 272,      // 17rem
  collapsed: 80,      // 5rem
  mobileHeight: 80    // When collapsed on mobile
};

// ========================================
// SPACING & PADDING
// ========================================
export const spacing = {
  // Main layout spacing
  mainContentPadding: 88,    // 5.5rem left padding
  dashboardPadding: 20,      // Dashboard container padding
  chartsGridGap: 20,         // Gap between chart panels
  chartPanelPadding: 20,     // Padding inside chart panels
  
  // Chart margins
  chartMarginTop: 50,
  chartMarginBottom: 50,
  chartMarginLeft: 40,
  chartMarginRight: 40,
  
  // Component spacing
  sidebarPadding: 24,        // 1.5rem
  legendGap: 8,
  accordionGap: 32           // 2rem
};

// ========================================
// CHART DIMENSIONS
// ========================================
export const charts = {
  // Width constraints
  minWidth: 400,
  maxWidth: 700,
  
  // Height calculation thresholds
  heightThresholds: {
    small: 600,
    medium: 1500
  },
  
  heights: {
    small: 800,
    medium: 1200,
    large: 2200
  },
  
};

// ========================================
// PURE HELPER FUNCTIONS (NO REACTIVE DEPENDENCIES)
// ========================================

/**
 * Calculate sidebar width based on collapsed state
 */
export function getSidebarWidth(isCollapsed) {
  return isCollapsed ? sidebar.collapsed : sidebar.expanded;
}

/**
 * Calculate available width for charts
 * Pure function - pass in reactive values from outside
 */
export function calculateChartWidth(screenWidth, isSidebarCollapsed) {
  if (!screenWidth) return charts.minWidth; // SSR fallback
  
  const sidebarWidth = getSidebarWidth(isSidebarCollapsed);
  const availableForChartsContainer = screenWidth 
    - sidebarWidth 
    - spacing.mainContentPadding 
    - spacing.dashboardPadding;
  
  const availablePerChart = (availableForChartsContainer - spacing.chartsGridGap) / 2 
    - spacing.chartPanelPadding;
  
  return Math.max(charts.minWidth, Math.min(charts.maxWidth, availablePerChart));
}

/**
 * Calculate chart height based on data size
 */
export function calculateChartHeight(dataLength) {
  if (!dataLength) return charts.heights.small;
  
  if (dataLength > charts.heightThresholds.small) {
    return dataLength < charts.heightThresholds.medium 
      ? charts.heights.medium 
      : charts.heights.large;
  }
  
  return charts.heights.small;
}

/**
 * Get chart margins as an object
 */
export function getChartMargins() {
  return {
    top: spacing.chartMarginTop,
    bottom: spacing.chartMarginBottom,
    left: spacing.chartMarginLeft,
    right: spacing.chartMarginRight
  };
}

/**
 * Calculate effective chart dimensions (minus margins)
 */
export function getEffectiveChartDimensions(width, height) {
  const margins = getChartMargins();
  return {
    width: width - margins.left - margins.right,
    height: height - margins.top - margins.bottom,
    centerX: (width - margins.left - margins.right) / 2
  };
}

/**
 * Get overlay position based on screen size
 */
export function getOverlayPosition(screenWidth, overlayType = 'legend') {
  if (!screenWidth) return overlays[overlayType].desktop; // SSR fallback
  
  if (screenWidth <= breakpoints.mobile) {
    return overlays[overlayType].mobile;
  } else if (screenWidth <= breakpoints.tablet) {
    return overlays[overlayType].tablet;
  }
  return overlays[overlayType].desktop;
}