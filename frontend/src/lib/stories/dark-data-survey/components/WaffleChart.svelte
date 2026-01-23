<script>
    import { Plot, RuleY, groupY, WaffleX } from 'svelteplot';
    import penguins from '../data/penguins.csv';
</script>

<Plot
    height={400}
    x={{ grid: true }}
    color={{ legend: true }}>
    <WaffleX
        gap={2}
        borderRadius={2}
        {...groupY(
            {
                data: penguins,
                y: 'island',
                fill: 'species'
            },
            { x: 'count' }
        )} />
</Plot>
