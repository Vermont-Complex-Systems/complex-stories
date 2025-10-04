<script>
    import { flip } from 'svelte/animate';

    let items = $state([
        { id: 'A', value: 1 },
        { id: 'B', value: 2 },
        { id: 'C', value: 3 },
        { id: 'D', value: 4 },
        { id: 'E', value: 5 }
    ]);

    function randomizeValues() {
        // Update values randomly
        items.forEach(item => {
            item.value = Math.random() * 10;
        });
        // Force reactivity
        items = items;
    }

    function sortItems() {
        items = [...items].sort((a, b) => a.value - b.value);
    }

    function randomizeAndSort() {
        randomizeValues();
        sortItems();
    }

    // Sorted version using $derived - THIS DOESN'T WORK
    let sortedDerived = $derived([...items].sort((a, b) => a.value - b.value));
</script>

<div style="padding: 20px; background: #1a1a1a; color: white;">
    <h3>Test 1: Manual sort (should work)</h3>
    <button onclick={randomizeAndSort}>Randomize & Sort</button>

    <div style="margin: 20px 0;">
        {#each items as item (item.id)}
            <div
                animate:flip={{ duration: 500 }}
                style="padding: 10px; margin: 5px; background: #333; border-radius: 4px;"
            >
                {item.id}: {item.value.toFixed(2)}
            </div>
        {/each}
    </div>

    <h3>Test 2: $derived sort (WON'T work - creates new array)</h3>
    <button onclick={randomizeValues}>Just Randomize Values</button>

    <div style="margin: 20px 0;">
        {#each sortedDerived as item (item.id)}
            <div
                animate:flip={{ duration: 500 }}
                style="padding: 10px; margin: 5px; background: #555; border-radius: 4px;"
            >
                {item.id}: {item.value.toFixed(2)}
            </div>
        {/each}
    </div>
</div>

<style>
    button {
        padding: 8px 16px;
        background: #4CAF50;
        color: white;
        border: none;
        border-radius: 4px;
        cursor: pointer;
    }

    button:hover {
        background: #45a049;
    }
</style>
