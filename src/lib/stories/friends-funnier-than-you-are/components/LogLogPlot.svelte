<script>
    import { Plot, Dot, Line, RuleY, RuleX, Text } from 'svelteplot';
    import cascadeData from '../data/cascadeDistributions.json';
    import InsetPlot from './LogLogPlot.Inset.svelte'
    // Critical point
    const pc = 0.0286;
    
    // Split p-values by regime
    let allPValues = Object.values(cascadeData.datasets)
        .map(d => d.metadata.p)
        .sort((a, b) => a - b);
    
    let subcriticalPValues = allPValues.filter(p => p < pc);
    let supercriticalPValues = allPValues.filter(p => p >= pc);
    
    // Slider state
    let subcriticalIndex = $state(Math.floor(subcriticalPValues.length * 0.6));
    let supercriticalIndex = $state(Math.floor(supercriticalPValues.length * 0.3));
    
    // Current p-values
    let p1 = $derived(subcriticalPValues[subcriticalIndex]);
    let p2 = $derived(supercriticalPValues[supercriticalIndex]);
    let dataset1Key = $derived(`l3_p${p1}`);
    let dataset2Key = $derived(`l3_p${p2}`);
    
    const tauData = [
        { p: 0.001, tau: 4.2 }, { p: 0.002, tau: 4.0 }, { p: 0.003, tau: 3.8 },
        { p: 0.005, tau: 3.6 }, { p: 0.0075, tau: 3.4 }, { p: 0.01, tau: 3.5 },
        { p: 0.0125, tau: 3.2 }, { p: 0.015, tau: 3.0 }, { p: 0.0175, tau: 2.8 },
        { p: 0.02, tau: 2.7 }, { p: 0.025, tau: 2.4 }, { p: 0.02859548, tau: 2.0 },
        { p: 0.032, tau: 1.9 }, { p: 0.035, tau: 1.9 }, { p: 0.04, tau: 1.9 },
        { p: 0.045, tau: 1.9 }, { p: 0.05, tau: 1.9 }, { p: 0.06, tau: 1.9 },
        { p: 0.07, tau: 1.9 }, { p: 0.08, tau: 1.9 }, { p: 0.09, tau: 1.9 }
    ];

    // τ lookup from Figure 1b
    function getTauFromP(p) {
        
        const exact = tauData.find(d => Math.abs(d.p - p) < 0.0001);
        if (exact) return exact.tau;
        
        for (let i = 0; i < tauData.length - 1; i++) {
            if (p >= tauData[i].p && p <= tauData[i + 1].p) {
                const t = (p - tauData[i].p) / (tauData[i + 1].p - tauData[i].p);
                return tauData[i].tau + t * (tauData[i + 1].tau - tauData[i].tau);
            }
        }
        return p < pc ? 3.0 : 1.9;
    }
    
    let tau1 = $derived(getTauFromP(p1));
    let tau2 = $derived(getTauFromP(p2));
    
    // Data processing with subsampling
    function getData(datasetKey) {
        const dataset = cascadeData.datasets[datasetKey];
        const fullData = dataset.data
            .slice(0, 10000)
            .map((value, index) => ({ value, index }))
            .filter(d => d.value > 1e-10 && d.value < 1e5);
        
        const sampledData = [];
        for (let i = 0; i < fullData.length; i++) {
            const s = i + 1;
            if (s < 50) {
                sampledData.push(fullData[i]);
            } else if (s < 500) {
                if (i % 3 === 0) sampledData.push(fullData[i]);
            } else {
                if (i % 5 === 0) sampledData.push(fullData[i]);
            }
        }
        return sampledData;
    }
    
    let data1 = $derived(getData(dataset1Key));
    let data2 = $derived(getData(dataset2Key));
    
    // Power law with adaptive range based on data
    function createPowerLaw(data, tau) {
        if (data.length === 0) return [];
        
        const refPoint = data.find(d => (d.index + 1) >= 20) || data[Math.floor(data.length/3)];
        const refS = refPoint.index + 1;
        const refY = refPoint.value;
        const A = refY * Math.pow(refS, tau);
        
        const startS = 3;
        const maxDataS = Math.max(...data.map(d => d.index + 1));
        const endS = Math.min(maxDataS * 1.5, 10000);
        
        const points = [];
        for (let i = 0; i < 50; i++) {
            const s = startS * Math.pow(endS / startS, i / 49);
            const y = A * Math.pow(s, -tau);
            points.push({ s, y });
        }
        
        return points;
    }
    
    let powerLaw1 = $derived(createPowerLaw(data1, tau1));
    let powerLaw2 = $derived(createPowerLaw(data2, tau2));
    
    function formatTicks(d) {
        const exp = Math.round(Math.log10(d));
        return `10^${exp}`;
    }
