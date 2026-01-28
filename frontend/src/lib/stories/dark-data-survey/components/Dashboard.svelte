<script>
    import TrustEvo from './TrustEvo.svelte';
    import TrustDistributionChart from './TrustDistributionChart.svelte';
    import { scaleSequential } from 'd3-scale';
    import { interpolateRdYlGn } from 'd3-scale-chromatic';
    import { extent } from 'd3-array';

    let { data, width, height } = $props();

    // Interactive controls state
    let selectedDemCategory = $state('Dem_Gender_Other');
    let highlightCircle = $state('');

    function handleInstitutionClick(institution) {
        // Toggle: if clicking the same institution, deselect it
        highlightCircle = highlightCircle === institution ? '' : institution;
    }


    // Filter circles for display
    let filteredCircles = $derived.by(() =>
        data.filter((c) => c.Demographic == selectedDemCategory
        )
    )

    $inspect(filteredCircles);


    const zScale = $derived(scaleSequential(interpolateRdYlGn).domain(extent(data.map(d=>d.Average_Trust))));

    // Category options
    const categoryOptions = [
        { value: 'overall_average', label: 'Overall Average' },
        { value: 'orientation_ord', label: 'Sexual Orientation' },
        { value: 'race_ord', label: 'Race' },
        { value: 'gender_ord', label: 'Gender' },
        { value: 'multi_platform_ord', label: 'Platform Usage' },
        { value: 'ACES_Compound', label: 'Adverse Childhood Experiences' }
    ];

    // Value options based on selected category
    const valueOptions = $derived.by(() => {
        switch (selectedDemCategory) {
            case 'Dem_Gender_Other':
                return [
                    { value: '0.0', label: 'Straight' },
                    { value: '1.0', label: 'Bisexual' },
                    { value: '2.0', label: 'Gay' },
                    { value: '3.0', label: 'Other' }
                ];
            case 'race_ord':
                return [
                    { value: '0.0', label: 'White' },
                    { value: '1.0', label: 'Mixed' },
                    { value: '2.0', label: 'POC' }
                ];
            case 'gender_ord':
                return [
                    { value: '0.0', label: 'Women' },
                    { value: '1.0', label: 'Men' },
                    { value: '2.0', label: 'Other' }
                ];
            case 'multi_platform_ord':
                return [
                    { value: '1.0', label: '1 Platform' },
                    { value: '2.0', label: '2 Platforms' },
                    { value: '3.0', label: '3 Platforms' },
                    { value: '4.0', label: '4 Platforms' },
                    { value: '5.0', label: '5 Platforms' }
                ];
            case 'ACES_Compound':
                return Array.from({ length: 13 }, (_, i) => ({
                    value: `${i}.0`,
                    label: i === 1 ? '1 ACE' : `${i} ACEs`
                }));
            case 'overall_average':
                return [{ value: '1.0', label: 'All Users' }];
            default:
                return [{ value: '1.0', label: 'Default' }];
        }
    });

    // Update selectedValue when category changes
    $effect(() => {
        const firstOption = valueOptions[0];
        if (firstOption) {
            selectedValue = firstOption.value;
        }
    });
</script>

<div class="dashboard">
    <div class="dashboard-header">
        <h2>Explore the Data</h2>
        <p>Click on an institution in the chart to highlight it.</p>
    </div>

    <div class="visualization-container">
        <div class="left-panel">
        </div>

        <div class="center-viz">
            <TrustEvo
                scrollyIndex={undefined}
                selectedDemographic={selectedDemCategory}
                {width}
                {height}
                isStorySection={false}
                isDashboard={true}
                storySection={null}
                conclusionVisible={false}
                externalCategory={selectedDemCategory}
                externalHighlight={highlightCircle}
                onInstitutionClick={undefined} />
        </div>

        <div class="right-panel">
            <TrustDistributionChart
                filteredData={filteredCircles}
                colorScale={zScale}
                {highlightCircle}
                onInstitutionClick={handleInstitutionClick}
                isDashboard={true} />
        </div>
    </div>

    <div class="controls-panel">
        <div class="control-group">
            <label for="category-select">Demographic Category:</label>
            <select id="category-select" bind:value={selectedDemCategory}>
                {#each categoryOptions as option}
                    <option value={option.value}>{option.label}</option>
                {/each}
            </select>
        </div>

        <div class="control-group">
            <label for="value-select">Value:</label>
            <select id="value-select" bind:value={selectedDemCategory}>
                {#each valueOptions as option}
                    <option value={option.value}>{option.label}</option>
                {/each}
            </select>
        </div>
    </div>
</div>

<style>
    .dashboard {
        width: 100%;
        margin: 2rem 0;
    }

    .dashboard-header {
        text-align: center;
        margin-bottom: 0;
    }

    .dashboard-header h2 {
        font-size: 2rem;
        margin-bottom: 0.5rem;
    }

    .dashboard-header p {
        font-size: 1.1rem;
        color: #666;
    }

    .controls-panel {
        padding: 1.5rem;
        display: flex;
        gap: 2rem;
        flex-wrap: wrap;
        justify-content: center;
        align-items: flex-end;
        position: relative;
        z-index: 1000;
        pointer-events: auto;
    }

    .control-group {
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
        min-width: 200px;
    }

    .control-group label {
        font-weight: 600;
        font-size: 0.9rem;
        color: whitesmoke;
    }

    .control-group select {
        padding: 0.5rem;
        border: 1px solid #ccc;
        border-radius: 4px;
        font-size: 1rem;
        background: white;
        cursor: pointer;
    }

    .control-group select:hover {
        border-color: #999;
    }

    .control-group select:focus {
        outline: none;
        border-color: #0891b2;
        box-shadow: 0 0 0 2px rgba(8, 145, 178, 0.1);
    }

    .visualization-container {
        position: relative;
        width: 100vw !important;
        margin-left: 50%;
        transform: translateX(-50%);
        display: flex;
        gap: 2rem;
        align-items: start;
        padding: 0 2rem;
        box-sizing: border-box;
    }

    .left-panel {
        flex-shrink: 0;
        width: 350px;
        align-self: center;
        transform: translateY(55%);
    }

    .center-viz {
        flex: 1;
        min-width: 0;
    }

    .right-panel {
        flex-shrink: 0;
        width: 350px;
        align-self: flex-end;
        transform: translateY(44%);
    }
</style>
