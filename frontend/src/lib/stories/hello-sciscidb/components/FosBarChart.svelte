<script>
    import { Plot, BarY} from 'svelteplot';
    let { data } = $props();

    // Separate data by metric type for layered bars
    const totalData = data.filter(d => d.metric_type === 'total');
    const abstractData = data.filter(d => d.metric_type === 'has_abstract');
    const fulltextData = data.filter(d => d.metric_type === 'has_fulltext');
</script>

<Plot
    x={{ type: "band", tickRotate: 40, label: "" }}
    y={{ grid: true, label: "↑ # Available papers" }}
    height={500}
    marginRight={40}
    >
    <!-- Background layer: total papers (lightest grey) -->
    <BarY
        data={totalData}
        x="field"
        y="count"
        fill="lightgrey"
        strokeWidth={1}
    />
    <!-- Middle layer: papers with abstracts (medium grey) -->
    <BarY
        data={abstractData}
        x="field"
        y="count"
        fill="#a0a0a0"
        inset={4}
    />
    <!-- Top layer: papers with full text (darkest grey) -->
    <BarY
        data={fulltextData}
        x="field"
        y="count"
        fill="#606060"
        inset={8}
    />
</Plot>