<script>
  let { children } = $props();
</script>

<div class="hero-text">
  {@render children?.()}
</div>

<style>
  .hero-text {
    line-height: 1.65;
    padding: 2rem 0; /* Convert 2em to rem */
  }

  :global(.hero-text h1) {
    margin: 0;
    font-size: var(--font-size-giant);
    font-family: var(--sans);
    font-weight: var(--font-weight-bold);
    -webkit-font-smoothing: antialiased;
    line-height: 1.1; /* Add explicit line-height for large text */
  }

  :global(.hero-text p) {
    font-weight: var(--font-weight-thin);
    font-size: var(--font-size-large);
    line-height: 1.4;
    max-width: var(--width-padded);
    margin-top: 1.5rem; /* Add explicit spacing */
    -webkit-font-smoothing: antialiased;
  }

  @media (max-width: 959px) {
    .hero-text {
      padding: 5rem 0 1rem 0; /* Add more top padding on mobile */
    }
  }

  @media (min-width: 960px) {
    .hero-text {
      padding: 4rem 0 2rem 0; /* Convert 4em 2em to rem */
    }
  }
</style>