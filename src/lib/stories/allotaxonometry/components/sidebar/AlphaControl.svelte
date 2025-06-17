<script>
    import * as d3 from "d3";
    import { Accordion } from "bits-ui";
    
    let { alpha = $bindable(0.58) } = $props();
    
    const alphas = d3.range(0,18).map(v => +(v/12).toFixed(2)).concat([1, 2, 5, Infinity]);
    let alphaIndex = $state(7); // Start at 0.58

    $effect(() => {
        alpha = alphas[alphaIndex];
    });
</script>

<Accordion.Item value="alpha" class="accordion-item">
    <Accordion.Content class="accordion-content">
        <div class="alpha-control">
            <div class="alpha-display">
                <span class="alpha-value">α={alpha}</span>
            </div>
            
            <div class="slider-container">
                <input 
                    type="range"
                    min="0"
                    max={alphas.length - 1}
                    value={alphaIndex}
                    oninput={(e) => alphaIndex = parseInt(e.target.value)}
                    class="alpha-slider"
                />
                
                <div class="slider-labels">
                    <span>0</span>
                    <span>∞</span>
                </div>
            </div>
        </div>
    </Accordion.Content>
</Accordion.Item>

<style>
    .alpha-control {
        display: flex;
        flex-direction: column;
        gap: 1rem;
    }

    .alpha-display {
        text-align: center;
        padding: 1rem;
        background-color: var(--bg-secondary);
        border-radius: var(--radius);
        border: 1px solid var(--border-color);
    }

    .alpha-value {
        font-size: 1.75rem;
        font-family: monospace;
        font-weight: 600;
        color: var(--text-primary);
    }

    .slider-container {
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
    }

    .alpha-slider {
        width: 100%;
        height: 6px;
        background-color: var(--border-color);
        border-radius: 3px;
        outline: none;
        cursor: pointer;
        -webkit-appearance: none;
        appearance: none;
    }

    .alpha-slider::-webkit-slider-thumb {
        -webkit-appearance: none;
        appearance: none;
        width: 18px;
        height: 18px;
        background: var(--accent-color);
        border-radius: 50%;
        cursor: pointer;
    }

    .alpha-slider::-moz-range-thumb {
        width: 18px;
        height: 18px;
        background: var(--accent-color);
        border-radius: 50%;
        cursor: pointer;
        border: none;
    }

    .slider-labels {
        display: flex;
        justify-content: space-between;
        font-size: 0.75rem;
        color: var(--text-muted);
    }
</style>