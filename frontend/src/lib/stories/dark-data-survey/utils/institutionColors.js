/**
 * Institution color mapping for consistent visualization across components
 * Color logic: Green (intimate), Blue (professional peers), Purple (semi-institutional/educational),
 * Orange/Red (institutions with sensitive data), Amber (commercial), Gray (strangers)
 */

export const institutionColorMap = {
    // Green: Intimate/close relationships
    'TP_Friend': '#10b981',
    'TP_Relative': '#059669',
    'TP_Neighbor': '#22c55e',
    'TP_Acquaintance': '#34d399',

    // Blue: Professional peers
    'TP_Co_worker': '#06b6d4',

    // Purple: Semi-institutional (Educational, Employer, Researcher, Non-Profits)
    'TP_School': '#a855f7',
    'TP_Employer': '#7c3aed',
    'TP_Researcher': '#9333ea',
    'TP_NonProf': '#8b5cf6',

    // Orange/Red: Institutions handling sensitive data
    'TP_Platform': '#ea580c',
    'TP_Gov': '#ef4444',
    'TP_Police': '#dc2626',
    'TP_Financial': '#f97316',
    'TP_Medical': '#f87171',

    // Amber: Commercial entities
    'TP_Company_cust': '#f59e0b',
    'TP_Company_notcust': '#d97706',

    // Gray: Strangers/unknown
    'TP_Stranger': '#6b7280'
};

/**
 * Get color for an institution
 * @param {string} institution - Institution name (e.g., 'TP_Friend')
 * @returns {string} Hex color code
 */
export function getInstitutionColor(institution) {
    return institutionColorMap[institution] || '#6b7280'; // Default to gray
}
