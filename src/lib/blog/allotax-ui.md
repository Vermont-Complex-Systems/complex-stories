
<a href="https://vermont-complex-systems.github.io/complex-stories/allotaxonometry" target="_blank" rel="noopener">
    <img src="/py_allotax_example005-crop.jpg" alt="ALLotaxonometry">
</a>

The allotaxonograph is a scientific tool developed by the [Computational Story Lab](https://compstorylab.org/) to compare any pairs of systems with meaningfully rankable components. For instance, think about baby names at different times, with their count frequency being heavy-tailed (that is, the most frequent baby names occur an order of magnitude more than less frequent names). It is a tool designed to understand complex systems, but could benefit to a larger audience, such as policy makers or applied scientists.

The thing is that some people only want to use tools programatically, say from a jupyter notebook using the Python programming language. Others only want a drag and drop approach, where they just want to drop their data on a standalone page, a be able to download the results. At the institute, this has led to the following question:

> How can we make tools from complex systems available to a diversity of users?

The [allotaxonometer-ui](https://github.com/Vermont-Complex-Systems/allotaxonometer-ui) library is our answer to this problem. Inspired by [bits-ui](https://bits-ui.com/), the `allotaxonometer-ui` is a headless component library that lets us share components and utility functions to build the allotaxonograph. It underlies the following projects and stories

<div class="image-grid">
  
  <div class="image-item">
    <a href="https://vermont-complex-systems.github.io/complex-stories/allotaxonometry" target="_blank" rel="noopener">
      <img src="/common/thumbnails/screenshots/allotaxonometry.jpg" alt="ALLotaxonometry">
    </a>
    <p class="image-caption">ALLotaxonometry</p>
  </div>
  
  <div class="image-item" style="max-width:90%;">
    <a href="https://vermont-complex-systems.github.io/complex-stories/allotax-scrolly" target="_blank" rel="noopener">
      <img src="/common/thumbnails/screenshots/allotax-scrolly.jpg" alt="A whirlwind tour of the allotaxonometer">
    </a>
    <p class="image-caption">A whirlwind tour of the allotaxonometer</p>
  </div>

  <div class="image-item">
    <a href="https://github.com/compstorylab/py-allotax" target="_blank" rel="noopener">
      <img src="/Allotax.jpg" alt="py-allotax">
    </a>
    <p class="image-caption">py-allotax</p>
  </div>
</div>

To better understand the contribution, we should consider first what researchers typically do when they develop new tools. If they believe in the ideals of open science, they might release their code, as with the original [matlab version](https://gitlab.com/compstorylab/allotaxonometer) of the allotaxonometer. But as "[amateur software developer](https://www.youtube.com/watch?v=zwRdO9_GGhY)", the code might be of varying quality in terms of maintainability and accessibility. Most scientists are not profesional developers, and even if they are it takes time to improve computer code such that it is accessible. Hence, the code might be release, but more or less easy to access for researchers around the world. 

The code will be also in a scientific language of choice, which most likely than not is not designed for the web. This means that it makes it hard to translate from the static world to the interactive, browser world by which most people discover new stuff. Thus, what do we need to take such tools as the allotaxonograph, and make it maitainable and shareable?

## The voyage begins

