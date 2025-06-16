<script lang="ts">
  import * as d3 from "d3";
  import { combElems, rank_turbulence_divergence, diamond_count, wordShift_dat, balanceDat } from 'allotaxonometer-ui';
  import { Dashboard } from 'allotaxonometer-ui';
  import { Slider } from "bits-ui";
  
  import boys1895 from '../data/boys-1895.json';
  import boys1968 from '../data/boys-1968.json';

      // Process the data directly
    let sys1 = $state(boys1895);
    let sys2 = $state(boys1968);
    let alpha = $state(0.58);
    let title = $state(['Boys 1895', 'Boys 1968']); // Make this mutable

    let showSidebar = $state(true);
  
    let DashboardHeight = 815;
    let DashboardWidth = 1200;
    let DiamondHeight = 500;
    let DiamondWidth = DiamondHeight;
    let marginInner = 140;
    let WordshiftWidth = 300;
    let marginDiamond = 40;
    
    const alphas = d3.range(0,18).map(v => +(v/12).toFixed(2)).concat([1, 2, 5, Infinity]);
    let alphaIndex = $state(7); // Start at 0.58

    $effect(() => {
        alpha = alphas[alphaIndex];
    });
    // Data processing
    let me = $derived(sys1 && sys2 ? combElems(sys1, sys2) : null);
    let rtd = $derived(me ? rank_turbulence_divergence(me, alpha) : null);
    let dat = $derived(me && rtd ? diamond_count(me, rtd) : null);
    
    let barData = $derived(me && dat ? wordShift_dat(me, dat).slice(0, 30) : []);
    let balanceData = $derived(sys1 && sys2 ? balanceDat(sys1, sys2) : []);
    let maxlog10 = $derived(me ? Math.ceil(d3.max([Math.log10(d3.max(me[0].ranks)), Math.log10(d3.max(me[1].ranks))])) : 0);
    let max_count_log = $derived(dat ? Math.ceil(Math.log10(d3.max(dat.counts, d => d.value))) + 1 : 2);
    let max_shift = $derived(barData.length > 0 ? d3.max(barData, d => Math.abs(d.metric)) : 1);
  
</script>
<div class="app-layout">
  {#if showSidebar}
  <aside class="sidebar">
      <div class="alpha-container">
        
          <span class="alpha-value">α={alpha}</span>

          <input 
            type="range"
            min="0"
            max={alphas.length - 1}
            value={alphaIndex}
            oninput={(e) => alphaIndex = parseInt(e.target.value)}
            list="alpha-settings"
            class="myslider"
          />
          
          <datalist id="alpha-settings">
            {#each alphas as ax, i}
              <option value={i} label={ax}></option>
            {/each}
          </datalist>
  </aside>
{/if}

<main class="dashboard-wrapper">
<Dashboard 
    {dat}
    {alpha}
    divnorm={rtd.normalization}
    {barData}
    {balanceData}
    {title}
    {maxlog10}
    {max_count_log}
    height={DashboardHeight}
    width={DashboardWidth}
    {DiamondHeight}
    {DiamondWidth}
    {marginInner}
    {marginDiamond}
    {WordshiftWidth}
    xDomain={[-max_shift * 1.5, max_shift * 1.5]}
/>
</main>
</div>


<style>


.myslider {
  width: 100%;
  height: 0.5rem;
  background-color: #e5e7eb; /* gray-200 in Tailwind */
  border-radius: 0.5rem;
  appearance: none;
  -webkit-appearance: none;
  cursor: pointer;
}


.alpha-container {
  display: flex;
  flex-direction: column;
}

.alpha-container > * + * {
  margin-top: 1rem; /* Replicates space-y-4 */
}


.alpha-value {
  font-size: 1rem; /* text-2xl */
  font-family: monospace; /* font-mono */
}



@media (max-width: 768px) {
  .app-layout {
    flex-direction: column;
  }

  .sidebar {
    width: 100%;
    border-right: none;
    border-bottom: 1px solid #e5e7eb;
  }
}


.app-layout {
  display: flex;
  height: 100vh;           /* Full screen height */
  width: 100vw;           
  overflow: hidden;
}

.sidebar {
  width: 150px;            /* Set your sidebar width */
  background: #f9fafb;
  border-right: 1px solid #e5e7eb;
  padding: 1.5rem;         /* Matches p-6 */
  overflow-y: auto;
  box-sizing: border-box;
}

.dashboard-wrapper {
  flex: 1;
  overflow: auto;
  padding: .5rem;
  background: white;
}

</style>