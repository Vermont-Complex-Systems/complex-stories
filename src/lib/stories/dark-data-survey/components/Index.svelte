<script>
import { base } from "$app/paths";
</script>

<section id="story"  class="story">
    <div class="logo-container">
            <a href="{base}/" class="logo-link">
                <img src="{base}/octopus-swim-right.png" alt="Home" class="logo" width="200" />
            </a>
    </div>

    <h1>Do younger folks care about privacy?</h1>
    <div class="article-meta">
        <p class="author">By <a href="{base}/author/juniper-lisa-lovato">Juniper Lovato</a></p>
        <p class="date">Aug 13, 2025</p>
    </div>



    <p>Spoiler: Privacy depends on who you are and and context.</p>

    <p>Pitch 1: Are you willing to share your data. Desire for privacy. Is it always through, or maybe it varies across contexts. Mixtures of privacy settings. </p>
    
    <p>Pitch 2: Do younger people care about privacy? </p>

    <p>Plot 1: privacy settings. Share what with whom.</p>

    <p>Plot 1: distance with the people you want to share your data</p>

    <p>Data</p>

    <ul>
        <li>undergrad</li>
    </ul>
</section>



<style>
    .article-meta {
        margin: -1rem auto 2rem auto; /* Negative margin to pull closer to title */
        font-family: var(--sans);
        max-width: 700px;
        text-align: center;
    }

    .article-meta .author {
        font-size: var(--font-size-medium);
        color: var(--color-secondary-gray);
        margin: 0 0 0.25rem 0;
        font-weight: 500;
    }

    .article-meta .date {
        font-size: var(--font-size-small);
        color: var(--color-tertiary-gray);
        margin: 0;
        font-weight: 400;
    }

    :global(#story) {
        max-width: 1200px;
        margin: 2rem auto;
        padding: 0 2rem;
    }

    :global(#story) h1 {
        font-size: var(--font-size-xlarge);
        margin: 2rem auto 3rem auto;
        text-align: center;
        font-family: var(--serif);
        max-width: 700px;
    }

	section p {
      font-size: 22px;
      max-width: 800px;
      line-height: 1.3;
      margin: 1rem auto;
  }

    section img {
        display: block;
        margin: 2rem auto;
        max-width: 100%;
        height: auto;
    }
</style>