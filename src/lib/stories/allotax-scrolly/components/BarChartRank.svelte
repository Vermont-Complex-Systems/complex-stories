<script>
    import { Plot, BarY, RuleY } from 'svelteplot';

    let { data, fill } = $props();
</script>

<Plot 
        y={{ grid: true }}
        x={{ tickRotate: 25 }}
        marginTop={25} 
        marginRight={25} 
        height={300}>
        <BarY 
            {data}
            y="counts" x="types" 
            {fill}
            stroke="grey"
            sort={{ channel: '-y' }}  />
        <RuleY data={[0]} />
</Plot>
