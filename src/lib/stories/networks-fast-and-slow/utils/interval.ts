export type IntervalHandle = ReturnType<typeof setInterval> | null;

/**
 * Starts an interval that calls `fn` every `delay` ms.
 * Returns a stop function that clears the interval.
 */
export function createInterval(fn: () => void, delay: number): () => void {
	let handle: IntervalHandle = setInterval(fn, delay);

	return () => {
		if (handle !== null) {
			clearInterval(handle);
			handle = null;
		}
	};
}
