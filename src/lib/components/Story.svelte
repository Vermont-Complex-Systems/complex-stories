<script>
  let { 
    id, 
    href, 
    slug, 
    short, 
    tease, 
    month, 
    bgColor, 
    isExternal = false,
    resource, 
    footer 
  } = $props();

  const style = bgColor ? `--story-bg: ${bgColor};` : "";
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
      {#if isExternal}
        <!-- External story indicator -->
        <div class="external-indicator">
          <svg class="external-icon" viewBox="0 0 24 24" fill="currentColor">
            <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6m4-3h6v6m-11 5L21 3"/>
          </svg>
          <span class="external-text">External Link</span>
        </div>
      {:else}
        <!-- Your existing card content for internal stories -->
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
  
  .external-badge {
    background: #e53e3e;
    color: white;
    font-size: 0.7rem;
    padding: 2px 6px;
    border-radius: 3px;
    text-transform: uppercase;
    font-weight: bold;
  }
  
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
  }

  .info p {
    font-size: var(--14px, 14px);
    text-transform: uppercase;
  }

  p {
    margin: 0;
  }

  a {
    display: block;
    text-decoration: none;
    cursor: pointer;
  }

  a:focus-visible {
    outline: 2px solid var(--color-focus, #0066cc);
  }

  .story:hover .info {
    transform: translateY(-4px);
  }


  .story:hover .card-content {
    transform: translate(-50%, -50%) scale(1.05);
  }

  .screenshot {
    background: var(--story-bg, var(--color-default-story-bg, #ddd));
    aspect-ratio: 1;
    position: relative;
    overflow: hidden;
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

  .resource h3.short {
    font-size: clamp(var(--20px, 20px), 6vw, var(--24px, 24px));
  }

  .footer h3.short {
    display: none;
  }

  p.tease {
    color: var(--color-secondary-gray, var(--color-fg, #666));
    font-size: var(--16px, 16px);
  }

  .footer p.tease {
    color: var(--color-secondary-gray, var(--color-fg, #666));
    font-size: clamp(var(--16px, 16px), 4vw, var(--20px, 20px));
    font-weight: bold;
    line-height: 1.2;
  }

  @media (min-width: 960px) {
    h3.short {
      font-size: clamp(var(--24px, 24px), 2.75vw, var(--32px, 32px));
    }
  }
</style>