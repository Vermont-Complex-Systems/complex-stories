<script>
    import { scaleOrdinal, scaleLinear } from "d3-scale"


    let { nodes, isGroup = false } = $props()
 
    let color_palette = ["#778da9", "#6a4c93", "#005f73", "#0a9396", "#94d2bd", "#e9d8a6", "#ee9b00", "#ca6702", "#bb3e03", "#ae2012", "#9b2226"]
    let color_scale = scaleOrdinal([1,2,3,4,5], color_palette)

    function generateStarPath(cx, cy, outerRadius, points, innerRatio) {
        const path = [];
        const angle = Math.PI / points;

        for (let i = 0; i < 2 * points; i++) {
            const r = i % 2 === 0 ? outerRadius : outerRadius * innerRatio;
            const a = i * angle;
            const x = cx + r * Math.sin(a);
            const y = cy - r * Math.cos(a);
            path.push(i === 0 ? `M${x},${y}` : `L${x},${y}`);
        }

        path.push("Z");
        return path.join(" ");
    }

    let r = scaleLinear()
        .domain([0, 1])
        .range([3, 10])
        .clamp(true);

</script>

<g class="node">
{#each nodes as node}
    <g class="nodes">
    {#if node.shape === 'star'}
        <path
            d={generateStarPath(node.x, node.y, 15, 5, 0.5)} 
            fill={node.infected ? "red" : "lightgrey"}
            stroke={node.highlight ? "yellow" : "black"}
            stroke-width={node.highlight ? 2 : 1}
            class:highlight={node.highlight === true }
            opacity={1}
        />
        {:else}
        <circle
            cx={node.x}
            cy={node.y}
            fill={isGroup ? color_scale(node.group) : node.infected === true ? "red" : "lightgrey"}
            stroke={node.highlight === true ? "yellow" : "black"}
            opacity=1.
            class:highlight={node.highlight === true }
            stroke-width={node.highlight === true ? 2 : 1}
            r={node.vbet != null ? r(node.vbet) : 8}
            />
    {/if}
    </g>
    <g>
    {#if isGroup}
        <text
        x={node.x}
        y={node.y}
        dx={7}
        font-size=13
        stroke="black"
        opacity=1.
        stroke-width=0.1
        >{node.label[0]}. {node.label.split(" ")[node.label.split(" ").length-1]}</text>
    {/if}
    </g>
{/each}
</g>

<style>
    .nodes {
      filter: drop-shadow(3px 5px 2px rgb(0 0 0 / 0.4));
    }
    
    circle {
        transition: r 300ms ease, opacity 500ms ease,
        cx 500ms cubic-bezier(0.76, 0, 0.24, 1),
        cy 500ms cubic-bezier(0.76, 0, 0.24, 1); /* https://easings.net/#easeInOutQuart */
        cursor: pointer;
    }

    @keyframes flicker {
    0%, 100% {
        opacity: 1;
        filter: drop-shadow(0 0 6px yellow);
    }
    50% {
        opacity: 0.3;
        filter: drop-shadow(0 0 12px orange);
    }
    }

    circle.highlight {
        animation: flicker 1s ease-in-out infinite;
    }


</style>