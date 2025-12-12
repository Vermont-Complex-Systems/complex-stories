<script lang="ts">
    import Spinner from '$lib/components/helpers/Spinner.svelte';
    import { Dashboard, Allotaxonograph } from 'allotaxonometer-ui';
    import Sidebar from './Sidebar.svelte';
    import Nav from './Nav.svelte';
    import { onMount } from 'svelte';
    import * as stateModule from '../sidebar-state.svelte.ts';

    import boys1895 from '../data/boys-1895.json'
    import boys1968 from '../data/boys-1968.json'

    // Create query using the state module
    const query = stateModule.createBabyNamesQuery();

    // Initial data load on mount (runs exactly once)
    onMount(() => {
        stateModule.loadData();
    });

    // Fetch locations on mount
    $effect(() => {
        stateModule.initializeAdapter();
    });

    // Auto-adjust periods when location changes and dates are out of range
    $effect(() => {
        const range = stateModule.derived.locationDateRange;

        // Adjust period1 if out of range
        if (stateModule.state.period1[0] < range.min || stateModule.state.period1[1] > range.max) {
            const periodLength = stateModule.state.period1[1] - stateModule.state.period1[0];
            const newStart = Math.max(range.min, Math.min(range.max - periodLength, stateModule.state.period1[0]));
            const newEnd = Math.min(range.max, newStart + periodLength);
            stateModule.state.period1 = [newStart, newEnd];
        }

        // Adjust period2 if out of range
        if (stateModule.state.period2[0] < range.min || stateModule.state.period2[1] > range.max) {
            const periodLength = stateModule.state.period2[1] - stateModule.state.period2[0];
            const newStart = Math.max(range.min, Math.min(range.max - periodLength, stateModule.state.period2[0]));
            const newEnd = Math.min(range.max, newStart + periodLength);
            stateModule.state.period2 = [newStart, newEnd];
        }
    });

    // Create Allotaxonograph instance reactively based on query data AND currentAlpha
    const instance = $derived(stateModule.getInstanceFromQuery(query.data));

    // Extract data properties as derived values
    const dat = $derived(instance?.dat);
    const barData = $derived(instance?.barData);
    const balanceData = $derived(instance?.balanceData);
    const maxlog10 = $derived(instance?.maxlog10);
    const divnorm = $derived(instance?.divnorm);
    const displayTitles = $derived(query.data?.title || ['System 1', 'System 2']);
    const me = $derived(instance?.me);
    const rtd = $derived(instance?.rtd);
    const isDataReady = $derived(!!query.data && !!instance);

    // Check if we got fewer results than requested
    const actualCounts = $derived(stateModule.getActualCounts(query.data));
    const showTopNWarning = $derived(stateModule.shouldShowTopNWarning(query.data, isDataReady));

    // Auto-dismiss warning after 5 seconds
    $effect(() => {
        if (showTopNWarning) {
            stateModule.state.warningDismissed = false;
            const timer = setTimeout(() => {
                stateModule.state.warningDismissed = true;
            }, 5000);
            return () => clearTimeout(timer);
        }
    });
</script>

<div class="app-container">
    <div class="layout">
        <aside class="sidebar-container">
            <Sidebar {query} {instance} {displayTitles} {me} {rtd} {isDataReady} {actualCounts} {showTopNWarning}
            />
        </aside>

        <main class="main-content">
            <Nav/>

            {#if query.isLoading && !query.data}
                <div class="main-loading">
                    <Spinner />
                    <p>Loading rust-wasm and baby names comparison...</p>
                </div>
            {:else if query.error}
                <!-- Fallback to static data when API fails -->
                {@const fallbackInstance = new Allotaxonograph(boys1895, boys1968, {
                    alpha: stateModule.derived.currentAlpha,
                    title: ['Boys 1895', 'Boys 1968']
                })}
                <Dashboard
                    dat={fallbackInstance.dat}
                    barData={fallbackInstance.barData}
                    balanceData={fallbackInstance.balanceData}
                    maxlog10={fallbackInstance.maxlog10}
                    divnorm={fallbackInstance.divnorm}
                    title={['Boys 1895', 'Boys 1968']}
                    alpha={stateModule.derived.currentAlpha}
                    WordshiftWidth={400}
                />
                <div class="error">
                    <p>Failed to load baby names data: babynames API is down. Falling back on static data.</p>
                </div>
            {:else if query.data}
                <Dashboard
                    {dat}
                    {barData}
                    {balanceData}
                    {maxlog10}
                    {divnorm}
                    title={displayTitles}
                    alpha={stateModule.derived.currentAlpha}
                    WordshiftWidth={400}
                />
            {/if}
        </main>
    </div>
</div>

<style>
    .app-container {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        z-index: 10;
        overflow: hidden;
    }

    .layout {
        display: flex;
        height: 100vh;
        width: 100vw;
        margin: 0;
        padding: 0;
    }

    .main-content {
        flex: 1;
        overflow: auto;
        background-color: var(--color-bg);
        max-width: none;
        margin: 0;
        padding: 5.5rem 0 0 0;
        transition: padding-left var(--transition-medium) ease;
    }
    
    .sidebar-container {
        flex-shrink: 0;
        width: 17rem;
        background-color: var(--color-input-bg);
        border-right: 1px solid var(--color-border);
        transition: width var(--transition-medium) ease;
        overflow: hidden;
    }


    .main-loading {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        height: 100%;
        gap: 1rem;
    } 

    .error {
        padding: 2rem;
        text-align: center;
        color: #ef4444;
    }

    /* Mobile */
    @media (max-width: 768px) {
        .layout {
            flex-direction: column;
        }

        .sidebar-container {
            width: 100% !important;
            height: auto;
            border-right: none;
            border-bottom: 1px solid var(--color-border);
        }
    }
</style>
