import { SvelteURLSearchParams } from 'svelte/reactivity';

/**
 * Creates a reactive URL search params instance that syncs with the browser URL.
 * Automatically initializes with provided defaults if params are not present.
 *
 * @param {Object} defaults - Default values for URL parameters
 * @returns {SvelteURLSearchParams} Reactive URL search params instance
 *
 * @example
 * const params = createUrlState({
 *     mode: 'dates',
 *     country: 'United States'
 * });
 */
export function createUrlState(defaults = {}) {
    const params = new SvelteURLSearchParams(
        typeof window !== 'undefined' ? window.location.search : ''
    );

    // Initialize defaults for missing params
    for (const [key, value] of Object.entries(defaults)) {
        if (!params.has(key)) {
            params.set(key, String(value));
        }
    }

    // Sync params with browser URL
    $effect(() => {
        if (typeof window !== 'undefined') {
            const newSearch = '?' + params.toString();
            if (window.location.search !== newSearch) {
                window.history.replaceState(null, '', newSearch);
            }
        }
    });

    return params;
}
