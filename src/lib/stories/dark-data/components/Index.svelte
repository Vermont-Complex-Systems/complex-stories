<script>
import { base } from "$app/paths";
</script>

<section id="story"  class="story">
    <div class="logo-container">
            <a href="{base}/" class="logo-link">
                <img src="{base}/octopus-swim-right.png" alt="Home" class="logo" width="200" />
            </a>
    </div>

    <h1>Where the data goes dark</h1>
    <div class="article-meta">
        <p class="author">By <a href="{base}/author/jonathan-st-onge">Jonathan St-Onge</a></p>
        <p class="date">Aug 13, 2025</p>
    </div>

    <p>The idea of <em>openness</em> in science is fundamental. It is a cornerstone of reproducibility and accountability in academic work.</p>
    
    <p>Yet, open science is notoriously hard to achieve or even define.</p>
    
    <p>Consider how with changing technology, new reproducibility tools and measures have come into play, establishing standards for publication: including an author's email address for questions, clarifications, links to access data repositories, or code availability statements in computational studies. All the pieces of the puzzle are constantly changing, but science ought to keep track of those, while moving forward.</p>

    <img src="{base}/data-sharing-scriberia.svg" alt="Home" width="500"/>

    
    
    <p>In this project, we seek to understand the extent to which open academic assets are indeed findable and accessible after initial publication and developing methods by which to understand what academic data assets should be findable and accessible.t he level of how findable and accessible these data are is what we call "<b class="luminous">data luminosity</b>".</p>

    
    <p> One obvious way that researchers share their data is through <em>data availability statements</em>. Simply stated, this is a statement in a paper that says whether the data is available, and if so, where it can be found. Simple enough? </p>
    
</section>

<div class="box">
        <div>CCDC 2051611 contains the supplementary crystallographic <span class="data">data</span> for this work. These <span class="data">data</span> can be obtained free of charge from The Cambridge Crystallographic Data Centre via www.ccdc.cam.ac.uk/data_request/cif.</div>
        <div>Supplementary <span class="data">data</span> are available at Journal of Tropical Pediatrics online.</div>
        <div>In this paper, we have applied <span class="data">data</span> from various sources. A detailed list of the variables, their definitions and sources is provided in Table 1.</div>
        <div>The <span class="data">data</span> that support the findings of this study are available from the corresponding author upon reasonable request.</div>
        <div>NAISC-L <span class="data">data</span> is stored in a relational database (RDB) and is uplifted to RDF using R2RML, a W3C Recommendation used to express mappings from RDBs to RDF (Das et al. 2012)... These mappings were created using the JUMA mapping tool (Crotti et al. 2018). The graphs can be viewed and downloaded in different RDF serialisation formats</div>
        <div>Temperature records from (a) mid-Holocene Sr/Ca derived record from KR-AMA-2, (b) modern microatoll KR-MMA-1 Sr/Ca record, and (c) instrumental <span class="data">data</span> obtained from Mourilyan Harbour in situ <span class="data">data</span> logger (http://www.aims.gov.au). Temperature values given are the mean of each dataset, with gray shading indicating the 95% confidence interval of the mean.</div>
        <div>Data provided by experimenters, and archived in original form in publications or computer-accessible <span class="data">data</span> repositories, e.g., in EXFOR [55], are considered to be raw <span class="data">data</span>.</div>
</div>


<style>
    .box > * {
      border: 2px solid rgb(96 139 168);
      border-radius: 5px;
      background-color: rgb(96 139 168 / 0.2);
      flex: 1 1 200px;
      margin: 0.5rem;
      padding: 1rem;
    }
    
    .box {
      width: 1000px;
      display: flex;
      flex-wrap: wrap;
      margin: 0 auto;
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

    .luminous {
        color: #ffffff;
        animation: glow 2s ease-in-out infinite alternate;
    }

    @keyframes glow {
        from {
            text-shadow: 
                0 0 5px #29a770,
                0 0 10px #29a770,
                0 0 15px #29a770;
        }
        to {
            text-shadow: 
                0 0 10px #29a770,
                0 0 20px #29a770,
                0 0 30px #29a770,
                0 0 40px #29a770;
        }
    }

    
    .data {
        background: #29a770;
        color: white;
        padding: 2px 6px;
        border-radius: 3px;
    }

    section img {
        display: block;
        margin: 2rem auto;
        max-width: 100%;
        height: auto;
    }
</style>