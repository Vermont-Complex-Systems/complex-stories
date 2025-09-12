<script>
    import { Plot, Dot, Line, RuleY, RuleX, Text } from 'svelteplot';
    let { data, p1, p2 } = $props();
</script>

<Plot 
    grid 
    frame 
    y={{domain:[0,6], label: "↑ τ"}} 
    x={{domain:[0,0.05]}} 
    marginTop={18}
    marginBottom={20}
    marginLeft={0}
    marginRight={20}
    width={200}
    height={170}
>
    <Dot
        {data}
        x = "p"
        y = "tau"
        fill = {(d) => d.p === p1 ? '#64b5f6' : d.p === p2 ? '#ffb74d' : '#ddd'}
        stroke = "grey"
        strokeWidth = 0.5
        fillOpacity = {(d) => d.p === p1 ? '0.7' : d.p === p2 ? '0.7' : '0.2'}
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