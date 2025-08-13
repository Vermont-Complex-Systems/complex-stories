<script>
    import * as d3 from 'd3';
    import DataTable from '$lib/components/helpers/NiceTable.svelte';
    import Spinner from '$lib/components/helpers/Spinner.svelte'
    import {  dashboardState, uiState, data, initializeApp, loadSelectedAuthor } from './state.svelte.js';
    import Dashboard from './Dashboard.svelte';
    import Nav from './Nav.svelte';
    import Sidebar from './Sidebar.svelte';
    
    // Initialize on component mount
    initializeApp();

    // Auto-load data when selected author or changes
    $effect(() => {
        if (dashboardState.selectedAuthor && !data.isInitializing) {
            loadSelectedAuthor();
        }
    });
</script>

<div class="dashboard-app">    
    <div class="app-container">
        <div class="layout">
            {#if data.isInitializing}
                <div class="loading-container">
                    <Spinner />
                </div>
            {:else if data.error}
                <div class="error-container">
                    <p>Error: {data.error}</p>
                    <button onclick={() => initializeApp()}>Retry</button>
                </div>
            {:else}
                <aside class="sidebar-container {uiState.sidebarCollapsed ? 'collapsed' : ''}">
                    <Sidebar />
                </aside>
                
                <main class="main-content {uiState.sidebarCollapsed ? 'collapsed-sidebar' : ''}">
                    <Nav />
                    
                    {#if data.isLoadingAuthor}
                        <div class="author-loading">
                            <p>Loading data for {dashboardState.selectedAuthor}...</p>
                        </div>
                    {/if}
                    
                    <Dashboard />
                    
                    
                    {#if uiState.debug == true}
                        <h1>Paper table</h1>
                        <DataTable data={data.paper?.filter(d=>d.ego_display_name === dashboardState.selectedAuthor).slice(0,5)}/>
                        
                        <h1>Coauthor table</h1>
                        <DataTable data={data.coauthor?.filter(d=>d.ego_display_name === dashboardState.selectedAuthor).slice(0,5)}/>
                    {/if}
                </main>    
            {/if}    
        </div>    
    </div>    
</div>    


<style>

    .loading-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        height: 100vh;
        margin: 0;
        padding: 0;
        gap: 1rem;
        box-sizing: border-box;
    }

    /* Story-specific global reset */
    .dashboard-app * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
        font-family: "EB Garamond", serif;
    }

    .dashboard-app {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background-color: var(--color-bg);
        color: var(--color-fg);
        z-index: 1000;
        overflow: hidden;
    }

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

    .sidebar-container {
        flex-shrink: 0;
        width: 17rem;
        background-color: var(--color-input-bg);
        border-right: 1px solid var(--color-border);
        transition: width var(--transition-medium) ease;
        overflow: hidden;
    }

    .sidebar-container.collapsed {
        width: 5rem;
    }

    .main-content {
        flex: 1;
        overflow: auto;
        background-color: var(--color-bg);
        max-width: none;
        margin: 0;
        padding: 2rem;
        transition: padding-left var(--transition-medium) ease;
    }

    .main-content.collapsed-sidebar {
        padding-left: 2rem;
    }
    
    .loading-container, .error-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        height: 100vh;
        width: 100vw;
        gap: 1rem;
    }

    .error-container button {
        padding: 0.5rem 1rem;
        background: var(--color-button-bg);
        color: var(--color-button-fg);
        border: none;
        border-radius: 4px;
        cursor: pointer;
    }

    /* Responsive */
    @media (max-width: 768px) {
        .layout {
            flex-direction: column;
        }
        
        .sidebar-container {
            width: 100% !important;
            height: auto;
            border-right: none;
            border-bottom: 1px solid var(--color-border);
            max-height: none;
            transition: max-height var(--transition-medium) ease;
        }

        .sidebar-container.collapsed {
            max-height: 80px; /* Just show the header */
            overflow: hidden;
        }

        .main-content,
        .main-content.collapsed-sidebar {
            padding: 1rem;
        }
    }
</style>