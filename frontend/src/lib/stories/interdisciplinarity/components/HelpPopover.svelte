<script>
	import { BadgeHelp } from '@lucide/svelte';
	import { Popover } from 'bits-ui'
	import { fade } from 'svelte/transition'

	let {
		iconSize = 30,
		side = 'bottom',
		align = 'center',
		sideOffset = 8
	} = $props()

	let open = $state(false)
</script>

<Popover.Root bind:open>
	<Popover.Trigger class="help-trigger" type="button" aria-label="Help information">
		<BadgeHelp size={iconSize} />
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
				<h3>Sorting & Queue Information</h3>
				<p>
					This annotation tool helps collect judgments about the interdisciplinarity of research
					papers across three different queues.
				</p>
				<ul>
					<li>
						<strong>General Queue:</strong> Curated papers from openAlex <a href="https://openalex.org/works?filter=primary_topic.id:t10064">Complex Network Analysis Techniques</a> topic.
					</li>
					<li>
						<strong>Community Queue:</strong> Papers contributed by researchers annotating their own
						work
					</li>
					<li>
						<strong>My Papers:</strong> Your own publications fetched from ORCID/OpenAlex
					</li>
				</ul>
				<h4>Sorting Options</h4>
				<ul>
					<li><strong>Default:</strong> Original order from the queue</li>
					<li>
						<strong>Year:</strong> Sort by publication year (newest first). Community and My Papers
						sort properly; CSV papers may appear random as metadata loads lazily.
					</li>
					<li><strong>Random:</strong> Fisher-Yates shuffle for unbiased annotation order</li>
					<li>
						<strong>Disagreement:</strong> Papers with the most disagreement among annotators appear
						first (requires multiple annotations)
					</li>
				</ul>
				<p class="help-note">
					Sorting in the Overview table affects the order in all queues. Use "Annotate" to jump to
					that paper in its queue.
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
		color: #666;
		transition:
			color 0.2s,
			background-color 0.2s;
		border-radius: 4px;
	}

	:global(.help-trigger:hover) {
		color: #2563eb;
		background-color: rgba(37, 99, 235, 0.05);
	}

	:global(.help-trigger[data-state='open']) {
		color: #2563eb;
		background-color: rgba(37, 99, 235, 0.1);
	}

	:global(.help-content) {
		background-color: white;
		border: 1px solid #e0e0e0;
		border-radius: 8px;
		padding: 1rem;
		box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
		max-width: 450px;
		z-index: 1000;
	}

	:global(.help-arrow) {
		fill: white;
		filter: drop-shadow(0 -1px 0 #e0e0e0);
	}

	.help-text h3 {
		margin: 0 0 0.75rem 0;
		font-size: 1rem;
		font-weight: 600;
		color: #333;
	}

	.help-text h4 {
		margin: 0.75rem 0 0.5rem 0;
		font-size: 0.9rem;
		font-weight: 600;
		color: #444;
	}

	.help-text p {
		margin: 0 0 0.75rem 0;
		font-size: 0.875rem;
		line-height: 1.5;
		color: #555;
	}

	.help-text ul {
		margin: 0 0 0.75rem 0;
		padding-left: 1.25rem;
		font-size: 0.875rem;
		line-height: 1.6;
		color: #555;
	}

	.help-text li {
		margin-bottom: 0.5rem;
	}

	.help-text li:last-child {
		margin-bottom: 0;
	}

	.help-text strong {
		font-weight: 600;
		color: #333;
	}

	.help-note {
		font-style: italic;
		font-size: 0.8rem;
		color: #777;
		margin-bottom: 0;
	}
</style>
