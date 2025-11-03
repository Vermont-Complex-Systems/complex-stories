<script>
    import { Accordion, Button } from "bits-ui";
    import { User, Palette, Users, RotateCcw, UserCheck, Search, ChevronRight, ChevronLeft, ChevronDown, ChevronUp, Info } from "@lucide/svelte";
    import { uiState, dashboardState, toggleSidebar } from '$stories/open-academic-analytics/state.svelte.js';
    import { base } from "$app/paths";
    
    import SelectAuthors from './sidebar/SelectAuthors.svelte';
    import AuthorAgeFilter from './sidebar/AuthorAgeFilter.svelte';
    import ResearchGroupFilter from './sidebar/ResearchGroupFilter.svelte';
    import DataInfo from './sidebar/DataInfo.svelte';
    import CoauthorNodeColor from './sidebar/NodeColor.coauthor.svelte';
    import PaperNodeSize from './sidebar/NodeSize.paper.svelte';
    import ChangePointChart from './sidebar/ChangePointChart.svelte';
    import Toggle from '$lib/components/helpers/SimpleToggle.svelte';
    import Methodology from './sidebar/Methodology.svelte';
    
</script>

<div class="sidebar-content">
    <div class="sidebar-header">
        {#if !uiState.sidebarCollapsed}
            <h2 class="sidebar-title">Open Academic Analytics</h2>
        {/if}
        <Button.Root onclick={toggleSidebar} variant="ghost" size="sm" class="sidebar-toggle">
            <!-- Desktop: horizontal chevron, Mobile: vertical chevron -->
            <div class="chevron-desktop">
                {#if uiState.sidebarCollapsed}
                    <ChevronRight size={16} />
                {:else}
                    <ChevronLeft size={16} />
                {/if}
            </div>
            <div class="chevron-mobile">
                {#if uiState.sidebarCollapsed}
                    <ChevronDown size={16} />
                {:else}
                    <ChevronUp size={16} />
                {/if}
            </div>
        </Button.Root>
    </div>
    
    {#if !uiState.sidebarCollapsed}
        <div class="sidebar-body">
            <!-- Global Filters Section (Always Visible) -->
            <DataInfo />
            <div class="global-filters-section">
                <div class="section-header-static">
                    <Search size={16} />
                    <span class="section-title">Global Filters</span>
                </div>
                <div class="filters-content">
                    <ResearchGroupFilter />

                    <Methodology
                        text="We manually annotated who has research groups or not based on whether authors have a website displaying their group status. You can preview annotated dataset <a href='{base}/datasets/academic-research-groups'>here</a>."
                    />

                    <AuthorAgeFilter />
                    <!-- Change Point Analysis Chart -->
                    <ChangePointChart
                        authorName={dashboardState.selectedAuthor}
                        visible={!!dashboardState.selectedAuthor}
                    />
                    
                    {#if dashboardState.selectedAuthor}
                        <Methodology
                            text="Bayesian change point analysis identifies shifts in collaboration patterns with younger coauthors over time. The dashed line shows the estimated changing rate. Training dataset for the bayesian change point analysis available <a href='https://huggingface.co/datasets/Vermont-Complex-Systems/training_data/viewer?views%5B%5D=train'>here</a>."
                        />
                    {/if}
                </div>
            </div>

            <!-- Individual Widgets Section (Always Visible) -->
            <div class="individual-widgets-section">
                <div class="section-header-static">
                    <Users size={16} />
                    <span class="section-title">Individual Widgets</span>
                </div>
                <div class="widgets-content">
                    <SelectAuthors />
                    <CoauthorNodeColor />

                    <Methodology
                        text={dashboardState.coauthorNodeColor === 'age_diff'
                            ? 'Relative age estimates from <a href="https://openalex.org/">OpenAlex</a> may be noisy due to name disambiguation and first publication year inference.'
                            : dashboardState.coauthorNodeColor === 'institutions'
                                ? 'Color shows top 10 institutions by frequency. All nodes are colored by their institution (determined by simple majority of publications yearly).'
                                : 'Color shows top 10 shared institutions by frequency. All nodes are colored by their shared institution (determined by simple majority of publications yearly).'}
                    />

                    <PaperNodeSize />
                    
                    <!-- Additional Settings -->
                    <div class="additional-settings-widget">
                        <div class="widget-header">
                            <RotateCcw size={14} />
                            <span class="widget-title">Filter out papers with > 25 coauthors?</span>
                        </div>
                        <div class="setting-content">
                            <div class="setting-item">
                                <Toggle bind:isTrue={dashboardState.filterBigPapers} onText="Yes" offText="No"/>
                            </div>
                        </div>
                    </div>
                </div>
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

    :global(.accordion-item) {
        border-bottom: 1px solid var(--color-border);
        margin-bottom: 0.5rem;
    }

    :global(.accordion-item:last-child) {
        border-bottom: none;
        margin-bottom: 0;
    }

    :global(.section-trigger) {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 0.5rem;
        width: 100%;
        padding: 1rem 0.75rem;
        font-size: var(--font-size-small);
        font-weight: var(--font-weight-medium);
        color: var(--color-fg);
        background: var(--color-gray-50);
        border: none;
        border-radius: var(--border-radius);
        transition: background-color var(--transition-medium) ease;
        cursor: pointer;
    }


    .global-filters-section {
        margin-top: 0.25rem;
        margin-bottom: 0.5rem;
    }

    .section-header-static {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.75rem;
        margin-bottom: 1rem;
        font-size: var(--font-size-small);
        font-weight: var(--font-weight-medium);
        color: var(--color-fg);
        background: var(--color-gray-50);
        border-radius: var(--border-radius);
    }

    :global(.dark) .section-header-static {
        background: var(--color-gray-800);
    }

    .filters-content {
        padding: 0 0.75rem;
    }

    .individual-widgets-section {
        margin-bottom: 0.5rem;
    }

    .widgets-content {
        padding: 0 0.75rem;
    }

    .additional-settings-widget {
        margin-bottom: 1rem;
    }

    .additional-settings-widget .widget-header {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        margin-bottom: 0.5rem;
        padding-bottom: 0.25rem;
        border-bottom: 1px solid var(--color-border);
    }

    .additional-settings-widget .widget-title {
        font-size: var(--font-size-xsmall);
        font-weight: var(--font-weight-medium);
        color: var(--color-fg);
    }

    .setting-content {
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
    }

    :global(.section-trigger:hover) {
        background-color: var(--color-gray-100);
    }

    :global(.dark .section-trigger) {
        background: var(--color-gray-800);
    }

    :global(.dark .section-trigger:hover) {
        background-color: var(--color-gray-700);
    }

    :global(.accordion-content) {
        padding: 0.5rem 0.75rem 1rem 0.75rem;
    }

    :global(.accordion-icon) {
        flex-shrink: 0;
        transition: transform 0.2s ease;
    }

    :global([data-state="open"] .accordion-icon) {
        transform: rotate(180deg);
    }

    .setting-item {
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
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
        .sidebar-content {
            height: 100vh;
            max-height: 100vh;
        }

        .sidebar-header {
            padding: 1rem;
            background: var(--color-input-bg);
            border-bottom: 1px solid var(--color-border);
        }

        .sidebar-body {
            padding: 1rem;
            height: calc(100vh - 80px); /* Subtract header height */
            max-height: calc(100vh - 80px);
            overflow-y: auto;
            overflow-x: hidden;
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