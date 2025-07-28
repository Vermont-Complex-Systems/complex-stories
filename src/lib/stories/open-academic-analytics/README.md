# Open academic Analytics

This project offers s micro-macro perspective on the coevolution of scientific productivity and collaborations. It is macro in that we deploy models and statistics to detect statistical patterns in career trajectories. It is micro in that we offer the possibility to users to investigate particular authors via our web interface. Here's a snapshot of the interface, you can find the live version [here](https://vermont-complex-systems.github.io/complex-stories/open-academic-analytics). We use faculties at University of Vermont as example.

<img width="1500" alt="open-academic-dashboard" src="https://github.com/user-attachments/assets/068730b0-4273-48cb-ab29-602be5340f06" />

### Back-end: Implementing principled data processing using dagster

We use [dagster](https://dagster.io/) as modern data orchestration tool to implement [principled data processing](https://www.youtube.com/watch?v=ZSunU9GQdcI). Here's a whirlwind tour of the approach, addressing reccurent concerns with messy, collaborative projects.

 - `Dagster offers a useful visual representation of code dependencies.` Looking at makefiles is annoying, who doesn't like to look at a shiny directed acyclic graph. 
 - `Atomizing tasks as sets of input-output scripts is up to the user.` Dagster only helps visualizing the dependencies, it does not constrain the user to adopt the PDP philosophy. As such, users must provide the dataflow such that each task takes a input, and return an output. 
 - `Duckdb working space within task and components`. [Duckdb](https://duckdb.org/) helps with managing complex data wrangling step, which can be reflected in the front-end. We use duckdb to manage our caching as well, using `primary keys` to avoid silly mistakes. By isomg duckdb to manage data wrangling on the fly in our web interface, we can transform large chunk of data seamlessly.
 - `Integrate back-end with front-end`. Each task, or asset, have a clear pathway to the front-end, and the front-end can be used to validate the data pipeline. It is modular through and through, such that even widgets on the dashboard can be tied to relevant dependencies in the backend.
 - `Dagster accomodate more sophisticated scenarios`. Dagster helps make our web app more fancy, such as by dealing with changing APIs or automation of data intake on a daily basis.

Here's a snapshot of our pipeline, as of `2025-07-08`:

<img width="1500" alt="Screenshot 2025-07-08 at 10 49 20 AM" src="https://github.com/user-attachments/assets/1ee84c3b-c244-490c-bb0e-438bab303167" />

<details><summary>Dagster instruction!</summary>

## Getting started

First, install your Dagster code location as a Python package. By using the --editable flag, pip will install your Python package in ["editable mode"](https://pip.pypa.io/en/latest/topics/local-project-installs/#editable-installs) so that as you develop, local code changes will automatically apply.

```bash
pip install -e ".[dev]"
```

Then, start the Dagster UI web server:

```bash
dagster dev
```

Open http://localhost:3000 with your browser to see the project.

You can start writing assets in `open_academic_analytics/assets.py`. The assets are automatically loaded into the Dagster code location as you define them.

## Development

### Adding new Python dependencies

You can specify new Python dependencies in `setup.py`.

### Unit testing

Tests are in the `open_academic_analytics_tests` directory and you can run tests using `pytest`:

```bash
pytest open_academic_analytics_tests
```

### Schedules and sensors

If you want to enable Dagster [Schedules](https://docs.dagster.io/guides/automate/schedules/) or [Sensors](https://docs.dagster.io/guides/automate/sensors/) for your jobs, the [Dagster Daemon](https://docs.dagster.io/guides/deploy/execution/dagster-daemon) process must be running. This is done automatically when you run `dagster dev`.

Once your Dagster Daemon is running, you can start turning on schedules and sensors for your jobs.

## Deploy on Dagster+

The easiest way to deploy your Dagster project is to use Dagster+.

Check out the [Dagster+ documentation](https://docs.dagster.io/dagster-plus/) to learn more.
</details>

### Front-end: A very svelte dashboard (experimental)

Why svelte to build a data apps over something like [Observable framework](https://observablehq.com/framework/), which is designed for such job? Framework is a powerful static-site generators for data that comes with "battery included". By that, I mean that out of the box libraries like duckdb, Leaflet, Lodash, are all working. But, I think there are two main reasons to favor svelte over Framework in our work.

1. `Integration with the rest of the website`. We already are using sveltekit to build the website. We wouldn't build that website using Framework.
1. `Front-End innovations`: The Svelte team is committed to improve how the web is being developed, simplifying it. We experiment with what they have to offer on that front. For instance, 
  
    - `Fine-grained reactivity`: We use the fact that svelte 5 runes provide fine-grained reactivity, leading to effective storytelling patterns such as scrolly-telling. It is in line with why svelteplot is not using observable plot as backend (see [why-svelteplot](https://svelteplot.dev/why-svelteplot)).
    - `Universal reactivity as stores`: Whereas before svelte 5 was using [stores](https://svelte.dev/docs/svelte/stores) to share reactive variables across components (effectively having global states), we can now declare reactive variables within `svelte.js` files that can be used anywhere in the app. Why do we care?


#### Centralizing states to prove data sustainability and extensibility

In [Framework](https://observablehq.com/framework/), I would often end up declaring my reactive variables somewhere in my code without thinking twice about it. Most often, those reactive variables are derived from queries to a Duckdb client to do on-the-fly data wranling. As I added more features to the data app, I would end up having many reactive variables, with a few queries to duckdb here and there, complicating the dependencies. 

As with Svelte, creating components for the different parts of our apps helped tame the complexity of the app. But I would still end up having many reactive variables passed to all my components, and subcomponents, sometime loosing track of what goes where. 

In Svelte 5, instead of passing props all the way down, we can centralize our logic within a single file, say `state.svelte.ts`. For concreteness, consider the following simplified utility tree from our story:

```
.
├── data/
| └──loader.js
└── components/
  ├── CoauthorChart.svelte
  ├── Dashboard.svelte
  ├── Index.svelte
  ├── PaperChart.svelte
  ├── sidebar
  │   ├── AuthorAgeFilter.svelte
  │   ├── NodeColor.coauthor.svelte
  │   ├── DataInfo.svelte
  │   └── SelectAuthors.svelte
  ├── Sidebar.svelte 
  └── state.svelte.ts // centralized states to manage dashboard
```

Here, `DataInfo.svelte` is a simple component that summarize statistics for a selected author, derived from the `selectedAuthors` reactive variables in `SelectAuthors.svelte`. As users change the selected author, the twin charts (`PaperChart.svelte` and `CoauthorChart.svelte`) are updating too, both called from our main `Dashboard.svelte` component. Additionally, `SelectAuthors.svelte` depends on the global `AuthorAgeFilter.svelte`, which decide what authors are displayed in the first place based on the academic age distribution. Arguably, it is in the nature of dashboard to create such intricate dependencies. `NodeColor.coauthor.svelte` is one example of a nested component that specify the color of nodes in the coauthor chart. There are many more.

With our `state.svelte.ts`, we do the following:

```js
// custom duckdb client 
import { registerParquetFile, query } from '$lib/utils/duckdb.js';
import { paperUrl, coauthorUrl } from '../data/loader.js';

// Reactive variables with respect to our dashboard state. 
export const dashboardState = $state({
    selectedAuthor: 'Peter Sheridan Dodds',
    coauthorNodeColor: 'age_diff',
    ageFilter: null,
});


// Data queried from our duckdb client.
export const data = $state({
    isInitializing: true,
    availableAuthors: [],
    paper: [],
    coauthor: [],
    error: null,
});

let tablesRegistered = false;

async function registerTables() {
    if (tablesRegistered) return;
    
    await registerParquetFile(paperUrl, 'paper');
    await registerParquetFile(coauthorUrl, 'coauthor');
    tablesRegistered = true;
}

// Simple duckdb call to know all of of our available authors.
async function loadAvailableAuthors() {
    await registerTables();
    
    const result = await query(`
        SELECT DISTINCT 
            name,
            LAST(author_age) as current_age,
            LAST(publication_year) as last_pub_year
        FROM coauthor 
        WHERE name IS NOT NULL AND author_age IS NOT NULL
        GROUP BY name
        ORDER BY name
    `);
    
    return result;
}

// We initialize the app with available authors in Index.svelte upon mounting the app.
export async function initializeApp() {
    try {
        data.isInitializing = true;
        data.availableAuthors = await loadAvailableAuthors(); 
        data.error = null;
        data.isInitializing = false;
    } catch (error) {
        console.error('Failed to initialize app:', error);
        data.error = error.message;
        data.isInitializing = false;
    }
}

// Duckdb call to access our paper data.
// Note that this function will be reactive to user input.
// Using duckdb to update our dashboard state is both more performant
// than JS code for data wrangling, but more important, wayyy more pleasant
// to write.
export async function loadPaperData(authorName) {
    await registerTables();
    const result = await query(`
        SELECT 
        strftime(publication_date::DATE, '%Y-%m-%d') as pub_date, * 
        FROM paper 
        WHERE name = '${authorName}' AND nb_coauthors < 25
        ORDER BY pub_date DESC
        `);
    return result;
}

// Duckdb call to access our coauthor data.
export async function loadCoauthorData(authorName) {
    await registerTables();
    const result = await query(`
        SELECT 
        strftime(publication_date::DATE, '%Y-%m-%d') as pub_date, 
        * 
        FROM coauthor 
        WHERE name = '${authorName}' AND nb_coauthors < 25
        ORDER BY pub_date DESC
        `);
    return result;
}

// Also called from top level, after initialization is done.
// Now this data is available globally.
export async function loadSelectedAuthor() {
    try {
        data.isLoadingAuthor = true;
        data.error = null;
        
        data.paper = await loadPaperData(dashboardState.selectedAuthor);
        data.coauthor = await loadCoauthorData(dashboardState.selectedAuthor);
        
        data.isLoadingAuthor = false;
    } catch (error) {
        data.error = error.message;
        data.isLoadingAuthor = false;
    }
}

// OPTIONAl (but useful)
// We create a class that is derived from previous data
class DerivedData {
  authors = $derived(data.availableAuthors || []);

  coauthors = $derived.by(() => {
    if (!data.coauthorData || data.coauthorData.length === 0) return [];
    const coauthors = [...new Set(data.coauthorData.map(c => c.coauth_name).filter(Boolean))];
    return coauthors.sort();
  });
}

export const unique = new DerivedData();
```

Alright, so there are really four main parts to our `state.svelte.ts` (with one more optional)
1. `Declaring objects`: e.g. `dashboardState` and `data` (you could also have `uiState` to keep track of the interface, we use it to know when the sidebar is toggled or not). In svelte, those objects will be usable as any other object. You don't need funky getter and setter as it was previously the case in svelte 4.
1. `Setting up Duckb client`
1. `Write initializeApp()`: this is the function that make available what is necessary for the rest of the app to run (we think of it as our function that doesn't take any argument, it'll be run once 😅)
1. `Write loadSelectedAuthors()`: this is the duckdb calls that react to user input.
1. `DerivedData class`: In those univeral reactivity files, we cannot export derived variables. To do so, it needs to be wrapped in a class. We use here for reactive variable that are derivable from our state variables, such as keeping track of unique elements in our dataset.  

Coming back to our example, lets look at how to our `state.svelte.ts` simplify our sidebar components:

```svelte
<script>
  import { Accordion } from "bits-ui";
  import { UserCheck } from "@lucide/svelte";
  import { dashboardState, unique } from '../state.svelte.ts';

  // Filter authors by age if filter is active. 
  let filteredAuthors = $derived.by(() => {
    if (!dashboardState.authorAgeFilter) return unique.authors;
      
    const [minAge, maxAge] = dashboardState.authorAgeFilter;
    return unique.authors.filter(author => {
      const age = author.current_age || 0;
      return age >= minAge && age <= maxAge;
    });
  });

  // Extract author names from filtered authors
  let authorNames = $derived.by(() => {
    if (!filteredAuthors || filteredAuthors.length === 0) return [];
    return filteredAuthors.map(author => author.name);
  });


  let filterStatus = $derived.by(() => {
    if (!dashboardState.authorAgeFilter) return '';
    const total = unique.authors.length;
    const filtered = filteredAuthors.length;
    return `(${filtered} of ${total} authors)`;
  });

  function handleSelectionChange(event) {
    const selected = Array.from(event.target.selectedOptions).map(option => option.value);
    // Only allow one selection - take the last one selected
    dashboardState.selectedAuthor = selected.length > 0 ? selected[selected.length - 1] : '';
  }
</script>

<!-- BITS-UI Accordion API: 
 Each children is understood in the context of its parent. 
 It is fully customizable, and production ready in the sense that it takes
 care of WAI-ARIA compliance, keyboard navigation by default, and more ... -->
<Accordion.Item value="author-select">
  <Accordion.Header>
    <!-- Trigger here allows the header to be collapsible. -->
    <Accordion.Trigger class="accordion-trigger">
      <UserCheck size={16} />
      Select Author {filterStatus}
    </Accordion.Trigger>
  </Accordion.Header>
  <Accordion.Content class="accordion-content">
    <div class="control-section">
      <!--  Here we pass dashboarState.selectedAuthor directly to our select widget!-->
      <select 
        multiple 
        class="filter-select-multiple"
        onchange={handleSelectionChange}
        value={dashboardState.selectedAuthor} 
      >
      <!--  authorNames is filtered based on global age filter here -->
        {#each authorNames as authorName}
          <option value={authorName} selected={dashboardState.selectedAuthor === authorName}>
            {authorName}
          </option>
        {/each}
      </select>
      <p class="filter-info">
        Select an author to filter all data. Only one can be selected at a time.
        {#if dashboardState.authorAgeFilter}
          <br><em>List filtered by age range.</em>
        {/if}
      </p>
    </div>
  </Accordion.Content>
</Accordion.Item>

<style>
  /* Style accordion */
</style>
```

In our sidebar, this can be called without any prop (similar to the rest of the sidebar subcomponents), making our code, arguably, quite readable and easily extensible:

```svelte
<script>
  import SelectAuthors from './sidebar/SelectAuthors.svelte';
  import AuthorAgeFilter from './sidebar/AuthorAgeFilter.svelte';
  import DataInfo from './sidebar/DataInfo.svelte';
  import CoauthorNodeColor from './sidebar/NodeColor.coauthor.svelte';
  import PaperNodeSize from './sidebar/NodeSize.paper.svelte';
</script>

// more code ...

<div class="sidebar-body">
  <Accordion.Root type="multiple" value={["author-select"]} class="accordion">
      <AuthorAgeFilter />
      <SelectAuthors />
      <CoauthorNodeColor />
      <PaperNodeSize />
      <DataInfo />
  </Accordion.Root>
</div>
```

Global states can be tricky, and preivously I've learned to avoid them in my `Python` code. But in this case I like it because I don't care about all the intermediary steps when passing down props in this data app. I know those global variables are always available, and declared in my `state.svelte.ts`. For instance, in my `DataInfo.svelte`, I simply do

```svelte
<script>
  import { data } from '../state.svelte.ts';
</script>

<div class="data-info-section">
  <div class="section-header">
    <span class="section-icon">📈</span>
    <span class="section-title">Author Info</span>
  </div>
  
  <div class="data-stats">
    <div class="stat-row">
      <span class="stat-label"># Papers:</span>
      <span class="stat-value">{data.paper?.length}</span>
    </div>
    <div class="stat-row">
      <span class="stat-label">Total collaborations:</span>
      <span class="stat-value">{data.coauthor?.length}</span>
    </div>
  </div>
</div>
```

Once again, no needs to pass props around and it works as expected. It was very easy to add that subcomponent, without fearing to break anything.

It is still work in progress, but so far it has proved a nice pattern I didn't see anywhere else. There might be performance issues, but so far the app can handle a fairly large datasets  without too much hassle (the `coauthor.parquet` table has 157,847 rows, which is not nothing in the fron-end world).

#### Tradeoffs of using svelte for building data apps

The tradeoff is that we need to setup some of what Frameworks was doing for us, e.g. duckdb. 
