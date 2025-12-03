<script>
    import { RangeCalendar } from "bits-ui";
    import { CalendarDate } from "@internationalized/date";

    let {
        period1 = $bindable([1950, 1959]),
        period2 = $bindable([1990, 1999]),
        minYear = 1880,
        maxYear = 2020
    } = $props();

    // Convert year ranges to CalendarDate ranges for the calendar component
    let period1Range = $state({
        start: new CalendarDate(period1[0], 1, 1),
        end: new CalendarDate(period1[1], 12, 31)
    });

    let period2Range = $state({
        start: new CalendarDate(period2[0], 1, 1),
        end: new CalendarDate(period2[1], 12, 31)
    });

    // Update the bindable props when calendar ranges change
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

    // Generate years for display (we'll show them in decade chunks)
    let currentDecade1 = $state(Math.floor(period1[0] / 10) * 10);
    let currentDecade2 = $state(Math.floor(period2[0] / 10) * 10);

    function navigateDecade(calendarIndex, direction) {
        const newDecade = (calendarIndex === 1 ? currentDecade1 : currentDecade2) + (direction * 10);
        if (newDecade >= minYear && newDecade <= maxYear) {
            if (calendarIndex === 1) {
                currentDecade1 = newDecade;
            } else {
                currentDecade2 = newDecade;
            }
        }
    }

    function generateYearsForDecade(startYear) {
        const years = [];
        for (let year = startYear; year < startYear + 10 && year <= maxYear; year++) {
            years.push(year);
        }
        return years;
    }

    function isYearInRange(year, range) {
        if (!range?.start || !range?.end) return false;
        return year >= range.start.year && year <= range.end.year;
    }

    function selectYear(year, calendarIndex) {
        const range = calendarIndex === 1 ? period1Range : period2Range;

        if (!range?.start) {
            // First click - set start
            const newRange = {
                start: new CalendarDate(year, 1, 1),
                end: null
            };
            if (calendarIndex === 1) {
                period1Range = newRange;
            } else {
                period2Range = newRange;
            }
        } else if (!range?.end) {
            // Second click - set end
            const startYear = range.start.year;
            const endYear = year;
            const newRange = {
                start: new CalendarDate(Math.min(startYear, endYear), 1, 1),
                end: new CalendarDate(Math.max(startYear, endYear), 12, 31)
            };
            if (calendarIndex === 1) {
                period1Range = newRange;
            } else {
                period2Range = newRange;
            }
        } else {
            // Range already set - start new range
            const newRange = {
                start: new CalendarDate(year, 1, 1),
                end: null
            };
            if (calendarIndex === 1) {
                period1Range = newRange;
            } else {
                period2Range = newRange;
            }
        }
    }
</script>

<div class="calendar-container">
    <!-- Period 1 Calendar -->
    <div class="period-calendar">
        <div class="calendar-header">
            <span class="period-title">Period 1</span>
            <span class="period-range">{period1[0]} - {period1[1]} ({period1[1] - period1[0] + 1} years)</span>
        </div>

        <div class="decade-navigation">
            <button
                class="nav-button"
                onclick={() => navigateDecade(1, -1)}
                disabled={currentDecade1 <= minYear}
            >
                ←
            </button>
            <span class="decade-label">{currentDecade1}s</span>
            <button
                class="nav-button"
                onclick={() => navigateDecade(1, 1)}
                disabled={currentDecade1 + 10 > maxYear}
            >
                →
            </button>
        </div>

        <RangeCalendar.Root
            bind:value={period1Range}
            minValue={new CalendarDate(minYear, 1, 1)}
            maxValue={new CalendarDate(maxYear, 12, 31)}
            class="year-calendar"
        >
            {#snippet children({ months, weekdays })}
                <div class="years-grid">
                    {#each generateYearsForDecade(currentDecade1) as year}
                        <button
                            class="year-cell {isYearInRange(year, period1Range) ? 'selected' : ''} period-1"
                            onclick={() => selectYear(year, 1)}
                        >
                            {year}
                        </button>
                    {/each}
                </div>
            {/snippet}
        </RangeCalendar.Root>
    </div>

    <!-- Period 2 Calendar -->
    <div class="period-calendar">
        <div class="calendar-header">
            <span class="period-title">Period 2</span>
            <span class="period-range">{period2[0]} - {period2[1]} ({period2[1] - period2[0] + 1} years)</span>
        </div>

        <div class="decade-navigation">
            <button
                class="nav-button"
                onclick={() => navigateDecade(2, -1)}
                disabled={currentDecade2 <= minYear}
            >
                ←
            </button>
            <span class="decade-label">{currentDecade2}s</span>
            <button
                class="nav-button"
                onclick={() => navigateDecade(2, 1)}
                disabled={currentDecade2 + 10 > maxYear}
            >
                →
            </button>
        </div>

        <RangeCalendar.Root
            bind:value={period2Range}
            minValue={new CalendarDate(minYear, 1, 1)}
            maxValue={new CalendarDate(maxYear, 12, 31)}
            class="year-calendar"
        >
            {#snippet children({ months, weekdays })}
                <div class="years-grid">
                    {#each generateYearsForDecade(currentDecade2) as year}
                        <button
                            class="year-cell {isYearInRange(year, period2Range) ? 'selected' : ''} period-2"
                            onclick={() => selectYear(year, 2)}
                        >
                            {year}
                        </button>
                    {/each}
                </div>
            {/snippet}
        </RangeCalendar.Root>
    </div>
</div>

<style>
    .calendar-container {
        display: flex;
        flex-direction: column;
        gap: 2rem;
        padding: 1rem;
    }

    .period-calendar {
        display: flex;
        flex-direction: column;
        gap: 1rem;
    }

    .calendar-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .period-title {
        font-weight: var(--font-weight-medium);
        font-size: var(--14px);
        color: var(--color-text-primary);
    }

    .period-range {
        font-size: var(--12px);
        color: var(--color-text-secondary);
        font-weight: var(--font-weight-medium);
    }

    .decade-navigation {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 1rem;
        padding: 0.5rem 0;
    }

    .nav-button {
        width: 2rem;
        height: 2rem;
        border: 1px solid var(--color-border);
        background: white;
        border-radius: var(--border-radius);
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: var(--font-weight-bold);
        transition: background-color var(--transition-fast) ease;
    }

    .nav-button:hover:not(:disabled) {
        background: var(--color-input-bg);
    }

    .nav-button:disabled {
        opacity: 0.5;
        cursor: not-allowed;
    }

    .decade-label {
        font-weight: var(--font-weight-medium);
        font-size: var(--14px);
        min-width: 4rem;
        text-align: center;
    }

    :global(.year-calendar) {
        width: 100%;
    }

    .years-grid {
        display: grid;
        grid-template-columns: repeat(5, 1fr);
        gap: 0.5rem;
        padding: 1rem;
        border: 1px solid var(--color-border);
        border-radius: var(--border-radius);
        background: white;
    }

    .year-cell {
        padding: 0.75rem 0.5rem;
        border: 1px solid var(--color-border);
        background: white;
        border-radius: var(--border-radius);
        cursor: pointer;
        font-size: var(--12px);
        font-weight: var(--font-weight-medium);
        transition: all var(--transition-fast) ease;
        color: var(--color-text-primary);
    }

    .year-cell:hover {
        background: var(--color-input-bg);
    }

    .year-cell.selected.period-1 {
        background: var(--color-good-blue);
        color: white;
        border-color: var(--color-good-blue);
    }

    .year-cell.selected.period-2 {
        background: var(--color-electric-green);
        color: white;
        border-color: var(--color-electric-green);
    }
</style>