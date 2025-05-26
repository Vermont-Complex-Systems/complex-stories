<script>
  import { getStoryComponent } from '$lib/utils/storyRegistry.js';
  import Meta from '$lib/components/Meta.svelte';
  
  let { data } = $props();
  const { story, copyData } = data;
  
  const StoryComponent = getStoryComponent(story.slug);
</script>

<Meta 
  title={story.short}
  description={story.tease}
/>

{#if StoryComponent}
  <!-- Svelte 5 way: direct component usage -->
  <StoryComponent {story} data={copyData} />
{:else}
  <div class="error">
    <h2>Story Component Not Found</h2>
    <p>The story component for "{story.slug}" could not be loaded.</p>
  </div>
{/if}