<script>
  import { getStory } from '$lib/story.remote';

  let { params } = $props();

  // Capture the slug value at initialization
  const slug = params.slug;

  // Use await directly in the component
  const { story, copyData } = await getStory(slug);

  // Dynamically import the story component
  const StoryComponent = await import(`$lib/stories/${slug}/components/Index.svelte`);
</script>

<!-- Render the story component with its data -->
<StoryComponent.default {story} data={copyData} />
