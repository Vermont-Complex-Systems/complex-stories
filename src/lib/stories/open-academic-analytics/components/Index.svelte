<script>
    import {  data, initializeApp } from './state.svelte.js';
    
    // Initialize on component mount
    initializeApp();

    $inspect(data.paper)
</script>