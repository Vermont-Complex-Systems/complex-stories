<script lang="ts">
	import { createInterval } from '../utils/interval';
	import {
		resetNodes,
		infectNode,
		highlightConnectedNodes,
		highlightRandomNeighbor,
		infectRandomNeighbors,
		highlightNode,
		StarNode,
		idConnectedNodes,
	} from '../utils/dynamics';

	import Manylinks from '../data/edges.json';

	import Edges from './SimpleLinks.svelte';
	import Nodes from './Nodes.svelte';

	import { radialLayout } from '../utils/RadialLayout';

	// Props
	let { scrollyIndex, nodes, links, width, height, padding } = $props();

	// Layout dimensions
	let innerHeight = height - padding.top - padding.bottom;

	// Initial layout and state
	let nodes_xy: Node[] = $state(radialLayout({ nodes, links, width, height: innerHeight }));

	const mainNode = $derived(nodes_xy[0]);

	let renderedLinks = $state(links);

	let index = $state(1);
	let stopInterval: () => void = () => {};

	let selectedNeighbor: string | null = $state(null); 

	function takeOneStep(probability = 1.0) {
		// 1. Update links (rewire)
		index = (index + 1) % Manylinks.length;
		renderedLinks = Manylinks[index];

		// 2. Clear previous highlights
		nodes_xy.forEach(n => n.highlight = false);

		// 3. Wait a short time before attempting infection (so you can "see" the rewire)
		setTimeout(() => {
			const infectedNodes = nodes_xy.filter(n => n.infected);
			const source = infectedNodes[Math.floor(Math.random() * infectedNodes.length)];
			
			if (infectedNodes.length === 0) return; // no one to spread from

			const chosen = highlightRandomNeighbor(nodes_xy, renderedLinks, source.id);
			
			// 4. Optional: flicker highlight even if not infected
			if (chosen) {
				chosen.highlight = true;

				// Short delay before infection so user sees flicker
				setTimeout(() => {
					infectNode(chosen, probability); // probabilistic infection
				}, 800); // you can tweak this delay
			}
		}, 300); // delay between rewire and highlight
	}

	function runSteps(n: number, delay: number = 1000, probability: number = 1.0) {
		let step = 0;

		function doStep() {
			if (step >= n) return;

			takeOneStep(probability);
			step++;

			setTimeout(doStep, delay);
		}

		doStep();
	}
	

	$effect(() => {
		stopInterval();

		switch (scrollyIndex) {
			case 0:
				resetNodes(nodes_xy, nodes);
				mainNode.shape = undefined;
				stopInterval = createInterval(() => {
					index = (index + 1) % Manylinks.length;
					renderedLinks = Manylinks[index];
				}, 500);
				break;

			case 1:
				StarNode(mainNode);
				infectNode(mainNode);
				nodes_xy.forEach(n => (n.highlight = false));
				break;

			case 2:
				infectNode(mainNode);
				highlightConnectedNodes(nodes_xy, renderedLinks, mainNode.id);
				break;

			case 3:
				selectedNeighbor = highlightRandomNeighbor(nodes_xy, renderedLinks, mainNode.id);
				break;

			case 4:
				if (selectedNeighbor) {
					infectNode(selectedNeighbor)
				}
				break;
			case 5:
				setTimeout(() => runSteps(10, 1000 ,0.5), 0);
				break;
			case 6:
				// PART II: complex contagion 
				resetNodes(nodes_xy, nodes);
				break
			case 7:
				idConnectedNodes(nodes_xy, renderedLinks, mainNode.id);
				break				
			case 8:
				highlightNode(mainNode);
				infectRandomNeighbors(nodes_xy, renderedLinks, mainNode.id, 4);
				break;
			case 9:
				infectNode(mainNode);
				break
			case 10:
				resetNodes(nodes_xy, nodes);
				stopInterval = createInterval(() => {
					index = (index + 1) % Manylinks.length;
					renderedLinks = Manylinks[index];
				}, 500);
				break;
		}

		return () => stopInterval();
});
</script>


<div class="chart-container">
	<svg {width} {height} style="overflow: visible; max-width: 100%;">
		<g class="inner-chart">
			<Edges links={renderedLinks} nodes={nodes_xy} />
			<Nodes nodes={nodes_xy} />
		</g>
	</svg>
</div>

<style>
	:global(*) {
		font-family: Inter;
		-moz-osx-font-smoothing: grayscale;
	}
	
	.chart-container {
		width: 100%;
		display: flex;
		justify-content: center;
		align-items: center;
	}

	@media (max-width: 768px) {
		.chart-container {
			overflow: hidden;
		}
	}
</style>
