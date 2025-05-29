// src/lib/types.ts
export interface RadialLayoutOptions {
	nodes: Node[];
	links: Link[];
	width: number;
	height: number;
}

export type Node = {
	id: string;
	x: number;
	y: number;
	shape?: string;
	infected?: boolean;
	highlight?: boolean;
};

export type RawLink = {
	source: string;
	target: string;
	value: number;
};

export type SimulatedLink = {
	source: Node;
	target: Node;
	value: number;
	index?: number;
	highlight?: boolean;
};

// Union type that covers both
export type Link = RawLink | SimulatedLink;