/**
 * Load and process curated papers for interdisciplinarity annotation
 */

import paperIds from './top_cited_papers_comp_networks.csv'

/**
 * Get unique paper IDs from the CSV
 * The CSV has duplicates (one row per author/citation), so we deduplicate
 */
export function getUniquePaperIds() {
	const uniqueIds = new Set()

	// paperIds is an array of objects with oa_wid field
	for (const row of paperIds) {
		if (row.oa_wid && row.oa_wid.trim() !== '') {
			uniqueIds.add(row.oa_wid.trim())
		}
	}

	return Array.from(uniqueIds)
}

/**
 * Get a subset of paper IDs (for batching or limiting)
 */
export function getPaperIdsBatch(start = 0, limit = 20) {
	const uniqueIds = getUniquePaperIds()
	return uniqueIds.slice(start, start + limit)
}

/**
 * Get total number of unique papers
 */
export function getTotalPapers() {
	return getUniquePaperIds().length
}
