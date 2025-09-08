<script>
import { base } from "$app/paths";

import InteractiveFig1 from "./InteractiveFig1.svelte";
import BranchingNetwork from "./BranchingNetwork.svelte";
import SelfReinforcingNetwork from "./SelfReinforcingNetwork.svelte";
import LogLogPlot from "./LogLogPlot.svelte";

import Md from '$lib/components/helpers/MarkdownRenderer.svelte';

let { story, data } = $props();

const intro = data.intro;
const model = data.model;

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

    {#snippet renderContent(contentArray)}
        {#each contentArray as { type, value, component }, i}
            {#if type === "Component"}
                {#if component === "BranchingNetwork"}
                    <div class="branching-container">
                        <BranchingNetwork />
                    </div>
                {:else if component === "InteractiveFig1"}
                    <div class="plot-container">
                        <InteractiveFig1 />
                    </div>
                {:else if component === "SelfReinforcingNetwork"}
                    <div class="plot-container">
                        <SelfReinforcingNetwork />
                    </div>
                {:else if component === "LogLogPlot"}
                    <div class="plot-container">
                        <LogLogPlot />
                    </div>
                {/if}
            {:else if type === "html" }
                <p>{@html value}</p>
            {:else if type === "math" }
                <div class="plot-container">
                    <Md text={value}/>
                </div>
            {:else}
                <p><Md text={value}/></p>
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
</article>


<style>
    :global(body:has(#cascade-story)) {
        background-color: #f8f5e6;
        overflow-x: hidden; /* Prevent horizontal scroll from full-width components */
    }
    
    :global(body:has(#cascade-story)) h1, h2 {
        font-family: var(--sans);
        max-width: 300px;
        font-size: var(--font-size-giant);
        margin: 0 auto 1rem auto;
        text-align: center;
    }    

    section h2 {
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
        max-width: 300px;
        position: relative;
        transform: translateX(1rem);
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

    .article {

    }
</style>