import { runCorrelationStats, computeAvgJaccardSimilarity } from './correlation';
import type { Node, Link } from '$lib/types';

// Helper for generating unique random node pairs
function* randomPairs(nodes: Node[], count: number) {
	const ids = nodes.map(n => n.id);
	const seen = new Set();
	while (seen.size < count) {
		const [a, b] = sampleTwo(ids);
		const key = a < b ? `${a}-${b}` : `${b}-${a}`;
		if (!seen.has(key)) {
			seen.add(key);
			yield [a, b];
		}
	}
}

function sampleTwo(arr: string[]): [string, string] {
	let i = Math.floor(Math.random() * arr.length);
	let j;
	do {
		j = Math.floor(Math.random() * arr.length);
	} while (i === j);
	return [arr[i], arr[j]];
}

self.onmessage = (event: MessageEvent) => {
	const {
		nodes,
		initialNodes,
		manyLinks,
		sourceNodeId,
		targetNodeId,
		r,
		s,
		sValues,
		maxSteps,
		trials,
		mode = 'single',
		numPairs = 20
	} = event.data;

	if (mode === 'sweep') {
		const structuralSimilarity = computeAvgJaccardSimilarity(
			manyLinks,
			sourceNodeId,
			targetNodeId
		);

		const results = sValues.map(sVal =>
			runCorrelationStats(
				nodes,
				initialNodes,
				manyLinks,
				sourceNodeId,
				targetNodeId,
				sVal,
				r,
				maxSteps,
				trials,
				structuralSimilarity
			)
		);
		postMessage(results);
	}

	else if (mode === 'multi-pair-sweep') {
		const results = [];

		for (const [source, target] of randomPairs(nodes, numPairs)) {
			const similarity = computeAvgJaccardSimilarity(manyLinks, source, target);

			for (const sVal of sValues) {
				const res = runCorrelationStats(
					nodes,
					initialNodes,
					manyLinks,
					source,
					target,
					sVal,
					r,
					maxSteps,
					trials,
					similarity
				);

				results.push({
					...res,
					sourceId: source,
					targetId: target
				});
			}
		}

		postMessage(results);
	}

	else {
		const result = runCorrelationStats(
			nodes,
			initialNodes,
			manyLinks,
			sourceNodeId,
			targetNodeId,
			s,
			r,
			maxSteps,
			trials
		);
		postMessage(result);
	}
};
