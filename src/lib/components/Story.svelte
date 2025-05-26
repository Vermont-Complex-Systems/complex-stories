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
  
  // Thumbnail handling
  const imagePath = `${base}/common/thumbnails/screenshots`;
  const hasImage = true; // You can make this dynamic based on file existence
</script>

<div class="story" {style} class:external={isExternal} class:resource class:footer>
  {#if !resource && !footer}
    <div class="info">
      <p class="id">#{id}</p>
      <p class="month">{month}</p>
      {#if isExternal}
        <span class="external-badge">External</span>
      {/if}
    </div>
  {/if}
  
  <a 
    {href} 
    rel={isExternal ? "external noopener" : undefined}
    target={isExternal ? "_blank" : undefined}
    class="inner"
  >
    <div class="screenshot">
      {#if hasImage && !isExternal}
        <!-- Internal story with thumbnail -->
        <img 
          src="{imagePath}/{slug}.jpg" 
          loading="lazy" 
          alt="Thumbnail for {short}"
        />
        <!-- Fallback card content if image fails to load -->
        <div class="card-content fallback" style="display: none;">
          <span class="story-number">#{id}</span>
        </div>
      {:else if isExternal}
        <!-- External story indicator -->
        <div class="external-indicator">
          <svg class="external-icon" viewBox="0 0 24 24" fill="currentColor">
            <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6m4-3h6v6m-11 5L21 3"/>
          </svg>
          <span class="external-text">External Link</span>
        </div>
      {:else}
        <!-- Fallback for stories without images -->
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

  .external-badge {
    background: #e53e3e;
    color: white;
    font-size: 0.7rem;
    padding: 2px 6px;
    border-radius: 3px;
    text-transform: uppercase;
    font-weight: bold;
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
    border-radius: 8px;
  }

  /* Image styles */
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

  /* Card content fallback */
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

  /* External story styles */
  .external-indicator {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    text-align: center;
    color: white;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 8px;
  }
  
  .external-icon {
    width: 2rem;
    height: 2rem;
    opacity: 0.9;
  }
  
  .external-text {
    font-size: 0.9rem;
    font-weight: bold;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }
  
  .story.external .screenshot {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  }
  
  .story.external:hover .external-indicator {
    transform: translate(-50%, -50%) scale(1.05);
  }

  /* Text content */
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