  <script>
    import { Plot, AreaY, LineY, HTMLTooltip } from 'svelteplot';
    import Toggle from './Toggle.svelte'
    import RangeFilter from './RangeFilter.svelte'
    
    let { data, isFacet, showMed, showArea, maxAge } = $props();
  </script>

<div>
      <Plot grid frame 
          x={{label: "Academic age →"}}
          y={{label: "↑ Mean # of collaborations"}}
          color={{legend: true, scheme: ["#404788FF", "#20A387FF", "#FDE725FF"]}}
          >
          {#if showMed}
            <LineY {data}  
              x="age_std" 
              y="mean_collabs"
              stroke="age_category" 
              strokeOpacity=0.4
              fx={isFacet ? "age_category" : null}/>
              <LineY {data}  
                x="age_std" 
                y="median_collabs"
                strokeDasharray=5
                strokeWidth=3
                stroke="age_category" 
                fx={isFacet ? "age_category" : null}/>
          {:else}
              <LineY {data}  
                x="age_std" 
                y="mean_collabs"
                stroke="age_category" 
                fx={isFacet ? "age_category" : null}/>
          {/if}
          {#if showArea}
            <AreaY 
              {data} 
              x="age_std" 
              y1={(d) => d.mean_collabs - d.std_collabs}  
              y2={(d) => d.mean_collabs + d.std_collabs} 
              fillOpacity=0.2 
              fill="age_category"
              fx={isFacet ? "age_category" : null}
            />
          {/if}
      </Plot>
</div>