</script>

<div class="container">
    <div class="controls">
        <div class="slider-container">
            <label>Subcritical: p = {p1} (τ = {tau1.toFixed(1)})</label>
            <input 
                type="range" 
                bind:value={subcriticalIndex}
                min="0" 
                max={subcriticalPValues.length - 1}
                class="slider blue"
            />
        </div>
        
        <div class="slider-container">
            <label>Supercritical: p = {p2} (τ = {tau2.toFixed(1)})</label>
            <input 
                type="range" 
                bind:value={supercriticalIndex}
                min="0" 
                max={supercriticalPValues.length - 1}
                class="slider orange"
            />
        </div>
    </div>

    <div class="plot-wrapper">
        <div class="inset-loglog">
            <InsetPlot data={tauData} {p1} {p2}/>
        </div>

    <Plot 
        x={{
            type: 'log',
            tickFormat: formatTicks,
            label: "Cascade size s →"
        }} 
        y={{
            type: 'log',
            tickFormat: formatTicks,
            label: "↑ Fraction of cascades"
        }} 
        grid 
        frame
        marginLeft={60}
        marginRight={40}
    >
        <Dot
            data={data1}
            x={(d) => d.index + 1}
            y="value" 
            fill={`Subcritical p=${p1}`}
            symbol="triangle"
            r={2}
        />
        <Dot
            data={data2}
            x={(d) => d.index + 1}
            y="value" 
            fill={`Supercritical p=${p2}`}
            symbol="circle"
            r={2}
        />
        
        <Line
            data={powerLaw1}
            x="s"
            y="y"
            stroke="grey"
            strokeWidth={4}
            strokeDasharray="3,3"
        />
        <Line
            data={powerLaw2}
            x="s"
            y="y"
            stroke="grey"
            strokeWidth={4}
        />
    </Plot>
    </div>
</div>

<style>
    .container {
        width: 100%;
    }
    
    .plot-wrapper {
        position: relative;
    }
    
    .inset-loglog {
        position: absolute;
        top: 30px;
        right: 43px;
        width: 220px;
        height: 170px;
        background: #f8f5e6;
        border: 1px solid #ddd;
        border-radius: 4px;
        padding: 4px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        z-index: 10;
        overflow: hidden;
    }
    
    .inset-loglog :global(svg) {
        width: 100% !important;
        height: 100% !important;
        max-width: none !important;
        max-height: none !important;
    }
    
    .controls {
        justify-content: center;
        align-items: center;
        display: flex;
        gap: 40px;
        align-items: end;
        margin-bottom: 25px;
    }
    
    .slider-container {
        display: flex;
        flex-direction: column;
        gap: 8px;
        min-width: 250px;
        flex-shrink: 0;
    }
    
    .slider-container label {
        font-size: 14px;
        font-weight: 600;
        color: #333;
    }
    
    .slider {
        min-width: 100px;
        max-width: 200px;
        height: 6px;
        border-radius: 5px;
        outline: none;
        cursor: pointer;
    }
    
    .slider.blue {
        background: linear-gradient(to right, #fff3e0, #1976d2);
    }
    
    .slider.orange {
        background: linear-gradient(to right, #fff3e0, #f57c00);
    }
    
    .slider::-webkit-slider-thumb {
        -webkit-appearance: none;
        width: 16px;
        height: 16px;
        border-radius: 50%;
        background: whitesmoke;
        border: 1px solid black;
        cursor: pointer;
    }
    
    .slider::-moz-range-thumb {
        width: 16px;
        height: 16px;
        border-radius: 50%;
        background: whitesmoke;
        border: 1px solid black;
        cursor: pointer;
    }
</style>