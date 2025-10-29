import type { Node, Link } from '$lib/types';

/**
 * Reset all nodes.
 */
export function resetNodes(nodes: Node[], initialNodes: Node[]) {
	nodes.forEach((n, i) => {
		n.infected = false;
		n.highlight = false;
		n.shape = undefined;
		n.x = initialNodes[i].x;
		n.y = initialNodes[i].y;
	});
}

export function linkBetween(nodeA: Node, nodeB: Node, link: Link): boolean {
	const sourceId = typeof link.source === 'object' ? link.source.id : link.source;
	const targetId = typeof link.target === 'object' ? link.target.id : link.target;

	return (
		(sourceId === nodeA.id && targetId === nodeB.id) ||
		(sourceId === nodeB.id && targetId === nodeA.id)
	);
}


export function infectNode(node: Node, probability: number = 1.0): boolean {
	node.highlight = false;
	if (Math.random() < probability) {
		node.infected = true;
		return true;
	} else {
		return false;
	}
}

export function highlightNode(node: Node) {
	node.highlight = true;
}

export function StarNode(mainNode: Node) {
	mainNode.shape = "star";
}

/**
 * Return a list of neighbor node IDs connected to the given node.
 */
export function getNeighbors(links: Link[], mainId: string): string[] {
	const connectedIds = new Set<string>();

	links.forEach(link => {
		const sourceId = typeof link.source === 'object' ? link.source.id : link.source;
		const targetId = typeof link.target === 'object' ? link.target.id : link.target;

		if (sourceId === mainId && targetId !== mainId) connectedIds.add(targetId);
		else if (targetId === mainId && sourceId !== mainId) connectedIds.add(sourceId);
	});

	return Array.from(connectedIds);
}

/**
 * Highlight all neighbors of the main node (excluding itself).
 */
export function highlightConnectedNodes(nodes: Node[], links: Link[], mainId: string) {
	const neighbors = getNeighbors(links, mainId);
	
	// Filter to only uninfected neighbors
	const uninfectedNeighbors = neighbors
		.map(id => nodes.find(n => n.id === id))
		.filter(n => n && !n.infected) as Node[];

	uninfectedNeighbors.forEach(n => {
		n.highlight = neighbors.includes(n.id);
	});
}

/**
 * Make uninfected neighbors flicker. Return the chosen Node to infect next.
 */
export function highlightRandomNeighbor(
	nodes: Node[],
	links: Link[],
	mainId: string
): Node | null {
	const neighbors = getNeighbors(links, mainId);

	// Filter to only uninfected neighbors
	const uninfectedNeighbors = neighbors
		.map(id => nodes.find(n => n.id === id))
		.filter(n => n && !n.infected) as Node[];

	// Choose one at random if any
	const chosenNode = uninfectedNeighbors.length > 0
		? uninfectedNeighbors[Math.floor(Math.random() * uninfectedNeighbors.length)]
		: null;

	// Highlight the chosen one (and un-highlight others)
	nodes.forEach(n => {
		n.highlight = n === chosenNode;
	});

	return chosenNode;
}

/**
 * Highlight all neighbors of the main node (excluding itself).
 */
export function idConnectedNodes(nodes: Node[], links: Link[], mainId: string) {
	const neighbors = getNeighbors(links, mainId);

	nodes.forEach(n => {
		if (n.id !== mainId) {
			n.shape = neighbors.includes(n.id) === true ? 'star' : undefined;
		}
	});
}

/**
 * Infect all neighbors of the main node (excluding itself).
 */
export function infectNeighborood(nodes: Node[], links: Link[], mainId: string) {
	const neighbors = getNeighbors(links, mainId);

	nodes.forEach(n => {
		n.infected = neighbors.includes(n.id);
	});
}



export function infectRandomNeighbors(
	nodes: Node[],
	links: Link[],
	mainId: string,
	count: number = 1, // number of neighbors to maybe infect
	probability: number = 1.0 // chance each one gets infected
): string[] {
	const neighbors = getNeighbors(links, mainId);

	// Shuffle neighbors
	const shuffled = [...neighbors].sort(() => Math.random() - 0.5);

	// Choose up to `count` neighbors
	const selected = shuffled.slice(0, count);

	const infected: string[] = [];

	nodes.forEach(n => {
		if (selected.includes(n.id) && Math.random() < probability) {
			n.infected = true;
			infected.push(n.id);
		} 
	});

	return infected;
}


