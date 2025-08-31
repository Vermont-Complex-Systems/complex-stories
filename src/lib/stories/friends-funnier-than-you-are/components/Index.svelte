<script>
import { base } from "$app/paths";
import BranchingNetwork from "./BranchingNetwork.svelte";
import LogLogPlot from "./LogLogPlot.svelte";
</script>

<section id="story"  class="story">
    <div class="logo-container">
            <a href="{base}/" class="logo-link">
                <img src="{base}/octopus-swim-right.png" alt="Home" class="logo" width="200" />
            </a>
    </div>

    <h1>Your friends are funnier than you are (redux)</h1>
    <div class="article-meta">
        <p class="author">By <a href="{base}/author/jonathan-st-onge">Jonathan St-Onge</a> and <a href="{base}/author/laurent-hébert-dufresne">Laurent Hébert-Dufresne</a></p>
        <p class="date">Aug 15, 2025</p>
    </div>

    <p>Spoiler: How far your joke is going depends on your friends going viral.</p>

    <p>The spread of stories or beliefs are often compared to viruses. But stories, like jokes, differ in how their quality can change as a result of the propagation. That is, assume there is a chance <em>p</em> that the joke quality gets improve or degrade as a result of transmission.</p>
    
    <p>In the first case, we find classical <u><a href="https://en.wikipedia.org/wiki/Branching_process">branching process</a></u>; one rabbit reproduces into two, two becomes four, four becomes eight...and not so long after the planet is covered in rabbits.</p>

    <div class="plot-container">
        <BranchingNetwork />
    </div>

    <p>Below we show a log-log plot where we show the distribution of fraction of cascades that reach a certain size <em>s</em> for a varying <em>p</em>.</p>
    
    <div class="plot-container">
        <LogLogPlot />
    </div>
    
</section>



<style>

    .plot-container {
        display: flex;
        justify-content: center;
        align-items: center;
    }

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
        text-align: center !important ;
    }

    .article-meta .date {
        font-size: var(--font-size-small);
        color: var(--color-tertiary-gray);
        margin: 0;
        font-weight: 400;
        text-align: center !important ;
    }

    :global(#story) {
        max-width: 700px;
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
        max-width: 700px;
        margin: 1rem auto;
        text-align: left !important;
    }

    section img {
        display: block;
        margin: 2rem auto;
        max-width: 100%;
        height: auto;
    }
</style>