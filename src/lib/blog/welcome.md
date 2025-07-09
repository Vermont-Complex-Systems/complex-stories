
[Open Source Programs Offices](https://en.wikipedia.org/wiki/Open_Source_Program_Office) (OSPOs) help organizations adopt open source solutions to digital challenges. They grew out of technology companies' growing realization that dedicated teams of open source enthuasiasts could effectively guide their developers through open source software development—from licensing to design patterns and code reusability. 

At the [Vermont Research Open-Source Program Office (VERSO)](https://verso.w3.uvm.edu/), we help research groups adopt good practices in *research* software development. As an OSPO, we share the belief that academia can benefit from having a small team of open source enthuasists that can effectively guide research groups in navigating open source software development. 

We recognize that research groups operate under different constraints and may hold different ideas about the value of good coding practices than industry does. After all, research groups are not tech companies. That said, we believe that academia can learn from how modern organizations handle the challenges of hyperscale technologies, while recognizing when industry practices do not always apply to research. 

This blog is intended to demonstrate how and when adopting best practices in research software development creates value. We will showcase research projects we're involved in through scientific data essays, then use blog posts to explain which open source practices proved useful and why. 

### A first case study: principled data processing using dagster

<div style="text-align: center; margin: 2rem 0;">
  <img src="/Global_Asset_Lineage.svg" alt="data pipeline" style="max-width: 1200px; width: 100%;">
</div>

Consider the practice of writing [data orchestration](https://github.com/dagster-io/dagster) to handle messy, collaborative research projects. This approach to the data lifecycle exemplifies what we mean by "good practices"—an alternative to the common research habit of hacking together duct-tape software solutions that "just work".

We will use the [opening academic analytics](https://vermont-complex-systems.github.io/complex-stories/open-academic-analytics) (OAA) project as an example, as it captures some of the real world challenges of researchers are confronted. In this project, we are interested in characterizing the coevolution of collaborations and productivity. We "open" academic analytics in that this kind of work is typically done behind close doors, while being sold to university administrators to make strategic business decisions.

The OAA project has some complexity associated with it, such as calling the openAlex API to get the data, and a messy data pipeline to wrangle the data in an original timeline plot. Here we show how to use a library called [dagster](https://github.com/dagster-io/dagster) to manage the pipeline. The core idea is that we will be interested in a given researcher (that we call "ego"), and we will build a timeline of its papers and collaborations, with respect to relevant metadata.

