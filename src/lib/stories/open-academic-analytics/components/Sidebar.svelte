<script>
    import { Accordion, Button } from "bits-ui";
    import { User, Palette, Users, RotateCcw, UserCheck } from "@lucide/svelte";
    import { uiState, toggleSidebar, resetDashboardFilters } from '../state.svelte.ts';
    
    import SelectAuthors from './sidebar/SelectAuthors.svelte';
    import AuthorAgeFilter from './sidebar/AuthorAgeFilter.svelte';
    import DataInfo from './sidebar/DataInfo.svelte';
    import ColorModeFilter from './sidebar/ColorModeFilter.svelte';
    
    let { paperData = [], coauthorData = [], availableAuthors = [] } = $props();

    let availableCoauthors = $derived.by(() => {
        if (!coauthorData || coauthorData.length === 0) return [];
        // Get unique coauthor names (not IDs) from coauthor data
        const coauthors = [...new Set(coauthorData.map(c => c.coauth_name).filter(Boolean))];
        return coauthors.sort().slice(0, 50); // Increased limit and sorted
    });

</script>

<div class="sidebar-content">
    <div class="sidebar-header">
        {#if !uiState.sidebarCollapsed}
            <h2 class="sidebar-title">Open Academic Analytics</h2>
        {/if}
        <Button.Root onclick={toggleSidebar} variant="ghost" size="sm" class="sidebar-toggle">
            <!-- Desktop: horizontal chevron, Mobile: vertical chevron -->
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="chevron-desktop">
                {#if uiState.sidebarCollapsed}
                    <path d="M9 18l6-6-6-6"/>
                {:else}
                    <path d="M15 18l-6-6 6-6"/>
                {/if}
            </svg>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="chevron-mobile">
                {#if uiState.sidebarCollapsed}
                    <path d="M6 9l6 6 6-6"/>
                {:else}
                    <path d="M18 15l-6-6-6 6"/>
                {/if}
            </svg>
        </Button.Root>
    </div>
    
    {#if !uiState.sidebarCollapsed}
        <div class="sidebar-body">
            <Accordion.Root type="multiple" value={["author-select", "filters", "data"]} class="accordion">
                <AuthorAgeFilter {availableAuthors} />
                <SelectAuthors {availableAuthors} />
                <ColorModeFilter />
                <DataInfo {paperData} {coauthorData} {availableCoauthors} />
            </Accordion.Root>
            <div class="interaction-help">
                <p class="data-info">
                    Training dataset for the bayesian change point analysis available <a href="https://huggingface.co/datasets/Vermont-Complex-Systems/training_data/viewer?views%5B%5D=train">here</a>.
                </p>
            </div>
            <!-- Reset Button -->
            <div class="reset-section">
                <Button.Root onclick={resetDashboardFilters} variant="outline" size="sm" class="reset-button">
                    <RotateCcw size={14} />
                    Reset Filters
                </Button.Root>
            </div>
        </div>
    {:else}
        <div class="sidebar-collapsed">
            <div class="collapsed-item" title="Select Author">
                <UserCheck size={18} />
            </div>
            <div class="collapsed-item" title="Highlight Author">
                <User size={18} />
            </div>
            <div class="collapsed-item" title="Color Mode">
                <Palette size={18} />
            </div>
            <div class="collapsed-item" title="Highlight Coauthor">
                <Users size={18} />
            </div>
            <div class="collapsed-item" title="Dataset Info">📊</div>
        </div>
    {/if}
</div>

<style>
    .interaction-help {
        text-align: center;
    }

    .data-info {
        font-size: var(--font-size-xsmall);
        color: var(--color-secondary-gray);
        margin: 0;
        line-height: 1.3;
    }
        
    .sidebar-content {
        height: 100%;
        display: flex;
        flex-direction: column;
        min-width: 0;
        overflow: hidden;
        max-width: 100%;
    }

    .sidebar-header {
        padding: 1.5rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 2rem;
        border-bottom: 1px solid var(--color-border);
        min-height: 80px;
        flex-shrink: 0;
        min-width: 0;
        overflow: hidden;
        max-width: 100%;
    }

    .sidebar-content:has(.sidebar-collapsed) .sidebar-header,

    .sidebar-title {
        font-size: var(--font-size-small);
        font-weight: var(--font-weight-bold);
        margin: 0;
        color: var(--color-fg);
        font-family: var(--font-body);
    }

    .sidebar-body {
        padding: 1.5rem;
        flex: 1;
        display: flex;
        flex-direction: column;
        gap: 2rem;
        overflow-y: auto;
        overflow-x: hidden;
        max-width: 100%;
    }

    .sidebar-collapsed {
        padding: 1rem 0.5rem;
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 1rem;
        flex: 1;
    }

    .collapsed-item {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 0.25rem;
        padding: 0.5rem;
        border-radius: var(--border-radius);
        transition: background-color var(--transition-medium) ease;
        cursor: pointer;
    }

    .collapsed-item:hover {
        background-color: var(--color-gray-200);
    }

    :global(.dark) .collapsed-item:hover {
        background-color: var(--color-gray-700);
    }

    /* Chevron visibility - show desktop by default */
    .chevron-desktop {
        display: block;
    }

    .chevron-mobile {
        display: none;
    }

    :global(.accordion) {
        width: 100%;
    }

    :global(.accordion-trigger) {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        width: 100%;
        padding: 0.75rem;
        font-size: var(--font-size-small);
        font-weight: var(--font-weight-medium);
        color: var(--color-fg);
        background: transparent;
        border: none;
        border-radius: var(--border-radius);
        transition: background-color var(--transition-medium) ease;
        cursor: pointer;
    }

    :global(.accordion-trigger:hover) {
        background-color: var(--color-gray-100);
    }

    :global(.dark .accordion-trigger:hover) {
        background-color: var(--color-gray-800);
    }

    :global(.accordion-content) {
        padding: 0 0.75rem 1rem 0.75rem;
    }

    .reset-section {
        padding-top: 1rem;
        border-top: 1px solid var(--color-border);
    }

    :global(.reset-button) {
        width: 100%;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0.5rem;
    }

    :global(.sidebar-toggle) {
        flex-shrink: 0;
    }

    :global([data-separator-root]) {
        /* margin-top: 1.2rem; */
        /* margin-bottom: 1.2rem; */
        flex-shrink: 0;
        height: 1px;
        width: 100%;
    }

    /* Mobile styles */
    @media (max-width: 768px) {
        .sidebar-header {
            padding: 1rem;
            background: var(--color-input-bg);
            border-bottom: 1px solid var(--color-border);
        }
        
        :global(.sidebar-toggle) {
            padding: 0.75rem !important;
        }

        /* Switch chevron visibility on mobile */
        .chevron-desktop {
            display: none;
        }

        .chevron-mobile {
            display: block;
        }

        .sidebar-collapsed {
            display: none; /* Hide collapsed icons on mobile */
        }
    }
</style>