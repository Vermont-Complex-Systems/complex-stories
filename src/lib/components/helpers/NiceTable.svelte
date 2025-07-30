<script>
  export let data = [];
  export let title = "";
  
  // Get column headers from the first row of data
  $: headers = data.length > 0 ? Object.keys(data[0]) : [];
</script>

<div class="table-container">
  {#if title}
    <h2 class="table-title">{title}</h2>
  {/if}
  
  {#if data.length > 0}
    <table class="data-table">
      <thead>
        <tr>
          {#each headers as header}
            <th>{header}</th>
          {/each}
        </tr>
      </thead>
      <tbody>
        {#each data as row}
          <tr>
            {#each headers as header}
              <td>{row[header] ?? ''}</td>
            {/each}
          </tr>
        {/each}
      </tbody>
    </table>
  {:else}
    <p class="no-data">No data to display</p>
  {/if}
</div>

<style>
  .table-container {
    margin: 1rem 0;
    overflow-x: auto;
  }
  
  .table-title {
    margin-bottom: 1rem;
    color: #333;
    font-size: 1.5rem;
  }
  
  .data-table {
    width: 100%;
    border-collapse: collapse;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    border-radius: 8px;
    overflow: hidden;
  }
  
  .data-table th {
    background-color: #f8f9fa;
    color: #495057;
    font-weight: 600;
    padding: 12px;
    text-align: left;
    border-bottom: 2px solid #dee2e6;
  }
  
  .data-table td {
    padding: 12px;
    border-bottom: 1px solid #dee2e6;
  }
  
  .data-table tbody tr:hover {
    background-color: #f8f9fa;
  }
  
  .data-table tbody tr:last-child td {
    border-bottom: none;
  }
  
  .no-data {
    text-align: center;
    color: #6c757d;
    font-style: italic;
    padding: 2rem;
  }
</style>