<script>
	import { Plot, BarY, RuleY } from 'svelteplot'

	let {
		data = [],
		fill = '#6b7280',
		stroke = '#374151',
		height = 350
	} = $props()

	const domain = [
		'Very much interdisciplinary',
		'Somewhat interdisciplinary',
		'Undecided',
		'Not really interdisciplinary',
		'Not at all interdisciplinary'
	]
</script>

<Plot
	y={{ grid: true, label: 'Number of Papers' }}
	x={{
		tickRotate: -15,
		label: 'Interdisciplinarity Rating',
		domain
	}}
	marginTop={25}
	marginRight={25}
	marginBottom={100}
	{height}>
	<BarY
		{data}
		y="count"
		x="rating"
		{fill}
		{stroke}
	/>
	<RuleY data={[0]} />
</Plot>
