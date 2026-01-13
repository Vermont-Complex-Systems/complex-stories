<article class="story">
	<h2>Why interdisciplinarity</h2>

    <p>It all started with a simple question: does network science start to bite its own tail? Here, biting its own tail means that network scientists might be abstracting away too much from other domains, perhaps in the name of mathematical modeling. The models are becoming more and more inward looking, in that their quality is more mathematical than drawn from other fields of study. In itself, it is not bad. Sophisticated mathematical modeling can be a worthy goal. But if network science ought to be "welcoming" to other disciplines, perhaps the models should remain as accessible as possible to fields that are less mathematically savvy. In any case, that was the original impetus.</p> 
    
    <p>As complex systems researchers, the instinct was to quantify this statement with the help of some methods. To ease the work, we used what was already made available by <a href="https://openalex.org/">OpenAlex</a>. Each paper has been annotated with a primary topic, and one of those seemed related enough to network science as we knew it: <a href="https://openalex.org/topics/T10064">Complex Network Analysis Techniques</a> (used to be called Statistical Mechanics of Complex Networks). To measure scientific <em>insularity</em>, we simply looked at the number of papers cited outside one's own topic compared to other topics. The naive idea was that over time, insular fields will start to cite papers more and more inside that topic, becoming less outward looking.</p>

    <div style="width: 100%; max-width: fit-content; margin-inline: auto; border: 1px solid #ddd; border-radius: 8px;">
        <img src="/insuarity.jpg" alt="insularity">
        <p>See <a href="https://jstonge1.w3.uvm.edu/">here</a> for original methodology.</p>
    </div>
    
    <p>This first approach is flawed in different ways. First off, we did not take the time to model what we should expect by chance in terms of insularity over time. Obviously when a community is starting, it has to look outward. When a community is becoming more mature, then what should we expect in terms of looking outward versus inward? Second, topics on OpenAlex were created, in a nutshell, by <a href="https://docs.google.com/document/d/1bDopkhuGieQ4F8gGNj7sEc8WSE8mvLZS/edit#heading=h.5w2tb5fcg77r">maximizing modularity</a> over the full citation graph. Hence, by looking at insularity in terms of number of citations outside one's own topics, we're measuring basically what OpenAlex has optimized for. Third, outward-looking topics are any topics outside your own, but this does not take into account proximity of cited topics; you might cite many topics but they are adjacent to your own topic space.</p>

    <p>Regardless of the methodological issues, a deeper question might be: what does interdisciplinarity even mean? While asking this question at the <a href="https://vermontcomplexsystems.org/events/cnww/">Complex Networks Winter Workshop 2025</a>, one thing became clear: nobody really agrees on the exact nuances of interdisciplinarity. Some people do not really care, as it is yet another question that might be thought of as self-centered. But in my opinion this is an interesting question when it comes to preventing "the obnoxious physicists"</p>

    <div style="width: 60%; max-width: fit-content; margin-inline: auto; ">
        <img src="/physicists.png" alt="physicists">
    </div>

    <p>As with many XKCD comics, this is a joke, but with some element of truth in it. How do we make sure that researchers with a particular modeling toolbox take stabs at problems in other fields while respecting their customs and traditions?</p>

    <p>Then was born the following idea: let's just ask researchers what papers they think are interdisciplinary. What about their papers? What about key papers in complex network analysis? One idea we set up to test is that the difference between having firsthand experience of how a paper was conducted versus how it is perceived by the community. As <a target=_blank rel=noreferrer href=https://vermont-complex-systems.github.io/complex-stories/author/juniper-lisa-lovato>Juniper Lovato</a> puts it, interdisciplinarity of a paper is very much dictated by "who do you ask and when", something that is very hard to capture using quantitative methods alone.</p>

    <p>Let's leave the definition vague and see what people have to say about it. Then perhaps we can go back to our quantitative approach and learn something new. And this is exactly what this app is about. It is a simple <a href="https://en.wikipedia.org/wiki/Create,_read,_update_and_delete">CRUD app</a> where people can log in, then annotate their own papers with the degree to which they think they are interdisciplinary or not. There is also a general queue of papers drawn from the Complex Network Analysis Techniques topic.</p> 

    <div style="width: 60%; max-width: fit-content; margin-inline: auto; border: 1px solid #ddd; border-radius: 8px;">
        <img src="/login.jpg" alt="login">
    </div>
    
    <p>Right now, it is a bit dumb; these are the most cited papers (TODO: draw random papers with minimum citations, to make sure they are not garbage, every 5 years or so). Once you annotate your papers, we will also add a community queue so that people can annotate your papers, if you choose to do so (and hopefully people have read those papers).</p>
        
    <p>Note that this app ought to be community driven and it is a side quest; as such, if there are design issues or something wrong about it, open an issue on GitHub and it can change!</p>
	
</article>

<style>
	.story {
		background: white;
		border: 1px solid #e0e0e0;
		border-radius: 8px;
		padding: 2rem;
		margin-bottom: 2rem;
		max-width: 100%;
	}

	.story h2 {
		font-size: var(--font-size-medium);
		margin: 0 0 1rem 0;
		color: #1a1a1a;
		line-height: 1.3;
		padding: 0 1rem;
	}

	.story p {
		color: #666;
		line-height: 1.6;
		margin: 0;
		font-size: var(--font-size-xsmall) !important;
		padding: 1rem;
		max-width: 100%;
	}

	/* Mobile styles */
	@media (max-width: 768px) {
		.story {
			padding: 1rem;
			margin-bottom: 1rem;
			border-radius: 4px;
		}
        
		.story h2 {
            font-size: 1.6rem !important;
			padding: 0 0.5rem;
		}

		.story p {
			padding: 0.75rem 0.5rem;
            font-size: var(--font-size-large) !important;
		}

		.story :global(img) {
			max-width: 100%;
			height: auto;
		}

		.story :global(div[style*="width"]) {
			width: 100% !important;
			max-width: 100% !important;
			margin-inline: 0 !important;
			padding: 0.5rem;
		}
	}
</style>