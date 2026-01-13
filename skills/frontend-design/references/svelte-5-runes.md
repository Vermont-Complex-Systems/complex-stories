---
# Svelte 5 Runes - Complete Reference

This reference provides comprehensive coverage of Svelte 5's runes syntax for Complex Stories development.

## Table of Contents
1. [Introduction to Runes](#introduction)
2. [$state - Reactive State](#state)
3. [$derived - Computed Values](#derived)
4. [$effect - Side Effects](#effect)
5. [$props - Component Props](#props)
6. [$bindable - Two-Way Binding](#bindable)
7. [Advanced Patterns](#advanced-patterns)
8. [Migration from Svelte 4](#migration)

---

## Introduction to Runes {#introduction}

Runes are Svelte 5's new primitives for reactivity. They replace Svelte 4's implicit reactivity with explicit, composable reactive values.

**Key Benefits:**
- Explicit reactivity (no magic)
- Works outside `.svelte` files (`.svelte.ts` state files)
- Better TypeScript support
- More predictable behavior

**Basic Rule:** Once you use runes in a component, ALL reactivity must use runes (no mixing with old syntax).

---

## $state - Reactive State {#state}

`$state()` creates reactive variables that trigger updates when mutated.

### Basic Usage

```javascript
let count = $state(0);
let message = $state('Hello');
let isVisible = $state(false);

// Mutations trigger reactivity
count = count + 1;
message = 'World';
isVisible = !isVisible;
```

### Objects (Deeply Reactive)

```javascript
let user = $state({
  name: 'Alice',
  age: 30,
  settings: {
    theme: 'dark',
    notifications: true
  }
});

// All mutations are reactive
user.name = 'Bob';              // Reactive
user.age++;                     // Reactive
user.settings.theme = 'light';  // Reactive (deep)
```

### Arrays (Deeply Reactive)

```javascript
let items = $state([1, 2, 3]);

// Array methods trigger reactivity
items.push(4);        // Reactive
items.pop();          // Reactive
items[0] = 10;        // Reactive
items = items.filter(x => x > 2);  // Reactive

// Map, filter, etc. must reassign
items = items.map(x => x * 2);  // Reactive
```

### Classes with State

```javascript
class Counter {
  count = $state(0);
  name = $state('Counter');

  increment() {
    this.count++;
  }

  reset() {
    this.count = 0;
  }
}

let counter = new Counter();
counter.increment();  // count is reactive
```

### State in .svelte.ts Files

```typescript
// state.svelte.ts
export const dashboardState = $state({
  selectedAuthor: 'Peter Dodds',
  filterBigPapers: true,
  colorBy: 'age_diff'
});

export const data = $state({
  papers: null,
  coauthors: null,
  isLoading: false
});
```

### $state.raw (Non-Reactive State)

For large objects where you don't need deep reactivity:

```javascript
// Deep reactivity (default)
let bigData = $state({ items: [...10000 items...] });  // Expensive

// Shallow reactivity only
let bigData = $state.raw({ items: [...10000 items...] });  // Cheap

// Mutations to bigData itself are reactive
// Mutations to bigData.items are NOT reactive
```

### $state.snapshot (Get Raw Value)

Get a non-reactive snapshot of state:

```javascript
let data = $state({ count: 0, items: [1, 2, 3] });

// Get snapshot
let snapshot = $state.snapshot(data);
console.log(snapshot);  // { count: 0, items: [1, 2, 3] }

// Snapshot is not reactive
snapshot.count = 10;  // Does NOT trigger updates

// Useful for comparisons or logging
$effect(() => {
  console.log('State changed:', $state.snapshot(data));
});
```

---

## $derived - Computed Values {#derived}

`$derived()` creates computed values that update when dependencies change.

### Simple Derivations

```javascript
let count = $state(0);

// Automatically recomputes when count changes
let doubled = $derived(count * 2);
let message = $derived(`Count is ${count}`);
let isEven = $derived(count % 2 === 0);
```

### $derived.by() for Complex Logic

Use `.by()` when derivation requires multiple statements:

```javascript
let items = $state([1, 2, 3, 4, 5]);
let threshold = $state(3);

let filtered = $derived.by(() => {
  if (!items.length) return [];

  const result = items
    .filter(x => x > threshold)
    .sort((a, b) => b - a);

  console.log('Filtered:', result);
  return result;
});
```

### Chained Derivations

```javascript
let numbers = $state([1, 2, 3, 4, 5]);

let doubled = $derived(numbers.map(x => x * 2));
let sum = $derived(doubled.reduce((a, b) => a + b, 0));
let average = $derived(sum / doubled.length);
```

### Conditional Derivations

```javascript
let data = $state(null);
let isLoading = $state(true);

let displayData = $derived.by(() => {
  if (isLoading) return 'Loading...';
  if (!data) return 'No data';
  if (data.length === 0) return 'Empty';
  return data;
});
```

### Derived with D3 Scales

```javascript
import * as d3 from 'd3';

let data = $state([10, 20, 30, 40, 50]);
let width = $state(500);

// D3 scale as derived value
let xScale = $derived(
  d3.scaleLinear()
    .domain([0, d3.max(data)])
    .range([0, width])
);

// Use in SVG
<circle cx={xScale(value)} />
```

### Derived Classes

```typescript
class DerivedData {
  // Constructor receives state
  constructor(public data: ReturnType<typeof createState>) {}

  // Derived properties
  filteredItems = $derived.by(() => {
    return this.data.items.filter(item => item.visible);
  });

  total = $derived(
    this.filteredItems.reduce((sum, item) => sum + item.value, 0)
  );

  average = $derived(
    this.filteredItems.length > 0
      ? this.total / this.filteredItems.length
      : 0
  );
}

// Usage
export const data = createState();
export const derived = new DerivedData(data);
```

---

## $effect - Side Effects {#effect}

`$effect()` runs when reactive dependencies change. Use for DOM manipulation, subscriptions, logging, etc.

### Basic Side Effects

```javascript
let count = $state(0);

// Runs after every render when count changes
$effect(() => {
  console.log('Count is now:', count);
  document.title = `Count: ${count}`;
});
```

### Cleanup Functions

Return a function to clean up side effects:

```javascript
let intervalActive = $state(false);

$effect(() => {
  if (!intervalActive) return;

  const interval = setInterval(() => {
    console.log('Tick');
  }, 1000);

  // Cleanup runs before next effect and on unmount
  return () => {
    clearInterval(interval);
    console.log('Interval cleared');
  };
});
```

### IntersectionObserver Pattern

```javascript
let elementRef;
let isVisible = $state(false);

$effect(() => {
  if (typeof window === 'undefined' || !elementRef) return;

  const observer = new IntersectionObserver(
    (entries) => {
      isVisible = entries[0].isIntersecting;
    },
    { threshold: 0.5 }
  );

  observer.observe(elementRef);

  return () => {
    observer.disconnect();
  };
});
```

### Event Listeners

```javascript
let windowWidth = $state(0);

$effect(() => {
  if (typeof window === 'undefined') return;

  function handleResize() {
    windowWidth = window.innerWidth;
  }

  handleResize();  // Initial value
  window.addEventListener('resize', handleResize);

  return () => {
    window.removeEventListener('resize', handleResize);
  };
});
```

### Scrolly State Management

```javascript
let scrollyIndex = $state(0);
let nodes = $state([...]);

$effect(() => {
  switch (scrollyIndex) {
    case 0:
      resetNodes(nodes);
      break;
    case 1:
      highlightNodes(nodes);
      break;
    case 2:
      animateNodes(nodes);
      break;
  }
});
```

### $effect.pre (Run Before DOM Updates)

Rarely needed - runs before DOM updates instead of after:

```javascript
let value = $state(0);

$effect.pre(() => {
  // Runs BEFORE DOM updates
  console.log('Old DOM state');
});

$effect(() => {
  // Runs AFTER DOM updates (default)
  console.log('New DOM state');
});
```

### $effect.tracking (Check if in Effect)

```javascript
function logValue(value) {
  if ($effect.tracking()) {
    // We're inside an effect - dependencies will be tracked
    console.log('Tracked:', value);
  } else {
    // Not in effect - no tracking
    console.log('Untracked:', value);
  }
}
```

### $effect.root (Manual Effect Management)

Create effects that don't auto-cleanup:

```javascript
const cleanup = $effect.root(() => {
  $effect(() => {
    console.log('This effect persists');
  });

  // Return cleanup function
  return () => {
    console.log('Manually cleaned up');
  };
});

// Later, manually cleanup
cleanup();
```

---

## $props - Component Props {#props}

`$props()` declares component props with destructuring and defaults.

### Basic Props

```javascript
// Child.svelte
<script>
  let { title, count = 0, onIncrement } = $props();
</script>

<h2>{title}</h2>
<p>Count: {count}</p>
<button onclick={onIncrement}>Increment</button>

<!-- Parent.svelte -->
<Child
  title="Counter"
  count={5}
  onIncrement={() => count++}
/>
```

### TypeScript Props

```typescript
<script lang="ts">
  interface Props {
    title: string;
    count?: number;
    items: Array<{ id: string; value: number }>;
    onItemClick?: (id: string) => void;
  }

  let { title, count = 0, items, onItemClick }: Props = $props();
</script>
```

### Optional Props with Defaults

```javascript
let {
  width = 500,
  height = 400,
  data = [],
  color = '#3b82f6',
  onClick = null
} = $props();

// Use with type safety
{#if onClick}
  <button onclick={() => onClick(item)}>Click</button>
{/if}
```

### Rest Props

```javascript
let { title, ...rest } = $props();

// Forward remaining props
<div {...rest}>
  <h1>{title}</h1>
</div>
```

### Reactive Props

Props are automatically reactive - no need for stores:

```javascript
// Parent changes this.props
let parentCount = $state(0);

<Child count={parentCount} />

// Child receives reactive prop
let { count } = $props();

// Automatically updates when parent changes parentCount
<p>{count}</p>
```

---

## $bindable - Two-Way Binding {#bindable}

`$bindable()` allows parent components to bind to child props.

### Basic Bindable Props

```javascript
// Scrolly.svelte (child)
<script>
  let {
    value = $bindable(undefined),
    scrollProgress = $bindable(0)
  } = $props();
</script>

<!-- Parent -->
<script>
  let currentStep = $state(0);
  let progress = $state(0);
</script>

<Scrolly bind:value={currentStep} bind:scrollProgress={progress} />

<!-- Parent automatically updates when child changes value/scrollProgress -->
<p>Step: {currentStep}, Progress: {progress}%</p>
```

### Bindable with Defaults

```javascript
// Child with bindable defaults
let {
  isOpen = $bindable(false),
  selectedItem = $bindable(null)
} = $props();

// Parent can optionally bind
<Modal bind:isOpen />  <!-- Bound -->
<Modal />  <!-- Not bound, uses default -->
```

### Computed Bindables

```javascript
// Child
let { value = $bindable(0) } = $props();

// Derived from bindable
let doubled = $derived(value * 2);

// Can update bindable from inside
function increment() {
  value++;  // Parent receives update
}
```

---

## Advanced Patterns {#advanced-patterns}

### State Management Pattern

**File:** `state.svelte.ts`

```typescript
import { loadData } from './data.remote.js';

// Application state
export const appState = $state({
  selectedAuthor: 'Peter Dodds',
  filterBigPapers: true,
  colorBy: 'age_diff'
});

// Data state
export const data = $state({
  papers: null,
  coauthors: null,
  isLoading: false
});

// Derived data using class
class DerivedData {
  filteredPapers = $derived.by(() => {
    if (!data.papers) return [];
    if (!appState.filterBigPapers) return data.papers;
    return data.papers.filter(p => p.cited_by_count < 1000);
  });

  authorList = $derived.by(() => {
    const authors = new Set(this.filteredPapers.map(p => p.author));
    return Array.from(authors).sort();
  });

  stats = $derived({
    total: this.filteredPapers.length,
    maxCitations: Math.max(...this.filteredPapers.map(p => p.cited_by_count)),
    avgCitations: this.filteredPapers.reduce((sum, p) => sum + p.cited_by_count, 0) / this.filteredPapers.length
  });
}

export const derived = new DerivedData();

// Actions
export async function loadAuthorData() {
  data.isLoading = true;
  try {
    data.papers = await loadData({ author: appState.selectedAuthor });
  } finally {
    data.isLoading = false;
  }
}
```

**Usage in component:**

```svelte
<script>
  import { appState, data, derived, loadAuthorData } from '../state.svelte';

  // Load data when author changes
  $effect(() => {
    if (appState.selectedAuthor) {
      loadAuthorData();
    }
  });
</script>

<select bind:value={appState.selectedAuthor}>
  {#each derived.authorList as author}
    <option>{author}</option>
  {/each}
</select>

<p>Total papers: {derived.stats.total}</p>
<p>Max citations: {derived.stats.maxCitations}</p>
```

### Reactive Window Dimensions

```javascript
import { innerWidth, innerHeight } from 'svelte/reactivity/window';

// Reactive breakpoints
let isMobile = $derived(innerWidth.current <= 768);
let isTablet = $derived(innerWidth.current > 768 && innerWidth.current <= 1200);
let isDesktop = $derived(innerWidth.current > 1200);

// Responsive dimensions
let vizWidth = $derived.by(() => {
  if (isMobile) return Math.min(350, innerWidth.current - 40);
  if (isTablet) return 500;
  return 650;
});
```

### Throttled/Debounced Effects

```javascript
let searchQuery = $state('');
let debouncedQuery = $state('');

$effect(() => {
  const timeout = setTimeout(() => {
    debouncedQuery = searchQuery;
  }, 300);

  return () => clearTimeout(timeout);
});

// Use debouncedQuery for expensive operations
$effect(() => {
  if (debouncedQuery) {
    performExpensiveSearch(debouncedQuery);
  }
});
```

### Coordinating Multiple Effects

```javascript
let scrollyIndex = $state(0);
let animationProgress = $state(0);

// Effect 1: Start animation when step changes
$effect(() => {
  if (scrollyIndex === 2) {
    animationProgress = 0;
  }
});

// Effect 2: Animate progress
$effect(() => {
  if (animationProgress >= 100) return;

  const interval = setInterval(() => {
    animationProgress = Math.min(100, animationProgress + 1);
  }, 16);

  return () => clearInterval(interval);
});
```

---

## Migration from Svelte 4 {#migration}

### Reactive Declarations (`$:`)

**Svelte 4:**
```javascript
let count = 0;
$: doubled = count * 2;
$: console.log(count);
```

**Svelte 5:**
```javascript
let count = $state(0);
let doubled = $derived(count * 2);
$effect(() => console.log(count));
```

### Stores

**Svelte 4:**
```javascript
import { writable } from 'svelte/store';

const count = writable(0);
$count = 5;  // Set
count.update(n => n + 1);  // Update
```

**Svelte 5:**
```javascript
let count = $state(0);
count = 5;  // Set
count = count + 1;  // Update
```

### Props

**Svelte 4:**
```javascript
export let title;
export let count = 0;
```

**Svelte 5:**
```javascript
let { title, count = 0 } = $props();
```

### Two-Way Binding

**Svelte 4:**
```javascript
// Child
export let value;

// Parent
<Child bind:value />
```

**Svelte 5:**
```javascript
// Child
let { value = $bindable() } = $props();

// Parent (same)
<Child bind:value />
```

---

## Common Pitfalls

1. **Don't mix old and new syntax** - Once you use runes, ALL reactivity must use runes

2. **State in derived** - Don't mutate state inside $derived:
   ```javascript
   // ❌ Bad
   let count = $state(0);
   let bad = $derived(count++);  // Mutates state!

   // ✅ Good
   let incremented = $derived(count + 1);
   ```

3. **Effects are not reactive statements** - They run after render, not during:
   ```javascript
   // In Svelte 4, this would be synchronous
   $: count, doSomething();

   // In Svelte 5, this is async (runs after render)
   $effect(() => {
     count;
     doSomething();
   });
   ```

4. **Derived vs Effect** - Use derived for values, effect for side effects:
   ```javascript
   // ❌ Bad
   let doubled;
   $effect(() => doubled = count * 2);

   // ✅ Good
   let doubled = $derived(count * 2);
   ```

---

## Performance Tips

1. **Use $state.raw for large objects** that don't need deep reactivity
2. **Avoid expensive derivations** - use $derived.by() to control when computation happens
3. **Debounce effects** that trigger expensive operations
4. **Use untrack() in effects** to read state without subscribing
5. **Batch state updates** - multiple assignments in same function trigger one update

---

This reference covers all common patterns used in Complex Stories. Refer to Svelte 5 docs for more advanced use cases.
