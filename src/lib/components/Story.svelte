<script>
  let { id, href, slug, short, tease, month, bgColor } = $props();
  
  const style = bgColor ? `--story-bg: ${bgColor};` : "";
</script>

<div class="story" {style}>
  <div class="info">
    <p class="id">#{id}</p>
    <p class="month">{month}</p>
  </div>
  <a {href} class="inner">
    <div class="screenshot">
      <!-- Your card content -->
      <div class="card-content">
        <span class="story-number">#{id}</span>
      </div>
    </div>
    <div class="text">
      <h3 class="short">
        <strong>{short}</strong>
      </h3>
      <p class="tease">
        {tease}
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

  .story:not(.youtube):hover .screenshot img,
  .story:not(.resource):hover .screenshot img {
    transform: translate(-50%, 0) scale(1.05);
  }

  .story.youtube:hover .screenshot img,
  .story.resource:hover .screenshot img {
    transform: translate(-50%, 50%) scale(1.05);
  }

  /* Your card content hover effect */
  .story:hover .card-content {
    transform: translate(-50%, -50%) scale(1.05);
  }

  .screenshot {
    background: var(--story-bg, var(--color-default-story-bg, #ddd));
    aspect-ratio: 1;
    position: relative;
    overflow: hidden;
  }

  span.icon--play {
    position: absolute;
    top: 50%;
    left: 50%;
    width: 4em;
    aspect-ratio: 1;
    transform: translate(-50%, -50%);
    pointer-events: none;
    z-index: var(--z-top, 10);
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
  }

  .youtube img,
  .resource img {
    bottom: 50%;
    transform: translate(-50%, 50%);
    transform-origin: center center;
    aspect-ratio: auto;
  }

  /* Your existing card content styles */
  .card-content {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    text-align: center;
    color: white;
    transition: transform calc(var(--1s, 1s) * 0.25);
  }

  .card-type {
    display: block;
    font-size: var(--16px, 16px);
    text-transform: uppercase;
    font-weight: bold;
    margin-bottom: 8px;
    font-family: var(--mono, monospace);
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