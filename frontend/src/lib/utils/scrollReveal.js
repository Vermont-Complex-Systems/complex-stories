import { browser } from '$app/environment';

/**
 * Svelte action for scroll-based reveal animations using Intersection Observer.
 *
 * Usage:
 * ```svelte
 * <section use:scrollReveal>Content</section>
 * ```
 *
 * CSS (add to your component):
 * ```css
 * @media (prefers-reduced-motion: no-preference) {
 *   :global(section[data-animate="true"]) {
 *     opacity: 0;
 *     transition: opacity 0.5s ease-out;
 *   }
 *   :global(section[data-animate="true"][data-revealed="true"]) {
 *     opacity: 1;
 *   }
 * }
 * ```
 *
 * @param {HTMLElement} node - The DOM element to observe
 * @param {Object} options - Configuration options
 * @param {number} options.threshold - Intersection ratio threshold (0-1)
 * @param {string} options.rootMargin - Root margin for observer
 * @returns {Object} Svelte action object with destroy method
 */
export function scrollReveal(node, options = {}) {
	const {
		threshold = 0.1,
		rootMargin = '0px 0px -100px 0px'
	} = options;

	// Use data attribute instead of class for scoping
	node.dataset.animate = 'true';

	// SSR: reveal immediately
	if (!browser) {
		node.dataset.revealed = 'true';
		return;
	}

	const observer = new IntersectionObserver(
		(entries) => {
			entries.forEach((entry) => {
				// Only reveal when element is entering viewport
				if (entry.isIntersecting && entry.intersectionRatio > threshold) {
					entry.target.dataset.revealed = 'true';
				}
			});
		},
		{
			threshold,
			rootMargin
		}
	);

	observer.observe(node);

	return {
		destroy() {
			observer.disconnect();
		}
	};
}
