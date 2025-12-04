<script>
    import { CircleHelp } from '@lucide/svelte';
    import { Popover } from "bits-ui";
    import { fade } from 'svelte/transition';

    let {
        iconSize = 20,
        side = 'bottom',
        align = 'center',
        sideOffset = 8
    } = $props();

    let open = $state(false);
</script>

<Popover.Root bind:open>
    <Popover.Trigger class="help-trigger" type="button" aria-label="Help information">
        <CircleHelp size={iconSize} />
    </Popover.Trigger>
    <Popover.Portal>
        <Popover.Content
            {side}
            {align}
            {sideOffset}
            class="help-content"
            transition={fade}
            transitionConfig={{ duration: 150 }}
        >
            <div class="help-text">
                <h3>How the Allotaxonograph Works</h3>
                <p>
                    The Allotaxonograph visualizes differences in word usage between two time periods or countries on Wikipedia.
                </p>
                <ul>
                    <li><strong>Word Shift Graph:</strong> Shows which terms increased or decreased relative to divergence contribution, as calculated by the rank-turbulence metric. See <a href="https://epjdatascience.springeropen.com/articles/10.1140/epjds/s13688-023-00400-x">paper</a> for details.</li>
                    <li><strong>Alpha (α):</strong> Controls the normalization parameter - Try α = ∞, you will see that types tend to be similarly ranked with their frequency. By contrast, α = 0 allows us to inspect what is happening further down in the tail. </li>
                    <li><strong>Top N:</strong> Number of most frequent terms to include in the comparison</li>
                    <li><strong>Label threshold:</strong> We only show labels for which the counts per cell is less or equal to three</li>
                </ul>
                <p class="help-note">
                    Click on any term to see its contribution to the overall difference between the two distributions.
                </p>
            </div>
            <Popover.Arrow class="help-arrow" />
        </Popover.Content>
    </Popover.Portal>
</Popover.Root>

<style>
    :global(.help-trigger) {
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 0.5rem;
        background: none;
        border: none;
        cursor: pointer;
        color: var(--color-fg, #666);
        transition: color 0.2s, background-color 0.2s;
        border-radius: 4px;
    }

    :global(.help-trigger:hover) {
        color: var(--color-good-blue, #2563eb);
        background-color: rgba(37, 99, 235, 0.05);
    }

    :global(.help-trigger[data-state="open"]) {
        color: var(--color-good-blue, #2563eb);
        background-color: rgba(37, 99, 235, 0.1);
    }

    :global(.help-content) {
        background-color: white;
        border: 1px solid var(--color-border, #e0e0e0);
        border-radius: 8px;
        padding: 1rem;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        max-width: 400px;
        z-index: 1000;
    }

    :global(.help-arrow) {
        fill: white;
        filter: drop-shadow(0 -1px 0 var(--color-border, #e0e0e0));
    }

    .help-text h3 {
        margin: 0 0 0.75rem 0;
        font-size: 1rem;
        font-weight: 600;
        color: var(--color-fg, #333);
    }

    .help-text p {
        margin: 0 0 0.75rem 0;
        font-size: 0.875rem;
        line-height: 1.5;
        color: var(--color-fg, #555);
    }

    .help-text ul {
        margin: 0 0 0.75rem 0;
        padding-left: 1.25rem;
        font-size: 0.875rem;
        line-height: 1.6;
        color: var(--color-fg, #555);
    }

    .help-text li {
        margin-bottom: 0.5rem;
    }

    .help-text li:last-child {
        margin-bottom: 0;
    }

    .help-text strong {
        font-weight: 600;
        color: var(--color-fg, #333);
    }

    .help-note {
        font-style: italic;
        font-size: 0.8rem;
        color: var(--color-fg, #777);
        margin-bottom: 0;
    }
</style>
