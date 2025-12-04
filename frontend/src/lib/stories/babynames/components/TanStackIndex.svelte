<script>
    import { Allotaxonograph } from 'allotaxonometer-ui';
    import { combElems, rank_turbulence_divergence, diamond_count, wordShift_dat, balanceDat } from 'allotaxonometer-ui';
    import { getTopNgrams } from '$lib/api/data.remote.js';
    import { createQuery } from '@tanstack/svelte-query'
    import { CalendarDate, parseDate } from "@internationalized/date";
    import AllotaxHeader from '$lib/components/AllotaxHeader.svelte';
    import Dashboard from '$lib/components/Dashboard.svelte';
    import WarningBanner from '$lib/components/WarningBanner.svelte';
    import LoadingSpinner from '$lib/components/LoadingSpinner.svelte';
    import * as d3 from 'd3';
    import { createUrlState } from '$lib/state/urlParams.svelte.js';


    const alphas = d3.range(0,18).map(v => +(v/12).toFixed(2)).concat([1, 2, 5, Infinity]);

    // Initialize reactive URL params with defaults in logical order
    const params = createUrlState({});

    // Set defaults in the order they appear in the UI
    if (!params.has('mode')) params.set('mode', 'dates');

    const mode = params.get('mode');

    if (mode === 'dates') {
        // Order: mode, country, date, date2, topN, alphaIndex
        if (!params.has('country')) params.set('country', 'United States');
        if (!params.has('date')) params.set('date', '2025-06-23');
        if (!params.has('date2')) params.set('date2', '2025-09-12');
        if (!params.has('topN')) params.set('topN', '10000');
        if (!params.has('alphaIndex')) params.set('alphaIndex', '7');
        params.delete('country2'); // Only one country in dates mode
    } else {
        // Order: mode, date, country, country2, topN, alphaIndex
        if (!params.has('date')) params.set('date', '2025-06-23');
        if (!params.has('country')) params.set('country', 'United States');
        if (!params.has('country2')) params.set('country2', 'United Kingdom');
        if (!params.has('topN')) params.set('topN', '10000');
        if (!params.has('alphaIndex')) params.set('alphaIndex', '7');
        params.delete('date2'); // Only one date in countries mode
    }

    // Derive reactive state from params
    let comparisonMode = $derived(params.get('mode'));
    let alphaIndex = $derived(parseInt(params.get('alphaIndex')));
    let date1 = $derived(parseDate(params.get('date')));
    let date2 = $derived(params.has('date2') ? parseDate(params.get('date2')) : date1);
    let country1 = $derived(params.get('country'));
    let country2 = $derived(params.get('country2') || country1);
    let topN = $derived(parseInt(params.get('topN')));

    let noDataWarning = $state(null);
    let lastValidData = $state(null);
    let lastValidDate1 = $state(null);
    let lastValidDate2 = $state(null);

    // Initialize lastValid dates once
    $effect(() => {
        if (!lastValidDate1) lastValidDate1 = date1;
        if (!lastValidDate2) lastValidDate2 = date2;
    });

    const query = createQuery(() => ({
        queryKey: ['allotax', comparisonMode, date1, date2, country1, country2, topN],
        enabled: !!(date1 && date2), // Only run query if both dates are set
        queryFn: async () => {
        let data, elem1, elem2, titles;

        // Time the FastAPI fetch
        const startFetch = performance.now();

       if (comparisonMode === 'dates') {
            data = await getTopNgrams({
                dates: [new Date(date1), new Date(date2)],
                countries: country1,
                topN
            });

            elem1 = data[new Date(date1).toISOString().split('T')[0] + 'T00:00:00'];
            elem2 = data[new Date(date2).toISOString().split('T')[0] + 'T00:00:00'];
            titles = [date1, date2];
        } else {
            // Compare two countries on the same date
            data = await getTopNgrams({
                dates: new Date(date1),
                countries: [country1, country2],
                topN
            });

            elem1 = data[country1];
            elem2 = data[country2];
            titles = [country1, country2];
        }

        const fetchDuration = performance.now() - startFetch;
        console.log(`⏱️  FastAPI fetch took ${fetchDuration.toFixed(2)}ms`);

      if (!elem1 || !elem2) {
          const missingData = [];
          if (!elem1) missingData.push(comparisonMode === 'dates' ? date1 : country1);
          if (!elem2) missingData.push(comparisonMode === 'dates' ? date2 : country2);

          const warningMsg = `No data available for: ${missingData.join(', ')}`;
          console.warn(`⚠️  ${warningMsg}`);
          noDataWarning = warningMsg;

          // Revert to last valid dates
          params.set('date1', `${lastValidDate1.year}-${String(lastValidDate1.month).padStart(2, '0')}-${String(lastValidDate1.day).padStart(2, '0')}`);
          if (comparisonMode === 'dates') {
              params.set('date2', `${lastValidDate2.year}-${String(lastValidDate2.month).padStart(2, '0')}-${String(lastValidDate2.day).padStart(2, '0')}`);
          }

          // Return lastValidData if available, otherwise throw
          if (lastValidData) {
              return lastValidData;
          }
          throw new Error(warningMsg);
      }

      // Clear warning and store valid dates on successful fetch
      noDataWarning = null;
      lastValidDate1 = date1;
      lastValidDate2 = date2;

      // Time the visualization creation (WASM computation)
      const startViz = performance.now();
      const instance = new Allotaxonograph(elem1, elem2, {
          alpha: alphas[alphaIndex],
          title: titles
      });
      const vizDuration = performance.now() - startViz;
      console.log(`⏱️  Visualization creation took ${vizDuration.toFixed(2)}ms`);
      console.log(`⏱️  Total query time: ${(fetchDuration + vizDuration).toFixed(2)}ms`);
      // Store as last valid data
      lastValidData = instance;

      return instance;
  },
        staleTime: 1000 * 60 * 10, // 10 minutes
        refetchOnWindowFocus: false,
        refetchOnMount: false,
        placeholderData: (previousData) => previousData,
        retry: false // Don't retry on missing data errors
    }));

    $effect(() => {
        if (query.data) {
            query.data.setAlpha(alphas[alphaIndex]);
        }
    });

    // Derived titles for display
    const displayTitles = $derived(
        comparisonMode === 'dates' ? [date1, date2] : [country1, country2]
    );

    // Extract data from instance (maintaining reactivity)
    const instance = $derived(query.data || lastValidData);
    const dat = $derived(instance?.dat);
    const barData = $derived(instance?.barData);
    const balanceData = $derived(instance?.balanceData);
    const maxlog10 = $derived(instance?.maxlog10);
    const divnorm = $derived(instance?.divnorm);
</script>

<AllotaxHeader
    {country1}
    {country2}
    {date1}
    {date2}
    {topN}
    {alphaIndex}
    {comparisonMode}
    {alphas}
    {params}
    currentAlpha={query.data ? query.data.alpha : alphas[alphaIndex]}
    topNgramsQuery={query}
/>

<WarningBanner bind:message={noDataWarning} />

{#if query.isLoading}
    <LoadingSpinner message={lastValidData ? 'Fetching data...' : 'Initializing WASM and fetching data...'} />
{:else if dat}
    <div class="dashboard-container">
        <Dashboard
            {dat}
            {barData}
            {balanceData}
            {maxlog10}
            {divnorm}
            title={displayTitles}
            alpha={alphas[alphaIndex]}
            WordshiftWidth={400}
            comparisonMode={comparisonMode}
            country1={country1}
            country2={country2}
            date1={new Date(date1).toISOString().split('T')[0]}
            date2={new Date(date2).toISOString().split('T')[0]}
        />
    </div>
{:else}
    <LoadingSpinner isError={true} />
{/if}


<style>
    :global(body) {
        margin: 0;
        padding: 0;
    }

    .dashboard-container {
        padding: 2rem;
        max-width: 1400px;
        margin: 0 auto;
    }
</style>