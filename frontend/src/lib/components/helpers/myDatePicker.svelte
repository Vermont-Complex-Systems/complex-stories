<script lang="ts">
  import { DatePicker } from "bits-ui";
  import { Calendar, ChevronLeft, ChevronRight } from "@lucide/svelte";

  let {
    value = $bindable(),
    isDateUnavailable = undefined,
    disabled = false
  } = $props();
</script>

<DatePicker.Root
  weekdayFormat="short"
  fixedWeeks={true}
  bind:value
  {isDateUnavailable}
  {disabled}
  locale="en-CA"
>
  <DatePicker.Input>
    {#snippet children({ segments })}
      <div class="datepicker-input">
        {#each segments as { part, value }, i (part + i)}
          {#if part === "literal"}
            <DatePicker.Segment {part}>
              {#snippet child({ props })}
                <span {...props} class="segment-literal">{value}</span>
              {/snippet}
            </DatePicker.Segment>
          {:else}
            <DatePicker.Segment {part}>
              {#snippet child({ props })}
                <span {...props} class="segment-value">{value}</span>
              {/snippet}
            </DatePicker.Segment>
          {/if}
        {/each}

        <DatePicker.Trigger>
          {#snippet child({ props })}
            <button {...props} class="calendar-trigger">
              <Calendar class="calendar-icon" />
            </button>
          {/snippet}
        </DatePicker.Trigger>
      </div>
    {/snippet}
  </DatePicker.Input>

  <DatePicker.Content sideOffset={6}>
    <DatePicker.Calendar>
      {#snippet children({ months, weekdays })}
        <div class="calendar-popup">
          <DatePicker.Header>
            {#snippet child({ props })}
              <div {...props} class="calendar-header">
                <DatePicker.PrevButton>
                  {#snippet child({ props: btnProps })}
                    <button {...btnProps} class="nav-button">
                      <ChevronLeft />
                    </button>
                  {/snippet}
                </DatePicker.PrevButton>

                <DatePicker.Heading class="calendar-heading" />

                <DatePicker.NextButton>
                  {#snippet child({ props: btnProps })}
                    <button {...btnProps} class="nav-button">
                      <ChevronRight />
                    </button>
                  {/snippet}
                </DatePicker.NextButton>
              </div>
            {/snippet}
          </DatePicker.Header>

          <div class="calendar-body">
            {#each months as month (month.value)}
              <DatePicker.Grid>
                {#snippet child({ props })}
                  <div {...props} class="calendar-grid">
                    <DatePicker.GridHead>
                      {#snippet child({ props: headProps })}
                        <div {...headProps} class="grid-head">
                          <DatePicker.GridRow>
                            {#snippet child({ props: rowProps })}
                              <div {...rowProps} class="grid-row">
                                {#each weekdays as day (day)}
                                  <DatePicker.HeadCell>
                                    {#snippet child({ props: cellProps })}
                                      <div {...cellProps} class="head-cell">
                                        {day.slice(0, 2)}
                                      </div>
                                    {/snippet}
                                  </DatePicker.HeadCell>
                                {/each}
                              </div>
                            {/snippet}
                          </DatePicker.GridRow>
                        </div>
                      {/snippet}
                    </DatePicker.GridHead>

                    <DatePicker.GridBody>
                      {#snippet child({ props: bodyProps })}
                        <div {...bodyProps} class="grid-body">
                          {#each month.weeks as weekDates (weekDates)}
                            <DatePicker.GridRow>
                              {#snippet child({ props: rowProps })}
                                <div {...rowProps} class="grid-row">
                                  {#each weekDates as date (date)}
                                    <DatePicker.Cell {date} month={month.value}>
                                      {#snippet child({ props: cellProps })}
                                        <div {...cellProps} class="date-cell">
                                          <DatePicker.Day>
                                            {#snippet child({ props: dayProps })}
                                              <button {...dayProps} class="date-day">
                                                <div class="today-indicator"></div>
                                                {date.day}
                                              </button>
                                            {/snippet}
                                          </DatePicker.Day>
                                        </div>
                                      {/snippet}
                                    </DatePicker.Cell>
                                  {/each}
                                </div>
                              {/snippet}
                            </DatePicker.GridRow>
                          {/each}
                        </div>
                      {/snippet}
                    </DatePicker.GridBody>
                  </div>
                {/snippet}
              </DatePicker.Grid>
            {/each}
          </div>
        </div>
      {/snippet}
    </DatePicker.Calendar>
  </DatePicker.Content>
</DatePicker.Root>

<style>
  /* Input field */
  .datepicker-input {
    display: flex;
    align-items: center;
    width: 100%;
    max-width: 130px;
    padding: 0.375rem 0.5rem;
    border: 1px solid #ddd;
    border-radius: 4px;
    background: transparent;
    font-size: 0.875rem;
  }

  .segment-literal {
    padding: 0 0.125rem;
    color: #666;
  }

  .segment-value {
    padding: 0.125rem;
  }

  .segment-value:focus {
    color: #171717;
  }

  .segment-value[aria-valuetext="Empty"] {
    color: #999;
  }

  .calendar-trigger {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    padding: 0.25rem;
    margin-left: 0.25rem;
    background: transparent;
    border: none;
    cursor: pointer;
  }

  .calendar-trigger:hover {
    opacity: 0.7;
  }

  :global(.calendar-icon) {
    width: 1rem;
    height: 1rem;
    color: black;
  }

  /* Calendar popup */
  .calendar-popup {
    background: white;
    border: 1px solid rgba(0, 0, 0, 0.1);
    border-radius: 15px;
    padding: 22px;
    box-shadow: 0px 7px 12px 3px rgba(0, 0, 0, 0.1);
    z-index: 50;
  }

  /* Header */
  .calendar-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 1rem;
  }

  .nav-button {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 40px;
    height: 40px;
    border-radius: 9px;
    background: transparent;
    border: none;
    cursor: pointer;
    transition: all 0.2s;
  }

  .nav-button:hover {
    background: rgba(0, 0, 0, 0.05);
  }

  .nav-button:active {
    transform: scale(0.98);
  }

  .nav-button :global(svg) {
    width: 24px;
    height: 24px;
    color: #171717;
  }

  .calendar-heading {
    font-size: 15px;
    font-weight: 500;
  }

  /* Calendar body */
  .calendar-body {
    display: flex;
    flex-direction: column;
    gap: 1rem;
    padding-top: 1rem;
  }

  .calendar-grid {
    width: 100%;
    border-collapse: collapse;
    user-select: none;
  }

  .grid-head {
    margin-bottom: 0.25rem;
  }

  .grid-body {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
  }

  .grid-row {
    display: flex;
    width: 100%;
    justify-content: space-between;
    gap: 0;
  }

  .head-cell {
    width: 40px;
    color: rgba(23, 23, 23, 0.4);
    font-weight: normal;
    font-size: 0.75rem;
    text-align: center;
  }

  /* Date cells */
  .date-cell {
    padding: 0;
    position: relative;
    width: 40px;
    height: 40px;
    text-align: center;
  }

  .date-day {
    color: #171717;
    border: 1px solid transparent;
    border-radius: 9px;
    background: transparent;
    width: 40px;
    height: 40px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    position: relative;
    font-size: 0.875rem;
    font-weight: 400;
    transition: all 0.2s;
    cursor: pointer;
    white-space: nowrap;
  }

  .date-day:hover {
    border-color: #171717;
  }

  .date-day[data-selected] {
    background: #171717;
    color: white;
    font-weight: 500;
  }

  .date-day[data-disabled] {
    color: rgba(23, 23, 23, 0.3);
    pointer-events: none;
  }

  .date-day[data-unavailable] {
    color: rgba(23, 23, 23, 0.4);
    text-decoration: line-through;
  }

  .date-day[data-outside-month] {
    pointer-events: none;
    opacity: 0.3;
  }

  /* Today indicator */
  .today-indicator {
    position: absolute;
    top: 5px;
    width: 4px;
    height: 4px;
    border-radius: 50%;
    background: #171717;
    display: none;
    transition: all 0.2s;
  }

  .date-day[data-today] .today-indicator {
    display: block;
  }

  .date-day[data-selected] .today-indicator {
    background: white;
  }
</style>
