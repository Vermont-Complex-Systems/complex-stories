<script>
    import Spinner from '$lib/components/helpers/Spinner.svelte'
    import { countData, getAllFieldsAgg, getFieldsStem, getFieldsSocSci } from '$stories/hello-sciscidb/data.remote.js';
    import { Tween } from 'svelte/motion';
    import { cubicOut } from 'svelte/easing';

    import { base } from "$app/paths";

    import { Plot, BarY, Text } from 'svelteplot';
    import Slider from './Slider.svelte'
    import Select from './Select.svelte'
	import Streamgraph from './Streamgraph.svelte';
	import FosBarChart from './FosBarChart.svelte';
    import InsightBox from './InsightBox.svelte';
    import Header from "./Header.svelte";

    let selectedField = $state('Social Sciences');
    let selectedParse = $state('total');
    let selectedOffset = $state('wiggle');
    let minYear = $state(2000);
    let clicked = $state();

</script>

<section class="sciscidb-story">
<div class="dashboard">
    <Header />
    
    <p>We introduce useful snapshots of databases that are hosted at the University of Vermont, namely <a href="https://api.semanticscholar.org/api-docs/datasets">Semantic Scholar</a>, ... (more to come, <a href="https://docs.openalex.org/download-all-data/openalex-snapshot">OpenAlex</a> is next). Here we provide visualizations that we found missing from current APIs and have been helpful to a number of projects at the <a href="https://github.com/Vermont-Complex-Systems/">Vermont Complex Systems Institute</a>.</p>

    <InsightBox type="warning">
        <strong>TODO:</strong> Add TOC in the right margin when on desktop, but collapsible from the top on mobile
    </InsightBox>
    
    <h3>Introduction</h3>

    <p>The <a href="https://api.semanticscholar.org/api-docs/datasets">Semantic Scholar snapshot</a> provides metadata for over 200M texts from other aggregators such as PubMed, HAL, or the arXiv but also publishing partners such as ACM and the ACL (see <a href="https://www.semanticscholar.org/about/publishers">full list</a>). Although the raw number is impressive, Semantic Scholar distinguishes itself by open-sourcing a number of their natural language processing tools.</p>

    <div class="content-wrapper">
        <div class="text-content">
            <p>As part of their snapshot, they provide 16M parsed texts, called the <a href="github.com/allenai/s2orc">s2orc</a> collection, facilitating the creation of downstream applications such as <a href="https://www.connectedpapers.com/">Connected Papers</a>. Their original parsing scheme built on top of Grobid was made available on <a href="https://github.com/allenai/s2orc-doc2json">GitHub</a>. From that parsing, they extract a 2.4B citation graph that connects and contextualizes all that information.</p>
            <p>They provide useful representations of the texts as well, such as the <a href="https://huggingface.co/allenai/specter2">Specter2</a> embeddings for downstream tasks such as classification or topic modeling using density-based clustering. What I like about the Specter2 embedding is that it takes into account not only semantic similarity between texts, but also the relationships between texts. That is, two texts can be similar, but live in different reference spaces, which is a key feature of scientific work.</p> 
            <p>They also provide other tools on top of the data, such as their custom <a href="https://github.com/allenai/s2_fos">field of study</a> classifier, a spaCy pipeline for medical documents (<a href="https://github.com/allenai/scispacy">scispacy</a>), a recent toolkit for converting PDFs into clean and readable plain text (<a href="https://github.com/allenai/olmocr">OLMOCR</a>), and many more.</p>
        </div>
        <figure class="image-container">
            <img src='{base}/paper_layers.jpg' alt="some alt text" width="300"/>
            <figcaption><a href="https://github.com/allenai/papermage">PaperMage</a> view of the different layers in a paper.</figcaption>
        </figure>
    </div>

    <p>Practically, this means that the Semantic Scholar dataset provides researchers direct access to popular aggregators (arXiv, pubmed) and many more, some of which already having content parsed down to the paragraph level. This is tremendously helpful. If researchers want to expand their analysis beyond already parsed text, they can use AllenAI's open-source toolkits to do so. </p>

    <h3>Examining fields of study (FOS)</h3>

    <p>We already know from the papers that computer science and medicine papers are heavily represented in the Semantic Scholar database, by virtue of being more openly available than, say, economics or information science. The question is really: "how bad is it?" For the following plots, we use a 10M sample by FOS for convenience. Note that out of the 228M papers, around 148M papers have at least one associated field of study.</p>

    <p>Here is the macro perspective, looking at the counts of papers by FOS:</p>

    {#await getAllFieldsAgg()}
        <p>Loading FosBarChart data...</p>
    {:then data}
        <div class="chart-container">
            <FosBarChart {data}/>
        </div>
    {:catch error}
        <p>Error loading FosBarChart: {error.message}</p>
    {/await}

    <p>We next show the evolution of fields of study using a streamgraph. One issue is that we have more fields of study than humans are able to distinguish colors for. An easy workaround is to categorize our fields of study between STEM++ (like Physics and Chemistry, but also including environmental science and even medicine and computer science) and the Social Sciences++ (including humanities, law, and the arts). We now use a streamgraph to show the decomposition of fields of study over time for STEM++:</p>
    

    {#await getFieldsStem()}
        <p>Loading Streamgraph data...</p>
    {:then data}
        {@const data_f = data.filter(d => d.metric === selectedParse)}
        <div class="chart-container">
            <Streamgraph data={data_f} offset={selectedOffset} {clicked}/>
        </div>
    {:catch error}
        <p>Error loading Streamgraph: {error.message}</p>
    {/await}

    <div class="select-container">
        <Select bind:value={selectedOffset} options={['wiggle', 'normalize', 'none']}/>
        <Select bind:value={selectedParse} options={ ['total', 'has_abstract', 'has_fulltext']}/>
    </div>
    
    <p>When unnormalized, we can see the explosion of papers in different FOS, a trend that is acellerating in the 2000s. Note that we are currently using the <b>2025-08-19</b> release, which should include data up to very recently. We are still unclear whether the number of papers drastically shrink after 2020 or it is simply an artifact from the data pipeline. One hypothesis is that the Microsoft Academic Graph has been deprecated at the end of 2021, which was Microsoft undetaking of crawling scientific data at large. Maybe Semantic Scholar is somewhat less aggressive in their crawling, which would be aligned with their mission of providing high-quality data over quantity.</p>
    <p>When normalized, we note that medicine takes up much of the shares, which make sense as pubmed is a big open source datasets integrated in the database. Interestingly, we can see the extra space medicine takes around 2020, which is probably all the biomedical research that has been happening around COVID-19. We can see the rise of computer science.</p>

    <InsightBox type="tip">
        <p><strong>Tip:</strong> The streamgraph visualization requires a bit of practice to get right. Here we are using <em>inside-out</em> ordering, meaning the layers are arranged as to minimize the overall "wiggle" or movement of the baseline. When offset is set to null (also called silhouette mode), then all streams are stacked from a zero baseline upward. Click on a stream to make it more opaque, facilitating interpretation of the quantities.</p>
    </InsightBox>

    <p>We now move to the social sciences and humanities:</p>

    {#await getFieldsSocSci()}
        <p>Loading...</p>
    {:then data}
        {@const data_f = data.filter(d => d.metric === selectedParse)}
        <div class="chart-container">
            <Streamgraph data={data_f} offset={selectedOffset} {clicked}/>
        </div>
    {/await}

    <div class="select-container">
        <Select bind:value={selectedOffset} options={['wiggle', 'normalize', 'none']}/>
        <Select bind:value={selectedParse} options={ ['total', 'has_abstract', 'has_fulltext']}/>
    </div>

    <p>Here we will take the data with a grain of salt, as it could be something with how we wrangled the data (we are taking the first field of study in a list of entries) or perhaps something with the Semantic Scholar classifier, but what is up with Psychology after 2020?! Sociology grew to almost 25% of papers in that categorization. The Arts were also fairly constant, until COVID-19 hit. But again, I would take all that with a big grain of salt. The important bit here is to have a broad overview of what fields of study are biasing the Semantic Scholar dataset, nothing less, nothing more.</p>

    <p>One last thing to note is that by looking at the relative number of papers, we can see that STEM++ has around 3 times more papers than the Social Sciences++ category. It is not nothing, but any kind of analysis making claims about the whole of science based on the Semantic Scholar dataset should control for that fact. And this is also for papers with available FOS, which means the papers at least have an abstract. We might expect that STEM++ is even more represented when analyzing the S2ORC data.</p>

     <!-- <InsightBox type="tip">
        <p><strong>Tip:</strong> At the moment, we only talk about the FOS as provided in the Semantic Scholar database. But one could decompose those field of studies into topics, examining what is conisedered, say, "Biology" from a distance. We have a observable notebook prototype that does exactly that: <a href="https://observablehq.com/@jstonge/how-do-fos-evolve">here</a>. The challenge here is that to do so, we needed to integrate the openAlex database with that of Semantic Scholar, which was a bit messy. We might get back to it if there is interest.</p>

        <img src='{base}/prototype.jpg' alt="some alt text" width="700"/>
    </InsightBox> -->

    <h3>Time series venues (Very WIP)</h3>

    <p>For a given project, we wanted to know about the evolution of data sharing practices. We decided to sample the data by venue, as journal policies with respect to methods matter. Here we look at a time series by "top" venues, here simply defined by the venues' h5-index found on Google Scholar (we also use Google Scholar's subcategories of journals to classify papers). We use bullet charts to indicate how many available papers have been parsed out of all available papers in that venue.</p>

    <InsightBox type="warning">
        <strong>TODO:</strong> Add aggregated bar chart by subcategories of venues (see google scholar for the subcategories).
    </InsightBox>

     <p>You can explore the coverage of any specific field below:</p>

    <!-- {#await getAllPapers()}
        <p>Loading...</p>
    {:then data}    
        {@const filtered_data = data.filter((d) => d.field == selectedField && d.year >= minYear)}
        {@const uniq_venues = new Set(filtered_data.map(d=>d.venue))}
        
        <div class="chart-container">
            
            <div class="controls">
                <label>
                Google Scholar Category:
                {#await getFields()}
                    <select disabled>
                    <option>Loading venues...</option>
                    </select>
                {:then fields}
                    <Select bind:value={selectedField} options={fields}/>
                {:catch error}
                    <select disabled>
                    <option>Error loading venues</option>
                    </select>
                {/await}
                </label>
                
                <label>
                MinYear: {minYear}
                <Slider bind:value={minYear}/>
                </label>
            </div>

            <div class="chart2-container">

                <Plot 
                x={{tickRotate: 40, label: '', tickSpacing: 100}}
                y={{grid: true, axis: 'right' }}
                fy={{axis: false }}
                frame
                height={800}
                maxWidth="400px"
                marginRight={40}
                marginLeft={25}
                >
                <BarY 
                data={filtered_data}
                x="year"
                y="count"
                fy="venue"
                fillOpacity=0.1
                font-size=13
                stroke="black"
                />
                <Text 
                data={filtered_data}
                text={(d) => d.venue.length > 50 ? d.venue.slice(0,50)+'...' : d.venue}
                fy="venue"
                frameAnchor="top-left"
                dx={5}
                dy={5}
                fontSize={12}
                
                fontFamily='sans-serif'
                />
            </Plot>
            </div>
            <p style="font-size: 0.8rem; display: flex; justify-content: center; align-items: center;">p.s. {Array.from(uniq_venues).length} / 20 venues are showing up with this approach.</p>
        </div>
    {/await} -->

</div>
</section>

<style>
    
  .dashboard {
    border: 2px solid black;
    padding: 2rem;
    background-color: #f5f5f5;
    max-width: 800px;
    margin: 0 auto;
  }

  .sciscidb-story {
    width: 100vw;
    position: relative;
    left: 50%;
    right: 50%;
    margin-left: -50vw;
    margin-right: -50vw;
    margin-top: -2rem;
    padding: 4rem 1rem 2rem 1rem;
    background-color: #ccc;
    min-height: calc(100vh + 2rem);
  }

  /* NOTE: !important required to override app.css global 'section p' styles
     which use !important (line 204 in app.css).
     This is a dashboard with different typography needs than narrative content. */
  .dashboard p {
    line-height: 1.4rem !important;
    font-size: 1.1rem !important;
    font-family: sans-serif !important;
    max-width: none !important;
  }

  .dashboard h3 {
    font-size: 1.5rem !important;
    margin: 1.5rem 0 1rem 0 !important;
  }

  .select-container {
    margin-top: 1rem;
    margin-bottom: 1rem;
    max-width: fit-content;
    margin-inline: auto;
    display: flex;
    gap: 1rem;
  }

  /* .controls {
    display: flex;
    gap: 2rem;
    align-items: center;
    padding: 1rem;
    border-radius: 8px;
    margin: 0;
    flex-wrap: wrap;
    max-width: fit-content;
    margin-inline: auto;
  }
  
  .controls label {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .controls select {
    padding: 0.5rem;
    border: 1px solid #ccc;
    border-radius: 4px;
  } */
 
  
  .chart-container {
    width: 100%;
    border-radius: 15px;
    padding: 0.5rem;
    background-color: #e5e2e2;
  }
  
  /* .chart2-container {
    display: flex;
    justify-content: center;
    align-items: center;
  } */

  .content-wrapper {
    display: flex;
    flex-wrap: wrap;
    align-items: flex-start;
    gap: 20px;
}

.text-content {
    flex: 1 1 300px;
    min-width: 0;
}

.image-container { 
    flex: 0 0 auto;
    max-width: fit-content;
    border: 1px solid #ccc;
    padding: 20px;
    box-shadow: 5px 5px 10px rgba(0, 0, 0, 0.2);
    margin: 0;
    margin-top: 3rem;
}


.image-container figcaption {
    margin-top: 10px;
    font-size: 14px;
    color: #666;
    text-align: center;
    font-style: italic;
}

      /* Center image when it wraps on smaller screens */
    @media (max-width: 640px) {
        .image-container {
            align-self: center; /* This centers the image container */
            order: 2; /* Move image below text */
            margin-top: 0;
            margin-bottom: 1rem;
        }
        
        .text-content {
            order: 1;
        }
        .chart-container {
            width: 100%;
            padding: 0.5rem;
        }
    }

</style>

