<script>
    import { Plot, BarY, RuleY } from 'svelteplot';

    let { data, fill } = $props();
    const labelMap = { 1: "Public", 2: "Mixed", 3: "Private" };
</script>

<Plot 
        y={{ grid: true }}
        x={{ label: '' }}
        marginTop={25} 
        marginRight={25} 
        height={300}
        color={{
            type: "ordinal", 
            scheme: "pastel1"
        }}>
        <BarY 
            {data}
            y="count" x={(d) => labelMap[d.types] }
            {fill}
            stroke="grey"
            sort={{ channel: '-y' }}  />
        <RuleY data={[0]} />
</Plot>
