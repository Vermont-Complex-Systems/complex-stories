<script>
  import { ascending } from "d3";
  import { base } from "$app/paths";
  let { staff } = $props();
  staff.sort((a, b) => ascending(a.name, b.name));
</script>

<ul>
  {#each staff as { id, name, slug }}
    <li>
      <a href="{base}/author/{slug}">
        <img src="{base}/common/assets/authors/{id}.jpg" alt="headshot of {name}" />
        <span>{name}</span>
      </a>
    </li>
  {/each}
</ul>

<style>
  ul {
    display: flex;
    flex-wrap: wrap;
    list-style-type: none;
    padding: 0;
    gap: 2rem; /* Use our spacing token instead of hardcoded 32px */
    margin-bottom: 2rem; /* Use our spacing token instead of hardcoded 32px */
  }

  li {
    max-width: 10.1em;
    line-height: 1.25;
    transition: transform calc(var(--1s) * 0.25);
    color: var(--color-fg);
  }

  a {
    display: block; /* Makes the entire card clickable */
    padding: 0;
    color: var(--color-fg);
    text-decoration: none; /* Remove default link underline */
    transition: color var(--transition-medium);
  }

  a:hover {
    color: var(--color-link-hover);
  }

  img {
    width: 100%; /* Ensure consistent image sizing */
    height: auto;
    margin-bottom: 0.25em;
    border-radius: var(--border-radius); /* Add subtle rounding */
    transition: transform calc(var(--1s) * 0.25);
  }

  li:hover img {
    transform: rotate(var(--left-tilt)) scale(1.05);
  }

  span {
    font-family: var(--sans);
    font-weight: var(--font-weight-bold);
    font-size: var(--font-size-small);
    display: block; /* Makes it easier to style as a block */
    padding-top: 0.375rem; /* Use rem instead of px */
    text-decoration: underline 2px var(--color-fg);
    transition: text-decoration-color var(--transition-medium);
  }

  a:hover span {
    text-decoration-color: var(--color-link-hover);
  }
</style>