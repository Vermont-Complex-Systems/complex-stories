import type { Node, Link, RadialLayoutOptions } from '$lib/types';
import { clone } from '../utils/correlation';

export function radialLayout({ nodes, links, width, height }: RadialLayoutOptions): Node[] {
	const radius = Math.min(width / 1.5, height) / 1.5;

	nodes.forEach((node, i) => {
		const angle = (i / nodes.length) * 2 * Math.PI;
		node.x = width / 2 + radius * Math.cos(angle);
		node.y = height / 2 + radius * Math.sin(angle);
	});

	const nodeMap = new Map(nodes.map(n => [n.id, n]));

	links.forEach(link => {
		const sourceId = typeof link.source === 'string' ? link.source : link.source.id;
		const targetId = typeof link.target === 'string' ? link.target : link.target.id;

		link.source = nodeMap.get(sourceId) as Node;
		link.target = nodeMap.get(targetId) as Node;
	});

	return nodes;
}
