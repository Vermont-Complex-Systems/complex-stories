<script>
  let { stories } = $props();
</script>

<section id="stories">
  <ul>
    {#each stories as story}
      <li>
        <div class="story">
          <div class="info">
            <p class="id">#{stories.indexOf(story) + 1}</p>
            <p class="type">Story</p>
          </div>
          <a href="/{story.slug}" class="inner">
            <div class="screenshot">
              <div class="placeholder">
                <!-- You could add story thumbnails here later -->
                <span class="story-icon">📊</span>
              </div>
            </div>
            <div class="text">
              <h3 class="short">
                <strong>{story.title}</strong>
              </h3>
              <p class="tease">
                {story.description}
              </p>
            </div>
          </a>
        </div>
      </li>
    {/each}
  </ul>
</section>

<style>

  section {
    margin-top: 16px;
  }

  ul {
    padding: 0;
    display: flex;
    flex-wrap: wrap;
    margin: 0 auto;
  }

  li {
    margin: 0;
    list-style-type: none;
    padding: 32px 16px;
    width: 100%;
    --padding: clamp(16px, 12vw, 48px);
  }

  .info {
    display: flex;
    justify-content: space-between;
    font-family: var(--mono);
    margin-bottom: 8px;
    align-items: center;
    user-select: none;
    transition: transform calc(var(--1s) * 0.25);
    -webkit-font-smoothing: antialiased;
  }

  .id {
    border: 1px solid var(--color-fg);
    width: 4em;
    text-align: center;
    padding: 4px;
    border-radius: 2em;
    font-size: var(--14px);
    text-transform: uppercase;
    margin: 0;
  }

  .type {
    font-size: var(--14px);
    text-transform: uppercase;
    margin: 0;
    color: var(--color-secondary-gray);
  }

  a {
    display: block;
    text-decoration: none;
    cursor: pointer;
    color: inherit;
  }

  a:focus-visible {
    outline: 2px solid var(--color-focus);
  }

  .story:hover .info {
    transform: translateY(-4px);
  }

  .story:hover .screenshot .placeholder {
    transform: scale(1.05);
  }

  .screenshot {
    background: var(--color-default-story-bg);
    aspect-ratio: 1;
    position: relative;
    overflow: hidden;
  }

  .placeholder {
    width: 100%;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    background: whitesmoke;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    transform: scale(1);
    transition: transform calc(var(--1s) * 0.25);
  }

  .story-icon {
    font-size: 3rem;
  }

  .text {
    font-family: var(--sans);
    margin-top: 12px;
  }

  h3.short {
    color: var(--color-fg);
    font-size: clamp(var(--24px), 6vw, var(--28px));
    line-height: 1;
    margin: 0;
    margin-bottom: 8px;
    letter-spacing: -0.8px;
  }

  p.tease {
    color: var(--color-secondary-gray);
    font-size: var(--16px);
    margin: 0;
  }

  @media only screen and (min-width: 600px) {
    li {
      width: 50%;
      --padding: clamp(16px, 6vw, 48px);
    }
  }

  @media only screen and (min-width: 960px) {
    li {
      width: 33.3%;
      --padding: clamp(24px, 4vw, 56px);
    }

    h3.short {
      font-size: clamp(var(--24px), 2.75vw, 32px);
    }
  }

  /* Dark mode support */
  @media (prefers-color-scheme: dark) {
    :global(:root) {
      --color-fg: #fff;
      --color-bg: #1a1a1a;
      --color-secondary-gray: #999;
      --color-default-story-bg: #333;
    }
  }
</style>