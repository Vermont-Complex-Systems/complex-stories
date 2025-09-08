<script>
    import { Plot, Dot, Line, RuleY, RuleX, Text } from 'svelteplot';
    let { data, p1, p2 } = $props();
</script>

<Plot 
    grid 
    frame 
    y={{domain:[0,6], label: "↑ τ"}} 
    x={{domain:[0,0.05]}} 
    marginTop={10}
    marginBottom={20}
    marginLeft={30}
    marginRight={10}
    width={200}
    height={150}
>
    <Dot
        {data}
        x = "p"
        y = "tau"
        fill = {(d) => d.p === p1 ? '#1976d2' : d.p === p2 ? '#f57c00' : 'grey'}
        stroke = "black"
        strokeWidth = 0.5
        fillOpacity = {(d) => d.p === p1 ? '1.0' : d.p === p2 ? '1.0' : '0.6'}
        r = {3}
    />
    <RuleY
        data={[2]}
        strokeDasharray="6,6"
        opacity={0.5} 
        strokeWidth={1.5}
    />
    <RuleX
        data={[0.03]}
        strokeDasharray="6,6"
        opacity={0.5} 
        strokeWidth={1.5}
    />
    <Text 
        x={0.027} 
        y={5.7} 
        fontSize={10}
        text="p_c"/>
</Plot>