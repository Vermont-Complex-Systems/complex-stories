<script>
    import { Plot, BarY, RuleY } from 'svelteplot';

    let { data, x, y, fill } = $props();
</script>

<Plot 
        y={{ grid: true }}
        x={{ tickRotate: 25, label: '' }}
        marginTop={25} 
        marginRight={25} 
        height={300}>
        <BarY 
            {data} {y} {x} {fill}
            stroke="grey"/>
        <RuleY data={[0]} />
</Plot>
