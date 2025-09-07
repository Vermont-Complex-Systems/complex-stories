<script>
import { base } from "$app/paths";

import InteractiveFig1 from "./InteractiveFig1.svelte";
import BranchingNetwork from "./BranchingNetwork.svelte";
import SelfReinforcingNetwork from "./SelfReinforcingNetwork.svelte";
import LogLogPlot from "./LogLogPlot.svelte";

import Md from '$lib/components/helpers/MarkdownRenderer.svelte';

let { story, data } = $props();

const steps = data.story;

</script>


<!-- <article id="cascade-story">
    <div class="logo-container">
                <a href="{base}/" class="logo-link">
                    <img src="{base}/octopus-swim-right.png" alt="Home" class="logo" width="200" />
                </a>
    </div>

    <div class="title">
        <h1>
            {data.title}
        </h1>

        <div class="article-meta">
            <p class="author">
                By {@html data.author1}, {@html data.author2} and {@html data.author3}
            </p>
        </div>
    
    </div>


    {#each data.story as { type, value }, i}
		{#if type === "Component"}
            {i}
        {:else}
        <p> 
		    <Md text={value}/>
		</p>
        {/if}
    {/each}
</article> -->

<article id="cascade-story">
    
    <section class="story">
        <div class="logo-container">
                <a href="{base}/" class="logo-link">
                    <img src="{base}/octopus-swim-right.png" alt="Home" class="logo" width="200" />
                </a>
        </div>

        <h1>Your friends are funnier than you are</h1>
        <div class="article-meta">
            <p class="author">By <a href="{base}/author/jonathan-st-onge">Jonathan St-Onge</a> and <a href="{base}/author/laurent-hébert-dufresne">Laurent Hébert-Dufresne</a></p>
            <p class="date">Aug 15, 2025</p>
        </div>

        <Md text={"Spoiler: How far your joke is going depends on your friends going viral.\n\nThe spread of stories or beliefs are often compared to viruses. But stories, like jokes, differ in how their quality can change as a result of the propagation. That is, assume there is a chance _p_ that the joke quality gets improve or degrade as a result of transmission. But before getting there, lets talk about branching process.\n\nFrom a theoretical perspective, [branching process](https://en.wikipedia.org/wiki/Branching_process) have been the backbones of complex systems study, letting researchers draw analogy between natural and social systems for a long time. Scaling is a feature of branching process that has excited natural scientists (in particular physicists) for a long time, as it hints at some universal principles underlying how parts of complex systems, such as river networks or leaf size distribution but also family names and memes, scale in particular, self-organized ways."} />

        <div class="branching-container">
            <BranchingNetwork />
        </div>

        <Md text="There are many interrelated meaning of the idea of scaling; how organisms grow in size (so-called allometric scaling), self-similarity (fractal), algorithmic (how long does it takes to sort a list of objects). With branching process, we are interested in the <em>cascade size distribution</em>, or simply put, the probability of big, large events happening compared to smaller cascades. Mathematically, this idea is neatly has been summarized by that simple relationship:"/>

        <div class="plot-container">
            <Md text={'$s^{-\\tau}$'} />
        </div>

        <Md text={'In plain english, this expression states that the size of a cascade scale with exponent $\\tau$, where a larger negative exponent means a steeper decline in the likelihood of large events—popularized as black swan events—occuring. This relationship typically works again our evolved chimp instincts that expect a "typical scale", such as height or brain size within a species. With power-laws, we are in the realm of "heavy tail" systems, referring to the fact that we keep being surprised by large cascade events that we fail to foresee.'}/>
        
        <Md text={'But the exciting part concerns a specific value of the scaling exponent, τ = 3/2, which emerges universally in systems at criticality - the precise mathematical point where branching processes transition between extinction and explosive growth. This universal exponent appears across diverse phenomena from neural avalanches to nuclear chain reactions, suggesting deep underlying principles.\n\nThis is where our story deviates from classical branching processes, where each step follows identical rules, and moves into _self-reinforcing cascades_, where the spreading process itself modifies the content being spread. Empirical studies of social media cascades consistently show much steeper decay than the 3/2 prediction, with scaling exponents ranging from τ = 2 to 4. This means large cascades are much rarer than critical branching theory would predict, which begs the question: "why?"\n\nOne mechanism we will explore is that in social media epidemics, the content of the cascade itself evolves as it spreads, leading to fundamentally new dynamics that break the assumptions of classical branching processes.'}/>
        
        <div class="plot-container">
            <SelfReinforcingNetwork />
        </div>

        <Md text='Think of our above trees as a network now, where it can be a forest or a joke that upon hitting a particular nodes, produces a large reaction (dark). Now, lets add the element of quality of the content influencing the dynamics of the spread.'/>


        <div class="plot-container">
            <InteractiveFig1 />
        </div>

        <Md text={"Unlike traditional epidemic models where a virus remains unchanged as it spreads, here the 'content' can get stronger (reinforced) or weaker as it moves from person to person."}/>
    
        <ul>
            <li>Orange circles: People who are "receptive" - they strengthen or improve the content when they encounter it (intensity increases)</li>
            <li>Blue circles: People who are "non-receptive" - they weaken or dilute the content (intensity decreases)</li>
            <li>Gray circles: "Absorbing boundaries" where the content has weakened to zero and the cascade path dies out</li>
            <li>Dashed lines: Connect to dead-end states where spreading stops</li>
            <li>Concentric circles: Show generation boundaries, with "I_max" indicating the strongest version of the content that reached each level</li>
        </ul>

        <Md text={"Unlike classical branching processes that predict explosive growth only at criticality, self-reinforcing cascades create much steeper size distributions (higher τ values) because content quality varies. Weak content dies out quickly, while only exceptional content survives to create large cascades. This mirrors social media: most posts fade fast, while a few go viral."}/>

        <Md text={"But why? Imagine telling a joke. Let’s say _X_ people hear it. The funnier the joke (_Y_), the more people it reaches, and the relation is exponential: audience size grows like exp(_Y_). But joke quality isn’t fixed — it drifts as people retell it, sometimes getting sharper, sometimes falling flat. This kind of random drift, like a drunkard’s walk, produces an exponential distribution of _Y_. Taking an exponential of that gives a power-law distribution for _X_. In other words, most jokes go nowhere, but a rare few explode. And because funny jokes spawn more retellings, on average the person who told you a joke is funnier than you are."} />

        <Md text={"This simple joke analogy captures the mechanism illustrated in Fig. 1: content quality drifts randomly, but because cascade size grows exponentially with quality, the resulting distribution of cascade sizes follows a power law."} />

        <Md text='Below we show a log-log plot of the fraction of cascades that reach size _s_, for different values of _p_.'/>
        
        <div class="plot-container">
            <LogLogPlot />
        </div>
        
    </section>
</article>


<style>
    :global(body:has(#cascade-story)) {
        background-color: #f8f5e6;
    }
    
    :global(body:has(#cascade-story)) h1 {
        font-family: var(--serif);
        max-width: 300px;
        font-size: var(--font-size-giant);
        margin: 2rem auto 3rem auto;
        text-align: center;
    }    
    
    .logo-container {
        margin: 1rem auto 1rem auto; /* Add this - was missing! */
        max-width: 300px;
        position: relative;
        transform: translateX(1rem);
    }
    
    .branching-container {
        display: flex;
        justify-content: center;
        align-items: center;
        flex-direction: column;
    }

    .plot-container {
        display: flex;
        justify-content: center;
        align-items: center;
    }        
    
    .article-meta {
        margin: -1rem auto 2rem auto;
        font-family: var(--sans);
        max-width: 300px;
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
</style>