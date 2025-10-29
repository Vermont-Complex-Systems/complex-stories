<script>
  import { getStoryComponent } from '$lib/utils/storyRegistry.js';
  // import Meta from '$lib/components/Meta.svelte';
  
  let { data } = $props();
  const { story, copyData } = data;
  
  const StoryComponent = getStoryComponent(story.slug);
</script>

<!-- <Meta 
  title={story.short}
  description={story.tease}
/> -->

{#if StoryComponent}
  <StoryComponent {story} data={copyData} />
{/if}