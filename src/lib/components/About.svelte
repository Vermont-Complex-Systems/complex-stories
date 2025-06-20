<script>
  import { ascending } from "d3";
  import HeroText from "$lib/components/HeroText.svelte";
  import Details from "$lib/components/Details.svelte";
  import Team from "$lib/components/About.Team.svelte";

  let { copy, authors } = $props();

  const { sections } = copy;
  const staff = authors.filter((d) => d.position === "Staff");

  // Filter and sort contributors
  const contributors = authors.filter((d) => d.position !== "Staff" && d.id !== "vcsi");
  contributors.sort((a, b) => ascending(a.name, b.name));
  
  // Generate contributor links for the details list
  copy.contributors.detailsList = contributors.map(({ slug, name }) => {
    return `<a href="/author/${slug}">${name}</a>`;
  });
</script>

<section id="intro" class="column-regular">
  <HeroText>
    <h1>{copy.title}</h1>
    <p>{@html copy.dek}</p>
  </HeroText>
</section>

{#each sections as { id, hed }}
  <section {id} class="column-regular below">
    {#if hed}
      <h2 class="section-heading">{hed}</h2>
    {/if}

    <!-- Handle array content -->
    {#if Array.isArray(copy[id])}
      {#each copy[id] as { value }}
        <p>{@html value}</p>
      {/each}
    {/if}

    <!-- Handle object with text array -->
    {#if copy[id] && copy[id].text}
      {#each copy[id].text as { value }}
        <p>{@html value}</p>
      {/each}
    {/if}

    <!-- Team section -->
    {#if id === "team"}
      <Team {staff} />
    {/if}

    <!-- Details/collapsible section -->
    {#if copy[id] && copy[id].detailsSummary}
      <Details
        summary={copy[id].detailsSummary}
        text={copy[id].detailsText}
        list={copy[id].detailsList}
      />
    {/if}
  </section>
{/each}

<!-- Your existing styles stay the same -->
<style>
  .section-heading {
    line-height: 1.2;
    margin-top: 3rem;      /* Add space above section headings */
    margin-bottom: 1.5rem; /* Add space below section headings */
  }


  .below {
    margin-top: 2rem;
  }

  :global(#contributors ul) {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem 1rem;
  }
  
  :global(#contributors li) {
    padding-bottom: 0;
    width: calc(33.333% - 0.67rem);
    min-width: 0;
  }

  /* About page link styling */
  :global(.column-regular a) {
    color: var(--color-fg);
    text-decoration: underline 2px var(--color-fg);
    transition: color var(--transition-medium);
  }

  :global(.column-regular a:hover) {
    color: var(--color-link-hover);
    text-decoration-color: var(--color-link-hover);
  }

  /* Ensure paragraphs have proper spacing */
  :global(.column-regular p) {
    margin: 1rem 0;
    line-height: 1.6;
  }

  /* First paragraph in a section shouldn't have top margin */
  :global(.column-regular p:first-of-type) {
    margin-top: 0;
  }
  

  /* Responsive contributors grid */
  @media (max-width: 700px) {
    :global(#contributors li) {
      width: calc(50% - 0.5rem);
    }
  }

  @media (max-width: 400px) {
    :global(#contributors li) {
      width: 100%;
    }
  }
</style>