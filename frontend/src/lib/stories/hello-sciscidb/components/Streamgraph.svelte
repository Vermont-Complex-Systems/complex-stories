<script>
    import { Plot, AreaY, RuleY, Text } from 'svelteplot';
    import { tweened } from 'svelte/motion';
    import { cubicOut } from 'svelte/easing';
    import { extent } from 'd3-array';
    import { schemeSet3 } from 'd3-scale-chromatic';

    let { data, offset = $bindable(), clicked = $bindable() } = $props();

    // Create a stable color mapping for all fields
    const allFields = $derived([...new Set(data.map(d => d.field))].sort());
    const colorMapping = $derived(Object.fromEntries(
        allFields.map((field, i) => [field, schemeSet3[i % schemeSet3.length]])
    ));

    const dataTweened = tweened([], {
        duration: 2000,
        easing: cubicOut,
        interpolate: (a, b) => {
            return (t) => {
                if (!a.length) return b;
                if (!b.length) return a;

                return b.map((item, i) => ({
                    ...item,
                    count: a[i] ? a[i].count + (item.count - a[i].count) * t : item.count
                }));
            };
        }
    });

    // Update tweened data when props change
    $effect(() => {
        dataTweened.set(data);
    });

    // Get the current tweened value
    let currentData = $state([]);
    $effect(() => {
        dataTweened.subscribe(value => {
            currentData = value;
        });
    });
</script>

<Plot 
    x={{ grid: offset === 'normalize' ? false : true}} 
    y={{
        axis: offset === 'none' ? 'left' : false,
        grid: offset === 'none' ? true : false
        }} 
    marginLeft={offset === 'none' ? 40 : 15}
    marginRight={15} 
    color={{legend: true, scheme: "paired"}}
    caption="Color sorting by sum of papers, or ordered series by their total value. The biggest sum is at the bottom."
    >
        <AreaY
            data={currentData}
            x="year"
            y="count"
            z="field"
            fill="field"
            stroke="white"
            strokeOpacity=0.1
            stack={{
                order: 'sum',
                offset: offset,
                reverse: true
            }}
            cursor="pointer"
            opacity={{
                scale: null,
                value: (d) =>
                        !clicked || clicked === d.field ? 0.8 : 0.3
            }}
            onclick={(event, d) => {
                clicked = clicked === d.field ? null : d.field; // or d.data.field, depending on structure
            }}
        />
    </Plot>