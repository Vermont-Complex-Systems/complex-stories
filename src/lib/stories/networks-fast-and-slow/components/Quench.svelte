<script lang="ts">
	
	import { createInterval } from '../utils/interval';
	import type { Node, Link } from '$lib/types';
	import {
		resetNodes,
		infectNode,
		highlightNode,
        linkBetween,
		StarNode,
	} from '../utils/dynamics';
	
	import Manylinks from '../data/edges.json';

	import Edges from './SimpleLinks.svelte';
	import Nodes from './Nodes.svelte';

	import { radialLayout } from '../utils/RadialLayout';

	import ScatterCorr from './ScatterCorr.svelte';
	
	// Props
	let { scrollyIndex, nodes, links, width, height, padding } = $props();
    
	
	// Layout dimensions
	let innerHeight = height - padding.top - padding.bottom;
	
	// Initial layout and state
	let nodes_xy: Node[] = $state(radialLayout({ 
		nodes, links, width, height: innerHeight
	}));
	
	const mainNode = $derived(nodes_xy[0]);
	const targetNode = $derived(nodes_xy[5]);
	
	// let renderedNodesData = $state(nodes);
	let renderedLinks = $state(links);

	let index = $state(1);
	let stopInterval: () => void = () => {};
	let cumulativeTime = $state(0);
    // Simulation parameters
    const s = 500; // contact frame duration (1000ms = 1s per frame)
    const r = 0.2; // infection rate per second
    const infectionProbPerContact = r * (s / 1000); // convert ms to seconds

    // State
    let contactTime = 0;
    let targetInfected = false;

    // On each step
    function takeOneStep() {
        index = (index + 1) % Manylinks.length;
        renderedLinks = Manylinks[index];

        // Check contact between source and target
        const isContact = renderedLinks.some(link => linkBetween(mainNode, targetNode, link));

        if (isContact) {
            mainNode.highlight = true;
            targetNode.highlight = true;
            contactTime += s/1e3;

            if (!targetInfected && Math.random() < infectionProbPerContact) {
                infectNode(targetNode);
                targetInfected = true;
				cumulativeTime += contactTime;
                console.log("Infected after", contactTime, "seconds of cumulative contact.");
            }
        } else {
            mainNode.highlight = false;
            targetNode.highlight = false;
        }
    }

	function runSteps(n: number, delay: number = 1000) {
		let step = 0;

		function doStep() {
			if (step >= n) return;

			takeOneStep();
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
                
                StarNode(mainNode);
				infectNode(mainNode);
                
                StarNode(targetNode);
				highlightNode(targetNode);

				nodes_xy.forEach(n => (n.highlight = false));
				break;
            
            case 1:        
                setTimeout(() => runSteps(20, s ), 0);
                break;
			case 2:
				resetNodes(nodes_xy, nodes);
				stopInterval = createInterval(() => {
					index = (index + 1) % Manylinks.length;
					renderedLinks = Manylinks[index];
				}, 500);

        }
		
		return () => stopInterval();
    })

</script>


<div class="chart-container">
	{#if scrollyIndex >= 2 && scrollyIndex <= 3}
		<div class="scatter-wrapper">
			<ScatterCorr {nodes} {nodes_xy} {Manylinks} {mainNode} {targetNode} {scrollyIndex}/>
		</div>
	{:else}
		<svg {width} {height} style="overflow: visible;">
			<g class="inner-chart">
				<Edges links={renderedLinks} nodes={nodes_xy} />
				<Nodes nodes={nodes_xy} />
			</g>
		</svg>
	{/if}
</div>

<style>
	.chart-container {
		width: 100%;
		height: 100%;
		display: flex;
		align-items: center;
		justify-content: center;
	}

	.scatter-wrapper {
		width: 100%;
		height: 100%;
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		min-height: 500px; /* Ensure adequate height */
	}

	:global(*) {
		font-family: Inter;
		-moz-osx-font-smoothing: grayscale;
	}
</style>
