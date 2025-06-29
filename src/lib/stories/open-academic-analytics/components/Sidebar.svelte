<script>
    import { Accordion, Button, Separator } from "bits-ui";
    import { User, Palette, Users, RotateCcw, UserCheck } from "@lucide/svelte";
    import { dashboardState, uiState, toggleSidebar, resetDashboardFilters } from '../state.svelte.ts';

    let { paperData = [], coauthorData = [], availableAuthors = [] } = $props();
    
    // Available options for filters (based on currently selected author's data)
    let availableHighlightAuthors = $derived.by(() => {
        if (!paperData || paperData.length === 0) return [];
        const authors = [...new Set(paperData.map(p => p.ego_aid).filter(Boolean))];
        return authors.slice(0, 20);
    });

    let availableCoauthors = $derived.by(() => {
        if (!coauthorData || coauthorData.length === 0) return [];
        const coauthors = [...new Set(coauthorData.map(c => c.coauth_aid).filter(Boolean))];
        return coauthors.slice(0, 20);
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
                
                <!-- Author Selection Filter -->
                <Accordion.Item value="author-select">
                    <Accordion.Header>
                        <Accordion.Trigger class="accordion-trigger">
                            <UserCheck size={16} />
                            Select Author
                        </Accordion.Trigger>
                    </Accordion.Header>
                    <Accordion.Content class="accordion-content">
                        <div class="control-section">
                            <select bind:value={dashboardState.selectedAuthor} class="filter-select">
                                {#each availableAuthors as author}
                                    <option value={author}>{author}</option>
                                {/each}
                            </select>
                            <p class="filter-info">This filters all data to show only this author's papers and collaborations.</p>
                        </div>
                    </Accordion.Content>
                </Accordion.Item>

                <Separator.Root />
                
                <!-- Highlight Author Filter -->
                <Accordion.Item value="highlight-author">
                    <Accordion.Header>
                        <Accordion.Trigger class="accordion-trigger">
                            <User size={16} />
                            Highlight Author
                        </Accordion.Trigger>
                    </Accordion.Header>
                    <Accordion.Content class="accordion-content">
                        <div class="control-section">
                            <select bind:value={dashboardState.highlightedAuthor} class="filter-select">
                                <option value={null}>None</option>
                                {#each availableHighlightAuthors as author}
                                    <option value={author}>{author}</option>
                                {/each}
                            </select>
                        </div>
                    </Accordion.Content>
                </Accordion.Item>

                <Separator.Root />

                <!-- Color Mode Filter -->
                <Accordion.Item value="color-mode">
                    <Accordion.Header>
                        <Accordion.Trigger class="accordion-trigger">
                            <Palette size={16} />
                            Color Mode
                        </Accordion.Trigger>
                    </Accordion.Header>
                    <Accordion.Content class="accordion-content">
                        <div class="control-section">
                            <select bind:value={dashboardState.colorMode} class="filter-select">
                                <option value="age_diff">Age Difference</option>
                                <option value="acquaintance">Acquaintance Type</option>
                            </select>
                        </div>
                    </Accordion.Content>
                </Accordion.Item>

                <Separator.Root />

                <!-- Highlight Coauthor Filter -->
                <Accordion.Item value="highlight-coauthor">
                    <Accordion.Header>
                        <Accordion.Trigger class="accordion-trigger">
                            <Users size={16} />
                            Highlight Coauthor
                        </Accordion.Trigger>
                    </Accordion.Header>
                    <Accordion.Content class="accordion-content">
                        <div class="control-section">
                            <select bind:value={dashboardState.highlightedCoauthor} class="filter-select">
                                <option value={null}>None</option>
                                {#each availableCoauthors as coauthor}
                                    <option value={coauthor}>{coauthor}</option>
                                {/each}
                            </select>
                        </div>
                    </Accordion.Content>
                </Accordion.Item>

                <Separator.Root />

                <!-- Dataset Info -->
                <Accordion.Item value="data">
                    <Accordion.Header>
                        <Accordion.Trigger class="accordion-trigger">
                            📈 Dataset Info
                        </Accordion.Trigger>
                    </Accordion.Header>
                    <Accordion.Content class="accordion-content">
                        <div class="control-section">
                            <div class="data-stats">
                                <div class="stat-row">
                                    <span class="stat-label">Papers:</span>
                                    <span class="stat-value">{paperData?.length || 0}</span>
                                </div>
                                <div class="stat-row">
                                    <span class="stat-label">Collaborations:</span>
                                    <span class="stat-value">{coauthorData?.length || 0}</span>
                                </div>
                            </div>
                        </div>
                    </Accordion.Content>
                </Accordion.Item>

            </Accordion.Root>

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
    .sidebar-header:has(+ * .sidebar-collapsed) {
        padding: 1rem;
        justify-content: center;
    }

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

    .control-section {
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
    }

    .filter-select {
        padding: 0.5rem;
        border: 1px solid var(--color-border);
        border-radius: var(--border-radius);
        background: var(--color-bg);
        color: var(--color-fg);
        font-size: var(--font-size-small);
        width: 100%;
    }

    .filter-select:focus {
        outline: none;
        border-color: var(--color-good-blue);
    }

    .filter-info {
        font-size: var(--font-size-xsmall);
        color: var(--color-secondary-gray);
        margin: 0.5rem 0 0 0;
        font-style: italic;
        line-height: 1.3;
    }

    .data-stats {
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
    }

    .stat-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: var(--font-size-small);
    }

    .stat-label {
        color: var(--color-secondary-gray);
        font-weight: var(--font-weight-medium);
    }

    .stat-value {
        color: var(--color-fg);
        font-weight: var(--font-weight-bold);
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
        margin-top: 1.2rem;
        margin-bottom: 1.2rem;
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