# Open academic Analytics

This project offers s micro-macro perspective on the coevolution of scientific productivity and collaborations. It is macro in that we deploy models and statistics to detect statistical patterns in career trajectories. It is micro in that we offer the possibility to users to investigate particular authors via our web interface. Here's a snapshot of the interface, you can find the live version [here](https://vermont-complex-systems.github.io/complex-stories/open-academic-analytics). We use faculties at University of Vermont as example.

<img width="1500" alt="open-academic-dashboard" src="https://github.com/user-attachments/assets/068730b0-4273-48cb-ab29-602be5340f06" />

### Missing 

 - [x] Missing bayesian switchpoint model to detect when faculties start collaborating more extensively with younger collaborators. Perhaps we could use that to predict from data the existence of research groups
 - [ ] Aggregate plots where we can do some statistics.
   - [ ] time series plot where horizontal axis is standardized age, vertical axis is number of collaborations, and color is (bucketized) relative academic age. That is, what is the proportion of all authors that start to collaborate more extensively with younger authors starting at, say, `academic_age = 10`? How is that different across colleges? Within college, how are faculties with research groups differ from non-PIs.
 - [ ] Global filters
   - [ ] Add h-index filter to get uvm superstars
   - [ ] Add a departments/colleges brush filter
   - [ ] Add a toggle to filter based on whether faculties have a research groups

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


### Front-end: A very svelte dashboard

 - `Fully customizable dashboard`: Integrates seamlessly with the front-end ecosystems, using [bits-ui](https://bits-ui.com/) for creating all kinds of components (sidebar, toggle, filters, etc). 
 - `High-level abstraction`: Making use of [svelte-plot](https://svelteplot.dev/) for high-level charting.
 - `Data transformation powered by duckdb`: As with our back-end, we use duckdb to wrangle data on the fly. Using duckdb both for back-end and fron-end as tremendous advantage, helping with maintainability.

This is work in progress. But we try to stay organized by decomposing our dashboard with as many subcomponents as necessary. 

```
.
├── assets // dagster assets building the data pipeline
├── components // svelte components
│   ├── ChangePointChart.svelte
│   ├── CoauthorChart.svelte
│   ├── Collaboration.Agg.svelte // denote aggregate charts with `.Agg` suffix
│   ├── Dashboard.svelte
│   ├── helpers // Inputs and other misc components
│   │   ├── RangeFilter.svelte
│   │   ├── ThemeToggle.svelte
│   │   ├── Toggle.svelte
│   │   └── TutorialPopup.svelte
│   ├── Index.svelte // main component
│   ├── Legend.svelte
│   ├── Nav.svelte
│   ├── PaperChart.svelte
│   ├── Productivity.Agg.svelte
│   ├── sidebar
│   │   ├── AuthorAgeFilter.svelte
│   │   ├── ColorModeFilter.svelte
│   │   ├── DataInfo.svelte
│   │   ├── HighlightCoauthorFilter.svelte
│   │   └── SelectAuthors.svelte
│   └── Sidebar.svelte 
├── data
│   ├── copy.json
│   └── loader.js // duckdb loader, loading parquet files from static/
├── state.svelte.ts // centralized states to manage dashboard
└── utils
    └── combinedChartUtils.js
```

We are experimenting with centralizing our data work as much as we can in our `state.svelte.ts`. This is where we query our data using `duckdb`, making it efficient even as data increases in size. By taking advantage of Svelte new system of [Universal reactivity](https://svelte.dev/tutorial/svelte/universal-reactivity), we ensure that data is available to all our components are once and that everything remain in sync...