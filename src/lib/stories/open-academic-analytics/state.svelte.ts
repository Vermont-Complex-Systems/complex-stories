export const uiState = $state({
    sidebarCollapsed: false,
    isDarkMode: false,
});


export function toggleSidebar() {
    uiState.sidebarCollapsed = !uiState.sidebarCollapsed;
}
