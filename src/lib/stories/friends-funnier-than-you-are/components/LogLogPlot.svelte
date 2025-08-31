<script>
    import * as d3 from 'd3';
    import { Plot, Dot } from 'svelteplot'
  
    // average branching number = $\ell=3$
    // product with chance to independently improve with probability p = 0.01
    import rawData from '../data/src_cascade_dist/distribution_l3_at_p0.01.txt?raw';
    import rawData2 from '../data/src_cascade_dist/distribution_l3_at_p0.06.txt?raw';
    
    
    function loadData(dat) {
        return dat
            .trim()
            .split('\n')
            .slice(0,10_000)
            .map((line, i) => ({
            value: parseFloat(line.trim()),
            index: i
            }))
            .filter((d)=> d.value > 10e-10 && d.value < 10e5);
    }

    const data= loadData(rawData)
    const data2= loadData(rawData2)

    function formatTicks(d) {
        const exp = Math.round(Math.log10(d));
        return `10^${exp}`;
    }
</script>



<Plot 
    x={{
        type: 'log',
        tickFormat: formatTicks,
        label: "Cascade size s →"
    }} 
    y={{
        type: 'log',
        tickFormat: formatTicks,
        label: "↑ Fraction of cascades"
    }} 
    grid frame
    marginLeft={40}
    marginRight={40}
    color={{ 
        legend: true ,
        domain: ['p=0.01', 'p=0.06'],
        }}
    >
    <Dot
        {data}
        x={(d) => d.index + 1}
        y="value" 
        fill="p=0.01"
        symbol="triangle"
    />
    <Dot
        data={data2}
        x={(d) => d.index + 1}
        y="value" 
        fill="p=0.06"
        symbol="triangle"
    />
</Plot>

