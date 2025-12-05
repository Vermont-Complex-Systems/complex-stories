<script>
    let {
        value = $bindable('united_states'),
        label = "Location",
        locations = [],
        isLoading = false,
        isError = false
    } = $props();

    function handleChange(event) {
        value = event.target.value;
    }

    // Get current location display name - computed each render
    function getCurrentLocationName() {
        if (!locations?.length) return value;
        const location = locations.find(l => l.code === value);
        return location?.name || value;
    }
</script>

<div class="location-selector">
    <div class="selector-header">
        <span class="selector-label">{label}</span>
    </div>

    <div class="selector-control">
        {#if isLoading}
            <div class="loading-dropdown">Loading locations...</div>
        {:else if isError}
            <div class="error-dropdown">Failed to load locations</div>
        {:else if locations.length > 0}
            <select
                {value}
                onchange={handleChange}
                class="location-dropdown"
            >
                {#each locations as location}
                    <option value={location.code}>
                        {location.name}
                    </option>
                {/each}
            </select>
        {/if}
    </div>
</div>

<style>
    .location-selector {
        display: flex;
        flex-direction: column;
        gap: 0.75rem;
        width: 100%;
    }

    .selector-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.5rem;
    }

    .selector-label {
        font-size: var(--12px, 0.75rem);
        font-weight: var(--font-weight-medium, 500);
        color: var(--color-text-primary);
    }

    .current-selection {
        font-size: var(--11px, 0.69rem);
        color: var(--color-text-secondary);
        font-weight: var(--font-weight-normal, 400);
    }

    .selector-control {
        position: relative;
    }

    .location-dropdown,
    .loading-dropdown,
    .error-dropdown {
        width: 100%;
        padding: 0.75rem 1rem;
        border: 1px solid var(--color-border);
        border-radius: 6px;
        font-size: 0.875rem;
        background-color: var(--color-bg);
        color: var(--color-text-primary);
    }

    .location-dropdown {
        cursor: pointer;
        appearance: none;
        background-image: url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 20 20'%3e%3cpath stroke='%236b7280' stroke-linecap='round' stroke-linejoin='round' stroke-width='1.5' d='m6 8 4 4 4-4'/%3e%3c/svg%3e");
        background-position: right 0.75rem center;
        background-repeat: no-repeat;
        background-size: 1rem;
        transition: all 0.15s ease;
    }

    .location-dropdown:hover {
        border-color: var(--color-good-blue, #3b82f6);
        box-shadow: 0 0 0 1px rgba(59, 130, 246, 0.1);
    }

    .location-dropdown:focus {
        outline: none;
        border-color: var(--color-good-blue, #3b82f6);
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
    }

    .loading-dropdown {
        opacity: 0.6;
        font-style: italic;
    }

    .error-dropdown {
        color: #ef4444;
        border-color: #ef4444;
    }

    /* Mobile responsive */
    @media (max-width: 768px) {
        .location-dropdown,
        .loading-dropdown,
        .error-dropdown {
            padding: 1rem;
            font-size: 1rem;
        }
    }
</style>