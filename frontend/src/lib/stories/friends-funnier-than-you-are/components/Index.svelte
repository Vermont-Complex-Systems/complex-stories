<script>
import { base } from "$app/paths";

import InteractiveFig1 from "./InteractiveFig1.svelte";
import BranchingNetwork from "./BranchingNetwork.svelte";
import SelfReinforcingNetwork from "./SelfReinforcingNetwork.svelte";
import LogLogPlot from "./LogLogPlot.svelte";

import { renderTextContent } from '$lib/components/helpers/ScrollySnippets.svelte';

let { story, data } = $props();


</script>


<article id="cascade-story">
    
    <div class="logo-container">
        <a href="{base}/" class="logo-link">
            <img src="{base}/octopus-swim-right.png" alt="Home" class="logo" width="200" />
        </a>
    </div>

    <div class="title">
        <h1>{data.title}</h1>
        <h2>{data.subtitle}</h2>

        <div class="article-meta">
            <p class="author">
                By {@html data.author1}, {@html data.author2} and {@html data.author3}
            </p>
            <p class="date">
                {data.date}
            </p>
        </div>
    </div>

    <!-- Story-specific content renderer (inline snippet pattern)
         Components must be hardcoded here since they can't be passed as data.
         Text rendering (html, markdown, math) is delegated to shared renderTextContent. -->
    {#snippet renderContent(contentArray)}
        {#each contentArray as item}
            {#if item.type === "component"}
                {#if item.component === "BranchingNetwork"}
                    <div class="branching-container">
                        <BranchingNetwork />
                    </div>
                {:else if item.component === "InteractiveFig1"}
                    <div class="plot-container">
                        <InteractiveFig1 />
                    </div>
                {:else if item.component === "SelfReinforcingNetwork"}
                    <div class="plot-container">
                        <SelfReinforcingNetwork />
                    </div>
                {:else if item.component === "LogLogPlot"}
                    <div class="plot-container">
                        <LogLogPlot />
                    </div>
                {/if}
            {:else}
                <p>{@render renderTextContent(item)}</p>
            {/if}
        {/each}
    {/snippet}

    <section id="intro">
        {@render renderContent(data.intro)}
    </section>

    <section id="model">
        <h2>{data.ModelSectionTitle}</h2>
        {@render renderContent(data.model)}
    </section>
    
    <section id="result">
        <h2>{data.ResultSectionTitle}</h2>
        {@render renderContent(data.result)}
    </section>
    
    <section id="conclusion">
        <h2>{data.ConclusionSectionTitle}</h2>
        {@render renderContent(data.conclusion)}
    </section>
</article>


<style>
    :global(body:has(#cascade-story)) {
        background-color: #f8f5e6;
        overflow-x: hidden; /* Prevent horizontal scroll from full-width components */
    }

    /* Dark mode support */
    :global(.dark body:has(#cascade-story)) {
        background-color: var(--color-bg);
        color: var(--color-fg);
    }
    
    
    /* Fixed: properly scope h1 and h2 separately */
    :global(body:has(#cascade-story)) h1 {
        font-family: var(--serif);
        max-width: 450px;
        font-size: var(--font-size-giant);
        margin: 6rem auto 1rem auto;
        text-align: center;
    }

    /* Dark mode support */
    :global(body:has(#cascade-story)) .title {
        margin: 0 auto 5rem auto;
    }

    /* Scope section h2 to this story only */
    :global(#cascade-story) section h2 {
        margin-top: 3rem !important;
    }

    :global(body:has(#cascade-story)) h2 {
        font-size: var(--font-size-medium);
        font-weight: 400;
        margin: 0 auto 3rem auto;
        text-align: center;
    }    
    
    .logo-container {
        margin: 1rem auto 0 auto;
        max-width: 8rem;
        position: relative;
    }
    
    .branching-container {
        width: 100vw;
        position: relative;
        left: 50%;
        right: 50%;
        margin-left: -50vw;
        margin-right: -50vw;
        display: flex;
        justify-content: center;
        align-items: center;
        flex-direction: column;
        box-sizing: border-box;
    }

    .plot-container {
        display: flex;
        justify-content: center;
        align-items: center;
        margin: 0 0;
        padding: 0;
    }        
    
    .article-meta {
        margin: -1rem auto 2rem auto;
        font-family: var(--sans);
        max-width: 30rem;
        text-align: center;
    }
    
    .article-meta .author {
        font-size: var(--font-size-medium);
        color: var(--color-secondary-gray);
        margin: 0 0 0.25rem 0;
        font-weight: 500;
        text-align: center !important;
    }
    
    .article-meta .date {
        font-size: var(--font-size-small);
        color: var(--color-tertiary-gray);
        margin: 0;
        font-weight: 400;
        text-align: center !important;
    }
    
    @media (max-width: 768px) {
        :global(body:has(#cascade-story)) h1 {
            font-size: 4rem !important;
        }
        
        :global(body:has(#cascade-story)) h2 {
            font-size: 2rem !important;
        }
        
        .article-meta .author {
            font-size: var(--font-size-large) !important;
        }
        
        .article-meta .date {
            font-size: var(--font-size-medium) !important;
        }
        
        .logo-container {
            max-width: 6rem;
        }
    }
</style>