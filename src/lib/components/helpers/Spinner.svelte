<!-- In Spinner.svelte -->
<div id="loading"></div>
<style>
  #loading {
    display: inline-block;
    width: 50px;
    height: 50px;
    border: 3px solid rgba(255, 23, 23, 0.3);
    border-radius: 50%;
    border-top-color: rgb(175, 23, 23);
    animation: spin 1s ease-in-out infinite;
    -webkit-animation: spin 1s ease-in-out infinite;
  }

  @keyframes spin {
    to { -webkit-transform: rotate(360deg); }
  }
  @-webkit-keyframes spin {
    to { -webkit-transform: rotate(360deg); }
  }
</style>