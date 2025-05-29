<script>
    import { Plot, Dot } from 'svelteplot';
    import { group, mean } from 'd3-array';
    import Spinner from '$lib/components/helpers/Spinner.svelte';
    import { clone } from '../utils/correlation';

    let { nodes, nodes_xy, Manylinks, mainNode, targetNode, scrollyIndex } = $props();

    let data = $state([]);  
    let averageDataS = $state([]);
    let averageDataM = $state([]);
    let selectedMetric = $state('pearsonR');
    let isLoaded = $state(false);
    
    // Use $effect instead of onMount
    $effect(() => {       
        // Ensure nodes exist
        if (!mainNode || !targetNode) {
            console.log('Missing nodes:', { mainNode, targetNode });
            return;
        }

        console.log('Starting worker computation...');
        
        const worker = new Worker(new URL('../utils/correlation-worker.ts', import.meta.url), {
            type: 'module'
        });

        const sValues = [1, 50, 100, 300, 500, 700, 1000, 1200, 1400];

        worker.postMessage({
            nodes: clone(nodes_xy),
            initialNodes: clone(nodes),
            manyLinks: Manylinks,
            sourceNodeId: mainNode.id,
            targetNodeId: targetNode.id,
            r: 0.2,
            sValues,
            maxSteps: 100,
            trials: 1000,
            mode: 'multi-pair-sweep'
        });

        worker.onmessage = (e) => {
            console.log('Worker completed!', e.data);
            data = [e.data];
            
            averageDataS = Array.from(
                group(e.data, d => d.s),
                ([s, entries]) => ({
                    s,
                    MI: mean(entries, d => d.MI),
                    correlationRatio: mean(entries, d => d.correlationRatio),
                    pearsonR: mean(entries, d => d.pearsonR),
                    structuralSimilarity: mean(entries, d => d.structuralSimilarity)
                })
            );
            
            averageDataM = Array.from(
                group(e.data, d => d.structuralSimilarity),
                ([structuralSimilarity, entries]) => ({
                    structuralSimilarity,
                    MI: mean(entries, d => d.MI),
                    correlationRatio: mean(entries, d => d.correlationRatio),
                    pearsonR: mean(entries, d => d.pearsonR)
                })
            );
            
            isLoaded = true;
        };

        worker.onerror = (error) => {
            console.error('Worker error:', error);
            isLoaded = true; // Stop loading on error
        };

        // Cleanup function - this is crucial!
        return () => {
            console.log('Terminating worker...');
            worker.terminate();
        };
    });
</script>

{#if scrollyIndex > 1}
    <!-- Metric selector -->
    <div style="margin-bottom: 1rem;">
        <label for="metric">Y Axis:</label>
        <select id="metric" bind:value={selectedMetric}>
            <option value="MI">Mutual Information</option>
            <option value="pearsonR">Pearson Correlation</option>
            <option value="correlationRatio">Correlation Ratio</option>
        </select>
    </div>
    
    {#if !isLoaded}
        <div>
            <Spinner />
        </div>
    {:else}
        <Plot grid>
            <Dot data={averageDataS} x="s" y={selectedMetric} />
        </Plot>
        {#if scrollyIndex > 2}
            <div>
                <Plot grid>
                    <Dot data={averageDataM} x='structuralSimilarity' y={selectedMetric}/>
                </Plot>
            </div>
        {/if}
    {/if}
{/if}
