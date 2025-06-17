<script>
    import * as d3 from "d3";
    import { fly } from 'svelte/transition';
    
    let { barData, height = 300, dataType = "wordshift" } = $props();
    
    let width = $state(640);   
    
    let margin = { top: 40, left: 60, right: 20, bottom: 70 };

    // Handle different data formats
    let words = $derived(() => {
        if (dataType === "babynames") {
            return barData.map(d => d.types || d.word || d.name);
        }
        return barData.map(d => d.word);
    });
    
    let metrics = $derived(() => {
        if (dataType === "babynames") {
            return barData.map(d => d.counts || d.count || d.value);
        }
        return barData.map(d => Math.abs(d.metric));
    });

    let xScale = $derived(d3.scaleBand()
                  .domain(words)
                  .range([margin.left, width - margin.right])
                  .padding(0.1));
                  
    let yScale = $derived(d3.scaleLinear()
                  .domain([0, d3.max(metrics) || 1])
                  .range([height - margin.bottom, margin.top]));

    let yTicks = $derived(yScale.ticks(6));

    // Color scale for different data types
    let colorScale = $derived(() => {
        if (dataType === "babynames") {
            return d3.scaleOrdinal().range(["#2563eb"]);
        }
        return d3.scaleOrdinal()
                 .domain(["positive", "negative"])
                 .range(["#2563eb", "#dc2626"]);
    });
</script>

<div class="chart-container" bind:clientWidth={width}> 
    <svg {width} {height}>
        <!-- Y-axis -->
        <g class="axis y">
            {#each yTicks as tick}
                <g class="tick" transform="translate(0, {yScale(tick)})">
                    <text
                        y={-3}
                        dx={margin.left - 5}
                        dy={6}
                        text-anchor="end"
                    >
                        {#if dataType === "babynames"}
                            {d3.format(".0f")(tick)}
                        {:else}
                            {d3.format(".2f")(tick)}
                        {/if}
                    </text>
                    <line
                        x1={margin.left}
                        x2={width - margin.right}
                        y1={0}
                        y2={0}
                        stroke={tick === 0 ? '#8f8f8f' : '#e5e7eb'}
                        stroke-width={tick === 0 ? 1.5 : 0.5}
                    />
                </g>
            {/each}
        </g>

        <!-- X-axis -->
        <g class="axis x" transform="translate(0, {yScale(0)})">
            {#each words as word, i}
                <g class="tick" transform="translate({xScale(word) + xScale.bandwidth()/2}, 0)">
                    <text
                        dy={15}
                        text-anchor="middle"
                        transform="rotate(45)"
                        class="word-label"
                    >{word}</text>
                </g>
            {/each}
        </g>

        <!-- Bars or Circles based on data type -->
        {#if dataType === "babynames"}
            <!-- Circles for baby names (like the original) -->
            {#each barData as d, i}
                <circle
                    in:fly={{ y: 10, opacity: 0, duration: 500, delay: i * 30 }}
                    cx={xScale(d.types || d.word || d.name) + xScale.bandwidth()/2}
                    cy={yScale(d.counts || d.count || d.value)}
                    r={4}
                    fill="#2563eb"
                    opacity={0.8}
                    stroke="black"
                    stroke-width="0.5"
                />
            {/each}
        {:else}
            <!-- Bars for word shift data -->
            {#each barData as d, i (d.word)}
                {#if d.metric !== 0}
                    <rect
                        in:fly={{ y: 20, opacity: 0, duration: 500, delay: i * 50 }}
                        x={xScale(d.word)}
                        y={d.metric > 0 ? yScale(Math.abs(d.metric)) : yScale(0)}
                        width={xScale.bandwidth()}
                        height={Math.abs(yScale(Math.abs(d.metric)) - yScale(0))}
                        fill={colorScale(d.metric > 0 ? "positive" : "negative")}
                        opacity={0.8}
                        stroke="black"
                        stroke-width="0.5"
                    />
                {/if}
            {/each}

            <!-- Circles on top of bars -->
            {#each barData as d, i (d.word)}
                {#if d.metric !== 0}
                    <circle
                        in:fly={{ y: 10, opacity: 0, duration: 500, delay: i * 50 + 200 }}
                        cx={xScale(d.word) + xScale.bandwidth()/2}
                        cy={yScale(Math.abs(d.metric))}
                        r={3}
                        fill={colorScale(d.metric > 0 ? "positive" : "negative")}
                        opacity={0.9}
                        stroke="white"
                        stroke-width="1"
                    />
                {/if}
            {/each}
        {/if}
    </svg>
</div>

<style>
    .chart-container {
        position: relative;
        margin: 1rem 0;
    }

    rect {
        transition: 
            height 700ms cubic-bezier(0.76, 0, 0.24, 1),
            y 700ms cubic-bezier(0.76, 0, 0.24, 1),
            opacity 700ms cubic-bezier(0.76, 0, 0.24, 1);
        cursor: pointer;
    }

    circle {
        transition: 
            cy 700ms cubic-bezier(0.76, 0, 0.24, 1),
            r 300ms ease, 
            opacity 700ms cubic-bezier(0.76, 0, 0.24, 1);
        cursor: pointer;
    }

    .tick {
        fill: hsla(212, 10%, 53%, 1);
        font-size: 12px;
    }

    .word-label {
        font-size: 11px;
        font-weight: 500;
    }

    rect:hover, circle:hover {
        opacity: 1;
    }
</style>