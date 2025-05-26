<script>
  import { getStoryComponent } from '$lib/utils/storyRegistry.js';
  import Meta from '$lib/components/Meta.svelte';
  
  let { data } = $props();
  console.log('Page data:', data);
  
  const { story, copyData } = data;
  console.log('Story:', story);
  console.log('Copy data:', copyData);
  
  const StoryComponent = getStoryComponent(story.slug);
  console.log('Story component:', StoryComponent);
</script>

<Meta 
  title={story.short}
  description={story.tease}
/>

{#if StoryComponent}
  <svelte:component this={StoryComponent} {story} data={copyData} />
{:else}
  <div class="error">
    <h2>Story Component Not Found</h2>
    <p>The story component for "{story.slug}" could not be loaded.</p>
    <p>Slug: <code>{story.slug}</code></p>
    <p>Expected path: <code>$lib/stories/{story.slug}/components/Index.svelte</code></p>
  </div>
{/if}

<style>
  .error {
    max-width: 600px;
    margin: 2rem auto;
    padding: 2rem;
    text-align: center;
    background: #fef2f2;
    border: 1px solid #fecaca;
    border-radius: 8px;
    color: #991b1b;
  }
  
  .error code {
    background: #fee2e2;
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
    font-family: monospace;
    font-size: 0.9rem;
  }
</style>