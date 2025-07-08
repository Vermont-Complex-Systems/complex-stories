# Open academic Analytics

This project provide a micro-macro perspective on the coevolution of scientific productivity and collaborations.

It is macro in that we deploy models and statistics to detect statistical patterns in career trajectories.

It is micro in that we offer the possibility to users to investigate particular authors via our web interface.

### Implementing principled data processing using dagster

This project is also a dagster project, which implement a principled data processing pipeline. Here's a whirlwind tour of the approach, addressing reccurent concerns with messy, collaborative projects.

 - `Dagster offers a useful visual representation of code dependencies.` Looking at makefiles is annoying, who doesn't like to look at a shiny directed acyclic graph. 
 - `Atomizing tasks as sets of input-output scripts is up to the user.` Dagster only helps visualizing the dependencies, it does not constrain the user to adopt the PDP philosophy. As such, users must provide the dataflow such that each task takes a input, and return an output. 
 - `Duckdb working space within task`. Duckdb helps with managing complex data wrangling step, which can be reflected in the front-end. We use duckdb to manage our caching as well, using `primary keys` to avoid silly mistakes. 
 - `Integrate back-end with front-end`. Each task, or asset, have a clear pathway to the front-end, and the front-end can be used to validate the data pipeline. It is modular through and through, such that even widgets on the dashboard can be tied to relevant dependencies in the backend.
 - `Dagster accomodate more sophisticated scenarios`. Dagster helps make our web app more fancy, such as by dealing with changing APIs or automation of data intake on a daily basis.

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

