<script>
    import * as d3 from 'd3';

    let { data, fill } = $props();

    const H = 300;
    const MIN_BAR_WIDTH = 20; // px — minimum readable bar width
    const margin = { top: 25, right: 25, bottom: 80, left: 50 };

    let width = $state(1100); // SSR default, updated by bind:clientWidth

    let sorted = $derived([...data].sort((a, b) => b.counts - a.counts));

    // How many bars fit at the current width
    let maxBars = $derived(
        Math.max(5, Math.floor((width - margin.left - margin.right) / MIN_BAR_WIDTH))
    );
    let displayData = $derived(sorted.slice(0, maxBars));

    let xScale = $derived(
        d3.scaleBand()
            .domain(displayData.map(d => d.types))
            .range([margin.left, width - margin.right])
            .padding(0.1)
    );

    let yScale = $derived(
        d3.scaleLinear()
            .domain([0, d3.max(sorted, d => d.counts) ?? 1])
            .nice()
            .range([H - margin.bottom, margin.top])
    );

    let yTicks = $derived(yScale.ticks(5));
</script>

<div class="chart-container" bind:clientWidth={width}>
    <svg {width} height={H}>
        <!-- Y gridlines -->
        {#each yTicks as tick (tick)}
            <line
                x1={margin.left} x2={width - margin.right}
                y1={yScale(tick)} y2={yScale(tick)}
                stroke="var(--color-border, #e5e7eb)"
                stroke-width="1"
            />
        {/each}

        <!-- Bars -->
        {#each displayData as d (d.types)}
            <rect
                x={xScale(d.types) ?? 0}
                y={yScale(d.counts)}
                width={xScale.bandwidth()}
                height={yScale(0) - yScale(d.counts)}
                {fill}
                stroke="grey"
                stroke-width="0.5"
            />
        {/each}

        <!-- Baseline at y=0 -->
        <line
            x1={margin.left} x2={width - margin.right}
            y1={yScale(0)} y2={yScale(0)}
            stroke="currentColor" stroke-width="1"
        />

        <!-- X axis labels (rotated -45°) -->
        {#each displayData as d (d.types)}
            {@const cx = (xScale(d.types) ?? 0) + xScale.bandwidth() / 2}
            {@const cy = yScale(0) + 6}
            <text
                x={cx} y={cy}
                text-anchor="end"
                transform="rotate(-45, {cx}, {cy})"
                font-size="10"
                fill="currentColor"
            >
                {d.types}
            </text>
        {/each}

        <!-- Y axis labels -->
        {#each yTicks as tick (tick)}
            <text
                x={margin.left - 6}
                y={yScale(tick)}
                text-anchor="end"
                dominant-baseline="middle"
                font-size="11"
                fill="currentColor"
            >
                {d3.format('~s')(tick)}
            </text>
        {/each}
    </svg>
</div>

<style>
    .chart-container {
        width: 100%;
        min-height: 300px;
        position: relative;
        overflow: hidden;
    }
</style>
