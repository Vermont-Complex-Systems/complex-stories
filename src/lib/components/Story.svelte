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
  const hasImage = true;
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
      {#if hasImage}
        <img src="{imagePath}/{slug}.jpg" loading="lazy" alt="Thumbnail for {short}" />
        <div class="card-content fallback" style="display: none;">
          <span class="story-number">#{id}</span>
        </div>
      {:else}
        <div class="card-content">
          <span class="story-number">#{id}</span>
        </div>
      {/if}
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
    font-family: var(--mono, monospace);
    margin-bottom: 8px;
    align-items: center;
    user-select: none;
    transition: transform calc(var(--1s, 1s) * 0.25);
    -webkit-font-smoothing: antialiased;
  }

  .id {
    border: 1px solid var(--color-fg, #333);
    width: 4em;
    text-align: center;
    padding: 4px;
    border-radius: 2em;
    font-size: var(--14px, 14px);
    text-transform: uppercase;
    margin: 0;
  }

  .month {
    font-size: var(--14px, 14px);
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
    outline: 2px solid var(--color-focus, #0066cc);
  }

  .story:hover .info {
    transform: translateY(-4px);
  }

  .screenshot {
    background: var(--story-bg, var(--color-default-story-bg, #ddd));
    aspect-ratio: 1;
    position: relative;
    overflow: hidden;
    border-radius: 2px;
  }

  img {
    position: absolute;
    bottom: 0;
    left: 50%;
    transform: translate(-50%, 0) scale(1);
    width: calc(100% - (var(--padding, 16px) * 2));
    aspect-ratio: 6/7;
    transform-origin: center center;
    transition: transform calc(var(--1s, 1s) * 0.25);
    object-fit: cover;
  }

  .story:hover img {
    transform: translate(-50%, 0) scale(1.05);
  }

  .card-content {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    text-align: center;
    color: white;
    transition: transform calc(var(--1s, 1s) * 0.25);
  }

  .story:hover .card-content {
    transform: translate(-50%, -50%) scale(1.05);
  }

  .story-number {
    display: block;
    font-size: var(--24px, 24px);
    font-weight: bold;
  }

  .text {
    font-family: var(--sans, sans-serif);
    margin-top: 12px;
  }

  h3.short {
    color: var(--color-fg, #333);
    font-size: clamp(var(--24px, 24px), 6vw, var(--28px, 28px));
    line-height: 1;
    margin: 0;
    margin-bottom: 8px;
    letter-spacing: -0.8px;
  }

  p.tease {
    color: var(--color-secondary-gray, var(--color-fg, #666));
    font-size: var(--16px, 16px);
    margin: 0;
  }

  @media (min-width: 960px) {
    h3.short {
      font-size: clamp(var(--24px, 24px), 2.75vw, var(--32px, 32px));
    }
  }
</style>