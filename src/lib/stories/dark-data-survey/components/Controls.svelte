<script>
    let { 
        isInteractivePhase, 
        selectedCategory, 
        selectedValue, 
        categories, 
        getValuesForCategory, 
        currentCategory, 
        currentValue 
    } = $props();
</script>

{#if isInteractivePhase}
    <div class="controls">
        <label>
            Category:
            <select bind:value={selectedCategory}>
                {#each categories as category}
                    <option value={category}>{category}</option>
                {/each}
            </select>
        </label>
        
        <label>
            Value:
            <select bind:value={selectedValue}>
                {#each getValuesForCategory(selectedCategory) as value}
                    <option value={value.toString()}>{value}</option>
                {/each}
            </select>
        </label>
    </div>
{:else}
    <div class="scrolly-info">
        <p>Currently showing: {currentCategory} = {currentValue}</p>
    </div>
{/if}

<style>
    .controls {
        display: flex;
        gap: 1rem;
        margin-bottom: 1rem;
        padding: 1rem;
        background: rgba(255, 255, 255, 0.9);
        border-radius: 8px;
        pointer-events: auto;
        position: relative;
        z-index: 1000;
    }
    
    .controls label {
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
    }
    
    .controls select {
        padding: 0.5rem;
        border: 1px solid #ccc;
        border-radius: 4px;
    }
    
    .scrolly-info {
        padding: 1rem;
        text-align: center;
        font-weight: 500;
        color: var(--color-secondary-gray);
    }
</style>