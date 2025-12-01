<!-- +page.svelte -->
<script>
    import { base } from "$app/paths";
  </script>

<div class="header">
    <h1>A whirldwind tour of <a href="{base}/datasets">SciSciDB</a> (WIP)</h1>
    <div class="header-links">
      <a href="{base}/" class="octopus-link">
        <img src="{base}/octopus-swim-right.png" alt="Website" class="octopus-icon">
      </a>
      
    </div>
</div>

<style>
  .header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 2rem;
  }
  
  .header h1 {
    margin: 0;
    font-size: var(--font-size-large);
  }
  
  .header-links {
    display: flex;
    gap: 1rem;
    align-items: center;
  }
  
  .octopus-link {
    color: #666;
    text-decoration: none;
    transition: all 0.2s ease;
  }
  
  .octopus-link:hover {
    transform: scale(1.1);
  }
  
  .octopus-icon {
    width: 5rem;
    height: 5rem;
    object-fit: contain;
    transform: translateY(0.4rem); /* Moves logo up slightly */
  }

</style>