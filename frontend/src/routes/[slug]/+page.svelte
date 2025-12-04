<script>
  import { getStoryComponent } from '$lib/utils/storyRegistry.js';
  import Spinner from '$lib/components/helpers/Spinner.svelte';
  // import Meta from '$lib/components/Meta.svelte';

  let { data } = $props();
  const { story, copyData } = data;

  let StoryComponent = $state(null);

  // Load component dynamically
  getStoryComponent(story.slug).then(component => {
    StoryComponent = component;
  });
</script>

<!-- <Meta
  title={story.short}
  description={story.tease}
/> -->

{#if StoryComponent}
  <StoryComponent {story} data={copyData} />
{:else}
  <div class="story-loading">
      <Spinner text="Loading story..." />
  </div>
{/if}

<style>
  .story-loading {
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 2rem;
  }

  .loading-content {
    text-align: center;
    max-width: 600px;
  }

  .story-title {
    font-size: 2.5rem;
    margin-bottom: 1rem;
    color: var(--color-text, #333);
  }

  .story-description {
    font-size: 1.2rem;
    color: var(--color-text-muted, #666);
    margin-bottom: 2rem;
    line-height: 1.4;
  }
</style>