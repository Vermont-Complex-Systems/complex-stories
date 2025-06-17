<script>
  import * as d3 from "d3";
  import { Dashboard } from 'allotaxonometer-ui';
  import { combElems, rank_turbulence_divergence, diamond_count, wordShift_dat, balanceDat } from 'allotaxonometer-ui';
  import ThemeToggle from './ThemeToggle.svelte';
  import Sidebar from './Sidebar.svelte';
    
    import boys1895 from '../data/boys-1895.json';
    import boys1968 from '../data/boys-1968.json';

    // Process the data directly
    let sys1 = $state(boys1895);
    let sys2 = $state(boys1968);
    let alpha = $state(0.58);
    let title = $state(['Boys 1895', 'Boys 1968']); // Make this mutable
    
    let sidebarCollapsed = $state(false);
    let isDarkMode = $state(false);

    let DashboardHeight = 815;
    let DashboardWidth = $derived(sidebarCollapsed ? 1200 : 900);
    let DiamondHeight = 600;
    let DiamondWidth = DiamondHeight;
    let marginInner = 160;
    let marginDiamond = 40;
    let WordshiftWidth = $derived(sidebarCollapsed ? 550 : 400);

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
    let isDataReady = $derived(dat && barData && balanceData && me && rtd);
</script>

<div class="dashboard-app">
    <ThemeToggle bind:isDarkMode />
    
    <div class="app-container">
        <div class="layout">
            <Sidebar 
                bind:sidebarCollapsed 
                bind:sys1 
                bind:sys2 
                bind:title 
                bind:alpha 
                {me} 
                {rtd} 
                {isDataReady} 
            />

        <!-- Main Content -->
        <main class="main-content {sidebarCollapsed ? 'collapsed-sidebar' : ''}">
            {#if isDataReady}
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
                    class="dashboard"
                />
            {:else}
                <div class="loading-container">
                    <div class="loading-content">
                        <div class="spinner"></div>
                        <p class="loading-text">Loading dashboard...</p>
                    </div>
                </div>
            {/if}
        </main>
    </div>
</div>
</div>

<style>
    @import '../styles/app.css';

    /* OVERRIDES */
    
    .dashboard-app :global(button) {
        background: transparent !important;
        color: var(--dash-text-primary) !important;
        border: 1px solid var(--dash-border-color) !important;
        padding: 0.5rem !important;
    }

    .dashboard-app :global(button:hover) {
        background: var(--dash-bg-secondary) !important;
    }
</style>