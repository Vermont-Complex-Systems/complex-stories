
[Open Source Programs Offices](https://en.wikipedia.org/wiki/Open_Source_Program_Office) (OSPOs) help organizations adopt open source solutions to digital challenges. They grew out of technology companies' growing realization that dedicated teams of open source enthuasiasts could effectively guide their developers through open source software development—from licensing to design patterns and code reusability. 

At the [Vermont Research Open-Source Program Office (VERSO)](https://verso.w3.uvm.edu/), we help research groups adopt good practices in *research* software development. As an OSPO, we share the belief that academia can benefit from having a small team of open source enthuasists that can effectively guide research groups in navigating open source software development. 

We recognize that research groups operate under different constraints and may hold different ideas about the value of good coding practices than industry does. After all, research groups are not tech companies. That said, we believe that academia can learn from how modern organizations handle the challenges of hyperscale technologies, while recognizing when industry practices do not always apply to research. 

This blog is intended to demonstrate how and when adopting best practices in research software development creates value. We will showcase research projects we're involved in through scientific data essays, then use blog posts to explain which open source practices proved useful and why. 

### A first case study: principled data processing using dagster

Researchers have developed [principled data processing](https://www.youtube.com/watch?v=ZSunU9GQdcI) (PDP) to address the messiness of collaborative, data-driven projects. It is an approach to the data life cycle where researchers adopt a modular workflow; they write scripts that take some input, do some atomic tasks, and spit out single output. This logic is encoded in the project structure, and subsequently serve as documentations for reproducibility and maintainability ("the code is the documentation"). PDP exemplifies what we mean by "good practices" in research software engineering—an alternative to the common research habit of hacking together duct-tape software solutions that "just work". 

We show how we implemented PDP for the [open academic analytics](https://vermont-complex-systems.github.io/complex-stories/open-academic-analytics) (OAA) project using the data orchestration tool [dagster](https://github.com/dagster-io/dagster). The short-term contribution of this project is to web interface where we show how scientific productivity coevolve with collaborations. One research question we have while building this interface is the following:

> How does diversity in collaboration in terms of age and institutions impact the research of selected authors (whom we call "ego"). 

The OAA project is messy; we need to call openAlex API to get the data (which is noisy and imperfect), we need to wrangle the data to build relevant features, which we use in a Stan probabilistic model. We use [dagster](https://github.com/dagster-io/dagster) to manage and visualize our dependency graphs between our tasks. 


<div>
  <img src="/Global_Asset_Lineage.svg" alt="data pipeline">
</div>

Here we will on the subset of the problem of going from raw data to the paper timeline chart, where node size is proportional to number of citations. 


