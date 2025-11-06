import {resetNodes, infectNode, linkBetween} from './dynamics';
import type { Node, Link } from '$lib/types';


export function clone<T>(obj: T): T {
	return JSON.parse(JSON.stringify(obj));
}


export function computeAvgJaccardSimilarity(
	manyLinks: Link[][],
	idA: string,
	idB: string
): number {
	let total = 0;
	let count = 0;

	for (const frame of manyLinks) {
		const neighborsA = new Set<string>();
		const neighborsB = new Set<string>();

		for (const link of frame) {
			const source = typeof link.source === 'object' ? link.source.id : link.source;
			const target = typeof link.target === 'object' ? link.target.id : link.target;

			if (source === idA) neighborsA.add(target);
			if (target === idA) neighborsA.add(source);
			if (source === idB) neighborsB.add(target);
			if (target === idB) neighborsB.add(source);
		}

		const intersection = new Set([...neighborsA].filter(x => neighborsB.has(x)));
		const union = new Set([...neighborsA, ...neighborsB]);

		if (union.size > 0) {
			total += intersection.size / union.size;
			count++;
		}
	}

	return count > 0 ? total / count : 0;
}


export function simulateTrial(
	nodes: Node[],
	initialNodes: Node[],
	manyLinks: Link[][],
	sourceNodeId: string,
	targetNodeId: string,
	s: number,
	r: number,
	maxSteps: number
): { iInfected: boolean; jInfected: boolean } {
	resetNodes(nodes, initialNodes); // copy back positions and clear state

	const source = nodes.find(n => n.id === sourceNodeId)!;
	const target = nodes.find(n => n.id === targetNodeId)!;

	infectNode(source, 0.2); // infect source initially

	let index = 0;
	const p = r * (s / 1000); // infection probability per contact

	for (let t = 0; t < maxSteps; t++) {
		const renderedLinks = manyLinks[index];
		index = (index + 1) % manyLinks.length;

		if (
			source.infected &&
			!target.infected &&
			renderedLinks.some(link => linkBetween(source, target, link))
		) {
			if (Math.random() < p) {
				infectNode(target);
			}
		}
	}

	return {
		iInfected: source.infected,
		jInfected: target.infected
	};
}

export function runCorrelationStats(
	nodes: Node[],
	initialNodes: Node[],
	manyLinks: Link[][],
	sourceNodeId: string,
	targetNodeId: string,
	s: number,
	r: number,
	maxSteps: number = 100,
	trials = 1000,
    structuralSimilarity: number = 0 // default if not passed
) {
	let countJoint10 = 0;
	let countI = 0;
	let countJNot = 0;

	let count_00 = 0;
	let count_01 = 0;
	let count_10 = 0;
	let count_11 = 0;

	for (let i = 0; i < trials; i++) {
		const { iInfected, jInfected } = simulateTrial(
			nodes,
			initialNodes,
			manyLinks,
			sourceNodeId,
			targetNodeId,
			s,
			r,
			maxSteps
		);

		if (iInfected) countI++;
		if (!jInfected) countJNot++;
		if (iInfected && !jInfected) countJoint10++;

		if (!iInfected && !jInfected) count_00++;
		if (!iInfected && jInfected) count_01++;
		if (iInfected && !jInfected) count_10++;
		if (iInfected && jInfected) count_11++;
	}

	const p_i = countI / trials;
	const p_j_not = countJNot / trials;
	const p_10 = countJoint10 / trials;
	const ratio = p_i > 0 && p_j_not > 0 ? p_10 / (p_i * p_j_not) : null;

	const total = trials;
	const p00 = count_00 / total;
	const p01 = count_01 / total;
	const p10 = count_10 / total;
	const p11 = count_11 / total;

	const p_i_0 = p00 + p01;
	const p_i_1 = p10 + p11;
	const p_j_0 = p00 + p10;
	const p_j_1 = p01 + p11;

	function safeTerm(pxy: number, px: number, py: number): number {
        if (pxy === 0 || px === 0 || py === 0) return 0;
        return pxy * Math.log2(pxy / (px * py));
    }
    
    const MI =
      safeTerm(p00, p_i_0, p_j_0) +
      safeTerm(p01, p_i_0, p_j_1) +
      safeTerm(p10, p_i_1, p_j_0) +
      safeTerm(p11, p_i_1, p_j_1);

      
    // console.log(`p00=${p00}, p01=${p01}, p10=${p10}, p11=${p11}, p_i_0=${p_i_0}, p_i_1=${p_i_1}, p_j_0=${p_j_0}, p_j_1=${p_j_1}, MI=${MI}, structuralSimilarity=${structuralSimilarity}`);

	const E_X = p_i_1;
	const E_Y = p_j_1;
	const E_XY = p11;

	const varX = E_X * (1 - E_X);
	const varY = E_Y * (1 - E_Y);
	const covXY = E_XY - E_X * E_Y;

	const pearsonR = varX > 0 && varY > 0 ? covXY / Math.sqrt(varX * varY) : 0;


	return {
		s,
		p_10,
		p_i,
		p_j_not,
		correlationRatio: ratio, // renamed
		pearsonR,
		MI,
        structuralSimilarity
	};
}