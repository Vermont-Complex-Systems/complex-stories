<script>
  
  let { 
    value = $bindable(),
    options = [],
    minWidth = 200
  } = $props();

</script>

<div class="select-container" style="width: {minWidth}px;">
  <select bind:value class="styled-select">
    {#each options as option}
      <option value={option}>{option}</option>
    {/each}
  </select>
</div>

<style>
  .select-container {
    display: flex;
    flex-direction: column;
    gap: 4px;
    margin: 0 0 5px 0;
  }
</style>