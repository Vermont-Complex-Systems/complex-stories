// Shared so the enable-audio control can sit in the story header while the
// sonification engine stays mounted alongside the visualization.
export const audio = $state({
	enabled: false,
	toggle: async () => {}
});
