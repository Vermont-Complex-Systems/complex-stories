<script lang="ts">
	import { innerWidth } from 'svelte/reactivity/window';
	
	import Network from './Network.svelte';
	import Quench from './Quench.svelte';
	import Manylinks from '../data/edges.json';
	import nodes from '../data/nodes.csv';
	import Scrolly from '$lib/components/helpers/Scrolly.svelte';
	import Md from '$lib/components/helpers/MarkdownRenderer.svelte';
  import Hero from './Hero.svelte';

	let { story, data } = $props();

	let links = Manylinks[0];
	
	
	// const components = { Hero };
	let scrollyIndex = $state();
	
	const steps = data.steps;
	const postIntro = data.postIntro;


	let width = $state(innerWidth.current > 1200 ? 450 : 350);
	let height = 600;
	const padding = { top: 20, right: 40, bottom: 20, left: 60 };

</script>

<Hero />

<div class="centered-max-width">
<section id="mean-field">
    <h2>Part I: Annealing</h2>
    <p>But doing math on exact networks can get… messy. It’s often unwieldy to carry full structure through the equations. So instead, people often model the average effect of the dynamics — smoothing over the specific network in favor of general trends.</p>
    <p>To preserve some notion of structure without going fully detailed, modelers sometimes use what’s called an <u>annealed approximation</u>.</p>
    <p>Borrowed from metallurgy, annealing refers to the process of slowly cooling a metal so that its atomic structure settles into a stable — though not static — configuration. In network modeling, annealed networks refer to a similar idea: connections between nodes are not fixed, but constantly reshuffling, like social ties in a fast-moving crowd.</p> 
	<p>But why does that make sense? Think back to the bouncing balls. On average, the more infected balls there were, the more likely you were to bump into one. That’s the essence of a <u>mean-field approximation</u> — we ignore the specific bump and just look at average exposure.</p>

    <div class="chart-container-scrolly" >
        <Network {scrollyIndex} {nodes} {links} {width} {height} {padding} isRadial={true}/>
    </div>

    <div class="spacer"></div>
    <Scrolly bind:value={scrollyIndex}  offset={innerWidth.current > 1200 ? '50vh' : '20vh'}>
            {#each steps as text, i}
                {@const active = scrollyIndex === i}
                <div class="step" class:active>
					      <p> 
						      <Md text={text.value}/>
                </p>
                </div>
            {/each}
    </Scrolly>
    <div class="spacer"></div>
    
</section>



<section id="mean-field-versus-quench">
    <h2>Part II: Quenching</h2>
    <p>The annealed assumption is a powerful one, but it also has a fundamental drawback; it washes away persistent group interactions. In that sense, this is terrible (but still slightly better than the bouncing ball world). It can somewhat ephemeral group interactions, which can be fairly inclusive as a process. For instance, many models of <u>higher-order interactions</u> (or complex contagion) are about paper coauthorships, where the ephemerality of the interactions is the span it takes to publish a paper. It might be good enough.</p>
    <p>But workplace and households are both great example of group behaviors that are so persistent that it influences the dynamics in ways that mean-field just cannot. If your kid get sick, the chances are that the rest of the household will get sick too. There is <em>dynamical correlation</em> between the states of individuals within the household.</p>
    
    <div class="chart-container-scrolly">
        <Quench {scrollyIndex} {nodes} {links} {width} {height} {padding}/>
    </div>

    <div class="spacer"></div>
    <Scrolly bind:value={scrollyIndex}  offset={innerWidth.current > 1200 ? '50vh' : '20vh'}>
            {#each postIntro as text, i}
                {@const active = scrollyIndex === i}
                <div class="step" class:active>
					<p> 
                    <Md text={text.value}/>
                    </p>
                </div>
            {/each}
    </Scrolly>
    <div class="spacer"></div>
    
	<p>You should now have a better idea what physicists mean when they say that annealed networks are thought to be reshuffled constantly, leading to the system the relax faster than the dynamics. In contrast, quench changes slowly compared to the dynamics, meaning that local structures can strongly influence the dynamics.</p>
</section>
</div>




<style>
  /* Only global page styles */
	section {
	margin: 2rem auto;
	max-width: 1200px;
	padding: 0 2rem;
	}

	/* Allow viz sections to overflow the max-width */
	section:has(.chart-container-scrolly) {
	max-width: none; /* Remove width constraint for sections with visualizations */
	padding: 0 1rem; /* Reduce padding to give more space */
	}

	section h2 {
	font-size: 36px;
	margin-bottom: 1rem;
	}

	section p {
	font-size: 22px;
	max-width: 800px;
	line-height: 1.3;
	}


	/* Keep only the first section's scrolly styles */
	.chart-container-scrolly {
	width: 40%;
	height: 550px;
	position: sticky;
	top: calc(50vh - 275px);
	right: 5%;
	margin-left: auto;
	}


  .spacer {
    height: 75vh;
  }

  .step {
    height: 80vh;
    display: flex;
    place-items: center;
    justify-content: center;
  }

  .step p {
    padding: 0.5rem 1rem;
    background: whitesmoke;
    color: #ccc;
    border-radius: 5px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    transition: background 500ms ease;
    box-shadow: 1px 1px 10px rgba(0, 0, 0, 0.2);
    z-index: 10;
    width: 40%;
    transform: translateX(-60%);
  }

  .step.active p {
    background: white;
    color: black;
  }

  @media (max-width: 1200px) {
    section {
      padding: 0 1rem;
    }

    section p {
      font-size: 18px;
      max-width: none;
    }

    .chart-container-scrolly {
      position: sticky;
      top: calc(50vh - 275px);
      width: 100%;
      max-width: 600px;
      margin: 2rem auto;
      display: flex;
      justify-content: center;
      align-items: center;
    }

    .step {
      margin-left: 0;
      padding: 0 1rem;
      justify-content: center;
    }

    .step p {
      width: 100%;
      max-width: 600px;
      margin: 0 auto;
      text-align: center;
      transform: none;
    }
  }
</style>