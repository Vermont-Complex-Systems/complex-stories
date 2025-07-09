## Styling

We use no particular CSS frameworks for styling. The goal is for each story to have their own aesthetic, while having global styling that take care of commonsensical things. To achieve that, we have the following structure.

#### Global style

In `src/lib/styles`, we have the following CSS files

- app.css
- base.css
- font.css
- reset.css
- theme.css
- variables.css

I try as much as possible to make the bare minimum in those (this is WIP).

#### Component style (JSO)

For specific story, I like to declare "story-wide" settings in my `Index.svelte`. 

 - positioning decision should be made by the parent of a component.