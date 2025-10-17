<script>
	import { previewDataset } from '../preview.remote.js';
	import { page } from '$app/state';
	import DatasetPreview from "$lib/components/DatasetPreview.svelte"
	import Spinner from "$lib/components/helpers/Spinner.svelte"
</script>

{#await previewDataset(page.params.slug)}
	<Spinner text="loading data..." />
{:then dataset} 
	<DatasetPreview {dataset}/>
{/await}