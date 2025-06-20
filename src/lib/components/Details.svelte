<script>
  let { summary, text, list } = $props();
</script>

<details>
  <summary>{@html summary}</summary>
  <div class="inner">
    {#if text && typeof text === "string"}
      <p>{@html text}</p>
    {:else if text}
      {#each text as { value }}
        <p>{@html value}</p>
      {/each}
    {/if}

    {#if list}
      <ul>
        {#each list as value}
          <li>
            {#if value.lead}<strong>{@html value.lead}</strong>{/if}
            {@html value.description || value}
          </li>
        {/each}
      </ul>
    {/if}
  </div>
</details>

<style>
  details {
    font-size: var(--font-size-small);
    font-family: var(--sans);
    font-weight: var(--font-weight-bold);
    padding: 1rem 0;
    border-bottom: 1px solid var(--color-border);
  }

  summary {
    color: var(--color-fg);  /* Fixed: use our defined color */
    padding-bottom: 0.75rem;
    font-size: max(16px, var(--font-size-small));
    cursor: pointer;
    transition: transform calc(var(--1s) * 0.25);
    list-style: none; /* Remove default triangle */
  }

  /* Custom triangle for summary */
  summary::before {
    content: '▶';
    display: inline-block;
    margin-right: 0.5rem;
    transition: transform calc(var(--1s) * 0.25);
    font-size: 0.8em;
    color: var(--color-secondary-gray);
  }

  details[open] summary::before {
    transform: rotate(90deg);
  }

  summary:hover {
    transform: translateX(4px);
  }

  .inner {
    padding: 1rem;
    font-family: var(--serif);
    font-weight: var(--font-weight-normal);
  }

  .inner p {
    margin: 0.75rem 0;
    line-height: 1.6;
  }

  .inner p:first-child {
    margin-top: 0;
  }

  .inner p:last-child {
    margin-bottom: 0;
  }

  ul {
    width: 100%;
    list-style: none;
    padding-left: 0;
    margin: 1rem 0;
  }

  li {
    padding-bottom: 1rem;
    line-height: 1.5;
  }

  li:last-child {
    padding-bottom: 0;
  }

  /* Strong text in list items */
  li strong {
    font-family: var(--sans);
    font-weight: var(--font-weight-bold);
    display: block;
    margin-bottom: 0.25rem;
  }

  /* Link styling within details */
  :global(.inner a) {
    color: var(--color-link);
    text-decoration: underline;
    text-decoration-color: var(--color-link);
    transition: color var(--transition-medium);
  }

  :global(.inner a:hover) {
    color: var(--color-link-hover);
    text-decoration-color: var(--color-link-hover);
  }
</style>