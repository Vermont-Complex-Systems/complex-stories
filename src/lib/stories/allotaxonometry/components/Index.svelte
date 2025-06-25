<script>
    import Nav from './Nav.svelte';
    import Sidebar from './Sidebar.svelte';
    import Allotaxonograph from './Allotaxonograph.svelte';
    import { uiState } from '../state.svelte.ts';
</script>

<div class="dashboard-app">
    <Nav />
    
    <div class="app-container">
        <div class="layout">
            <aside class="sidebar-container {uiState.sidebarCollapsed ? 'collapsed' : ''}">
                <Sidebar />
            </aside>
            
            <main class="main-content {uiState.sidebarCollapsed ? 'collapsed-sidebar' : ''}">
                <Allotaxonograph />
            </main>
        </div>
    </div>
</div>

<style>
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
        padding: 4.5rem 0 0 0;
        transition: padding-left var(--transition-medium) ease;
    }

    .main-content.collapsed-sidebar {
        padding-left: 0;
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
        }

        .main-content.collapsed-sidebar {
            padding-left: 0;
        }
    }
</style>