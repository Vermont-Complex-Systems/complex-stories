<script lang="ts">
    import Spinner from '$lib/components/helpers/Spinner.svelte';
    import { Dashboard, Allotaxonograph } from 'allotaxonometer-ui';
    import Sidebar from './Sidebar.svelte';
    import Nav from './Nav.svelte';
    import { onMount } from 'svelte';
    import { createQuery } from '@tanstack/svelte-query';
    import { fileState, dashboardState } from '../sidebar-state.svelte.ts';
    import { getTopBabyNames } from '../allotax.remote.js';

    import boys1895 from '../data/boys-1895.json'
    import boys1968 from '../data/boys-1968.json'

    // Create query for baby names data
    const query = createQuery(() => ({
        queryKey: [
            'babynames',
            dashboardState.fetchedPeriod1[0], dashboardState.fetchedPeriod1[1],
            dashboardState.fetchedPeriod2[0], dashboardState.fetchedPeriod2[1],
            dashboardState.fetchedLocation,
            dashboardState.fetchedSex,
            dashboardState.fetchedTopN,
            fileState.hasUploadedFiles,
            !!fileState.uploadedSys1, !!fileState.uploadedSys2,
            JSON.stringify(fileState.uploadedTitle)
        ],
        queryFn: async () => {
            if (fileState.hasUploadedFiles) {
                const elem1 = fileState.uploadedSys1 || [];
                const elem2 = fileState.uploadedSys2 || [];
                return {
                    elem1,
                    elem2,
                    title: fileState.uploadedTitle
                };
            }

            const period1Str = `${dashboardState.fetchedPeriod1[0]},${dashboardState.fetchedPeriod1[1]}`;
            const period2Str = `${dashboardState.fetchedPeriod2[0]},${dashboardState.fetchedPeriod2[1]}`;

            const ngrams = await getTopBabyNames({
                dates: period1Str,
                dates2: period2Str,
                location: dashboardState.fetchedLocation,
                sex: dashboardState.fetchedSex,
                limit: dashboardState.fetchedTopN
            });

            const keys = Object.keys(ngrams);
            const elem1 = ngrams[keys[0]];
            const elem2 = ngrams[keys[1]];

            return {
                elem1,
                elem2,
                title: [`${dashboardState.fetchedPeriod1[0]}-${dashboardState.fetchedPeriod1[1]}`, `${dashboardState.fetchedPeriod2[0]}-${dashboardState.fetchedPeriod2[1]}`]
            };
        },
        enabled: true,
        staleTime: 5 * 60 * 1000, // 5 minutes
        gcTime: 10 * 60 * 1000, // 10 minutes
        placeholderData: (previousData) => previousData,
    }));

    // Initial data load on mount (runs exactly once)
    onMount(() => {
        dashboardState.loadData();
        dashboardState.initializeAdapter();
    });

    // Auto-adjust periods when location changes and dates are out of range
    $effect(() => {
        const range = dashboardState.dateRange;

        // Adjust period1 if out of range
        if (dashboardState.period1[0] < range.min || dashboardState.period1[1] > range.max) {
            const periodLength = dashboardState.period1[1] - dashboardState.period1[0];
            const newStart = Math.max(range.min, Math.min(range.max - periodLength, dashboardState.period1[0]));
            const newEnd = Math.min(range.max, newStart + periodLength);
            dashboardState.period1 = [newStart, newEnd];
        }

        // Adjust period2 if out of range
        if (dashboardState.period2[0] < range.min || dashboardState.period2[1] > range.max) {
            const periodLength = dashboardState.period2[1] - dashboardState.period2[0];
            const newStart = Math.max(range.min, Math.min(range.max - periodLength, dashboardState.period2[0]));
            const newEnd = Math.min(range.max, newStart + periodLength);
            dashboardState.period2 = [newStart, newEnd];
        }
    });

    // Create Allotaxonograph instance reactively based on query data AND currentAlpha
    const instance = $derived(
        query.data
            ? new Allotaxonograph(query.data.elem1, query.data.elem2, {
                alpha: dashboardState.currentAlpha,
                title: query.data.title
            })
            : new Allotaxonograph(boys1895, boys1968, {
                    alpha: dashboardState.currentAlpha,
                    title: ['Boys 1895', 'Boys 1968']
                })
    );

    // Extract data properties as derived values
    const displayTitles = $derived(query.data?.title || ['System 1', 'System 2']);
    const me = $derived(instance?.me);
    const rtd = $derived(instance?.rtd);
    const isDataReady = $derived(!!query.data && !!instance);
</script>

<div class="app-container">
    <div class="layout">
        <aside class="sidebar-container">
            <Sidebar {query} {instance} {displayTitles} {me} {rtd} {isDataReady}/>
        </aside>

        <main class="main-content">
            <Nav/>

            {#if query.isLoading && !instance}
                <div class="main-loading">
                    <Spinner />
                    <p>Loading rust-wasm and baby names comparison...</p>
                </div>
            {:else if instance}
                <Dashboard {...instance} />
                {#if query.error}
                    <div class="error">
                        <p>Failed to load baby names data: babynames API is down. Falling back on static data.</p>
                    </div>
                {/if}
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
