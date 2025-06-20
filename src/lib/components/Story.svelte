<script>
  import { base } from "$app/paths";
  
  let { 
    id, 
    href, 
    slug, 
    short, 
    tease, 
    month, 
    bgColor, 
    isExternal = false,
    resource = false, 
    footer = false
  } = $props();

  const style = bgColor ? `--story-bg: ${bgColor};` : "";
  const imagePath = `${base}/common/thumbnails/screenshots`;
  const finalHref = isExternal ? href : `${base}${href}`;
</script>

<div class="story" {style} class:external={isExternal} class:resource class:footer>
  {#if !resource && !footer}
    <div class="info">
      <p class="id">#{id}</p>
      <p class="month">{month}</p>
    </div>
  {/if}
  
  <a 
    href={finalHref}
    rel={isExternal ? "external noopener" : undefined}
    target={isExternal ? "_blank" : undefined}
    class="inner"
  >
    <div class="screenshot">
      <img src="{imagePath}/{slug}.jpg" loading="lazy" alt="Thumbnail for {short}" />
    </div>
    
    <div class="text">
      <h3 class="short">
        <strong>{@html short}</strong>
      </h3>
      <p class="tease">
        {@html tease}
      </p>
    </div>
  </a>
</div>

<style>
  .info {
    display: flex;
    justify-content: space-between;
    font-family: var(--mono);
    margin-bottom: 0.5rem; /* Convert 8px to rem */
    align-items: center;
    user-select: none;
    transition: transform calc(var(--1s) * 0.25);
    -webkit-font-smoothing: antialiased;
  }

  .id {
    border: 1px solid var(--color-fg);
    width: 4em;
    text-align: center;
    padding: 0.25rem; /* Convert 4px to rem */
    border-radius: 2em;
    font-size: var(--font-size-xsmall);
    text-transform: uppercase;
    margin: 0;
  }

  .month {
    font-size: var(--font-size-xsmall);
    text-transform: uppercase;
    margin: 0;
  }

  a {
    display: block;
    text-decoration: none;
    cursor: pointer;
    color: inherit;
  }

  a:focus-visible {
    outline: 2px solid var(--color-focus);
    outline-offset: 2px;
  }

  .story:hover .info {
    transform: translateY(-0.25rem); /* Convert -4px to rem */
  }

  .screenshot {
    background: var(--story-bg, var(--color-default-story-bg));
    aspect-ratio: 1;
    position: relative;
    overflow: hidden;
    border-radius: var(--border-radius);
  }

  img {
    position: absolute;
    bottom: 0;
    left: 50%;
    transform: translate(-50%, 0) scale(1);
    width: calc(100% - (var(--padding) * 2));
    aspect-ratio: 6/7;
    transform-origin: center center;
    transition: transform calc(var(--1s) * 0.25);
    object-fit: cover;
  }

  .story:hover img {
    transform: translate(-50%, 0) scale(1.05);
  }

  .text {
    font-family: var(--sans);
    margin-top: 0.75rem; /* Convert 12px to rem */
  }

  h3.short {
    color: var(--color-fg);
    font-size: clamp(var(--font-size-medium), 6vw, var(--font-size-large));
    line-height: 1;
    margin: 0 0 0.5rem 0; /* Convert 8px to rem */
    letter-spacing: -0.05em; /* Convert -0.8px to em for better scaling */
  }

  p.tease {
    color: var(--color-secondary-gray);
    font-size: var(--font-size-small);
    margin: 0;
    line-height: 1.4;
  }

  @media (min-width: 960px) {
    h3.short {
      font-size: clamp(var(--font-size-medium), 2.75vw, var(--font-size-large));
    }
  }
</style>