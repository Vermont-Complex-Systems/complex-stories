  <script>
    import { Plot, Dot, LineY, AreaY, HTMLTooltip } from 'svelteplot';
    import Toggle from './helpers/Toggle.svelte'
    import RangeFilter from './helpers/RangeFilter.svelte'
    
    let { data, maxAge } = $props();
  </script>

<div>
<Plot grid frame 
      x={{label: "Academic age →"}}
      y={{label: "↑ # collaborations with younger coauthors", domain: [0,40]}}
      color={{legend: true, type: 'ordinal'}}
      >
    <AreaY 
        {data}
        x="author_age" 
        y1={(d) => d.younger - d.q25_collabs}  
        y2={(d) => d.younger + d.q25_collabs} 
        fillOpacity=0.50 
        fill={(d) => d.has_research_group === 0 ? 'No research group' : 'Has research group'}
        fx="college"
      />
    <AreaY 
        {data}
        x="author_age" 
        y1={(d) => d.younger - d.median_collabs}  
        y2={(d) => d.younger + d.median_collabs} 
        fillOpacity=0.30 
        fill={(d) => d.has_research_group === 0 ? 'No research group' : 'Has research group'}
        fx="college"
      />
    <Dot 
        {data}
        x="author_age" 
        y="younger"
        fill={(d) => d.has_research_group === 0 ? 'No research group' : 'Has research group'}
        r={3}
        fx="college"
    />
</Plot>
</div>