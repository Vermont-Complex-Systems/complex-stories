<script>
    import { Plot, TickY, Line, RuleY, groupX } from 'svelteplot';
    import { dashboardState, dataState, prodAgg } from '../state.svelte.ts';
    let { data } = $props();
    
    const uniqueColleges = [
        'College of Engineering and Mathematical Sciences', 
        'Rubenstein School of Environment and Natural Resources', 
        'Larner College of Medicine', 'College of Arts and Sciences', 
        'College of Agriculture and Life Sciences', 
        'Grossman School of Business', 'College of Nursing and Health Sciences', 
        'College of Education and Social Services'
        ]
   
    // Thrigger reload
    $effect(async () => {
    if (dashboardState.selectedCollege) {
        dataState.prodAgg = await prodAgg(dashboardState.selectedCollege);
    }
});
</script>

<select class="filter-select" bind:value={dashboardState.selectedCollege}>
    <option value="">All colleges</option>
    {#each uniqueColleges as collegeName}
          <option value={collegeName}>{collegeName}</option>
    {/each}
</select>

<Plot y={{ grid: true, label: "↑ # mean number papers" }}>
    <RuleY data={[0]} />
    <TickY {data} 
        x="author_age" y="nb_papers" stroke={(d) => d.name == dashboardState.selectedAuthor ? 'lime' : 'black'} 
        strokeWidth=4
        />
    <Line
        {...groupX(
            { data: data, x: 'author_age', y: 'nb_papers' },
            { y: 'mean' }
        )}
        stroke="red"
        strokeWidth="2"
        curve="basis" />

</Plot>