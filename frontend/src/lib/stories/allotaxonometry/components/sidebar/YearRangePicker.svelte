<script>
    import { DateRangePicker } from "bits-ui";
    import { CalendarDate } from "@internationalized/date";

    let {
        period1 = $bindable([1950, 1959]),
        period2 = $bindable([1990, 1999]),
        minYear = 1880,
        maxYear = 2020
    } = $props();

    // Convert year arrays to date range objects
    let period1Range = $state({
        start: new CalendarDate(period1[0], 1, 1),
        end: new CalendarDate(period1[1], 12, 31)
    });

    let period2Range = $state({
        start: new CalendarDate(period2[0], 1, 1),
        end: new CalendarDate(period2[1], 12, 31)
    });

    // Update bindable props when date ranges change
    $effect(() => {
        if (period1Range?.start && period1Range?.end) {
            period1[0] = period1Range.start.year;
            period1[1] = period1Range.end.year;
        }
    });

    $effect(() => {
        if (period2Range?.start && period2Range?.end) {
            period2[0] = period2Range.start.year;
            period2[1] = period2Range.end.year;
        }
    });
</script>

<div class="picker-container">
    <!-- Period 1 -->
    <div class="period-section">
        <DateRangePicker.Root
            bind:value={period1Range}
            minValue={new CalendarDate(minYear, 1, 1)}
            maxValue={new CalendarDate(maxYear, 12, 31)}
        >
            <DateRangePicker.Label class="period-label">
                Period 1 ({period1[0]} - {period1[1]})
            </DateRangePicker.Label>

            <DateRangePicker.Trigger class="period-trigger period-1-trigger">
                {period1Range?.start && period1Range?.end
                    ? `${period1Range.start.year} - ${period1Range.end.year}`
                    : 'Select Period 1'
                }
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <rect width="18" height="18" x="3" y="4" rx="2" ry="2"/>
                    <line x1="16" x2="16" y1="2" y2="6"/>
                    <line x1="8" x2="8" y1="2" y2="6"/>
                    <line x1="3" x2="21" y1="10" y2="10"/>
                </svg>
            </DateRangePicker.Trigger>

            <DateRangePicker.Content class="picker-content">
                <DateRangePicker.Calendar class="picker-calendar" />
            </DateRangePicker.Content>
        </DateRangePicker.Root>
    </div>

    <!-- Period 2 -->
    <div class="period-section">
        <DateRangePicker.Root
            bind:value={period2Range}
            minValue={new CalendarDate(minYear, 1, 1)}
            maxValue={new CalendarDate(maxYear, 12, 31)}
        >
            <DateRangePicker.Label class="period-label">
                Period 2 ({period2[0]} - {period2[1]})
            </DateRangePicker.Label>

            <DateRangePicker.Trigger class="period-trigger period-2-trigger">
                {period2Range?.start && period2Range?.end
                    ? `${period2Range.start.year} - ${period2Range.end.year}`
                    : 'Select Period 2'
                }
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <rect width="18" height="18" x="3" y="4" rx="2" ry="2"/>
                    <line x1="16" x2="16" y1="2" y2="6"/>
                    <line x1="8" x2="8" y1="2" y2="6"/>
                    <line x1="3" x2="21" y1="10" y2="10"/>
                </svg>
            </DateRangePicker.Trigger>

            <DateRangePicker.Content class="picker-content">
                <DateRangePicker.Calendar class="picker-calendar" />
            </DateRangePicker.Content>
        </DateRangePicker.Root>
    </div>
</div>

<style>
    .picker-container {
        display: flex;
        flex-direction: column;
        gap: 1.5rem;
        padding: 1rem;
    }

    .period-section {
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
    }

    :global(.period-label) {
        font-size: var(--14px);
        font-weight: var(--font-weight-medium);
        color: var(--color-text-primary);
        margin-bottom: 0.5rem;
    }

    :global(.period-trigger) {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0.75rem 1rem;
        border: 1px solid var(--color-border);
        border-radius: var(--border-radius);
        background: white;
        cursor: pointer;
        font-size: var(--14px);
        transition: border-color var(--transition-fast) ease, box-shadow var(--transition-fast) ease;
        min-height: 2.5rem;
    }

    :global(.period-trigger:hover) {
        border-color: var(--color-text-secondary);
    }

    :global(.period-trigger:focus-visible) {
        outline: 2px solid var(--color-good-blue);
        outline-offset: 2px;
    }

    :global(.period-1-trigger[data-state="open"]) {
        border-color: var(--color-good-blue);
        box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.1);
    }

    :global(.period-2-trigger[data-state="open"]) {
        border-color: var(--color-electric-green);
        box-shadow: 0 0 0 2px rgba(34, 197, 94, 0.1);
    }

    :global(.picker-content) {
        z-index: 50;
        min-width: 20rem;
        padding: 1rem;
        border: 1px solid var(--color-border);
        border-radius: var(--border-radius);
        background: white;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
    }

    :global(.picker-calendar) {
        width: 100%;
    }

    /* Style the calendar to focus on year selection */
    :global(.picker-calendar [data-calendar-header]) {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 1rem;
    }

    :global(.picker-calendar [data-calendar-heading]) {
        font-weight: var(--font-weight-medium);
        font-size: var(--16px);
    }

    :global(.picker-calendar [data-calendar-grid]) {
        width: 100%;
        border-collapse: collapse;
        font-size: var(--12px);
    }

    :global(.picker-calendar [data-calendar-cell]) {
        padding: 0.5rem;
        text-align: center;
        position: relative;
        cursor: pointer;
        border-radius: var(--border-radius);
        transition: background-color var(--transition-fast) ease;
    }

    :global(.picker-calendar [data-calendar-cell]:hover) {
        background: var(--color-input-bg);
    }

    :global(.picker-calendar [data-calendar-cell][data-selected]) {
        background: var(--color-good-blue);
        color: white;
    }

    :global(.picker-calendar [data-calendar-cell][data-range-start]) {
        background: var(--color-good-blue);
        color: white;
    }

    :global(.picker-calendar [data-calendar-cell][data-range-end]) {
        background: var(--color-good-blue);
        color: white;
    }

    :global(.picker-calendar [data-calendar-cell][data-range-middle]) {
        background: rgba(59, 130, 246, 0.2);
    }
</style>