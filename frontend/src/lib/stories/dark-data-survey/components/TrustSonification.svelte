<script>
    import * as Tone from 'tone';
    import { onDestroy, onMount } from 'svelte';

    let {
        data = [],
        minTempoBpm = 5,
        maxTempoBpm = 120
    } = $props();

    let isReady = $state(false);
    let playerRegistry = new Map();
    let pointerListenerAttached = false;
    let audioEnabled = $state(false);
    let lastSignature = $state('');

    const institutionGroupMap = {
        // Green: Intimate/close relationships
        'TP_Friend': 'intimate',
        'TP_Relative': 'intimate',
        'TP_Neighbor': 'intimate',
        'TP_Acquaintance': 'intimate',

        // Blue: Professional peers
        'TP_Co_worker': 'professional',

        // Purple: Semi-institutional (Educational, Employer, Researcher, Non-Profits)
        'TP_School': 'semi-institutional',
        'TP_Employer': 'semi-institutional',
        'TP_Researcher': 'semi-institutional',
        'TP_NonProf': 'semi-institutional',

        // Orange/Red: Institutions handling sensitive data
        'TP_Platform': 'sensitive',
        'TP_Gov': 'sensitive',
        'TP_Police': 'sensitive',
        'TP_Financial': 'sensitive',
        'TP_Medical': 'sensitive',

        // Amber: Commercial entities
        'TP_Company_cust': 'commercial',
        'TP_Company_notcust': 'commercial',

        // Gray: Strangers/unknown
        'TP_Stranger': 'unknown'
    };

    const groupNoteMap = {
        intimate: 'C4',
        professional: 'D4',
        'semi-institutional': 'E4',
        sensitive: 'G4',
        commercial: 'A4',
        unknown: 'B4'
    };

    const groupVolumeMap = {
        intimate: -10,
        professional: -12,
        'semi-institutional': -14,
        sensitive: -16,
        commercial: -13,
        unknown: -18
    };

    const groupByCategory = (rows) => {
        const totals = new Map();
        const counts = new Map();

        for (const row of rows || []) {
            const rawCategory = row?.Trust_Category;
            const value = Number(row?.Average_Trust);
            if (!rawCategory || Number.isNaN(value)) continue;

            const category = institutionGroupMap[rawCategory] || rawCategory;

            console.log(`Processing row with category "${rawCategory}" mapped to "${category}" and value ${value}`);

            totals.set(category, (totals.get(category) || 0) + value);
            counts.set(category, (counts.get(category) || 0) + 1);
        }

        const grouped = [];
        for (const [category, total] of totals.entries()) {
            const count = counts.get(category) || 1;
            grouped.push({ category, average: total / count });
        }

        grouped.sort((a, b) => a.category.localeCompare(b.category));
        return grouped;
    };

    const tempoFromValue = (value, minValue, maxValue) => {
        if (maxValue <= minValue) return minTempoBpm;
        const normalized = (value - minValue) / (maxValue - minValue);
        return minTempoBpm + normalized * (maxTempoBpm - minTempoBpm);
    };

    const stopAndDispose = (entry) => {
        try {
            entry.loop.stop();
        } catch {
            // Ignore if already stopped.
        }
        entry.loop.dispose();
        entry.synth.dispose();
    };

    const ensureLoopStarted = (loop) => {
        if (audioEnabled && loop.state !== 'started') {
            loop.start(0);
        }
    };

    const syncPlayers = (assignments) => {
        const activeCategories = new Set(assignments.map((entry) => entry.category));
        for (const [category, entry] of playerRegistry.entries()) {
            if (!activeCategories.has(category)) {
                stopAndDispose(entry);
                playerRegistry.delete(category);
            }
        }

        if (!assignments.length) return;

        const values = assignments.map((entry) => entry.average);
        const minValue = Math.min(...values);
        const maxValue = Math.max(...values);

        for (const entry of assignments) {
            const existing = playerRegistry.get(entry.category);
            if (!existing) {
                if (existing) {
                    stopAndDispose(existing);
                }

                const synth = new Tone.MonoSynth({
                    oscillator: { type: 'sine' },
                    envelope: {
                        attack: 0.01,
                        decay: 0.1,
                        sustain: 0.2,
                        release: 0.2
                    }
                }).toDestination();

                const noteRef = { value: 'C4' };
                const volumeRef = { value: -12 };

                const loop = new Tone.Loop((time) => {
                    synth.volume.value = volumeRef.value;
                    synth.triggerAttackRelease(noteRef.value, '8n', time);
                }, 1);

                playerRegistry.set(entry.category, { synth, loop, noteRef, volumeRef });
                ensureLoopStarted(loop);
            }

            const registryEntry = playerRegistry.get(entry.category);
            if (!registryEntry) continue;

            const bpm = tempoFromValue(entry.average, minValue, maxValue);
            const intervalSeconds = 60 / bpm;
            registryEntry.loop.interval = intervalSeconds;
            registryEntry.noteRef.value = groupNoteMap[entry.category] || 'C4';
            registryEntry.volumeRef.value = groupVolumeMap[entry.category] ?? -12;
        }
    };

    const startAudio = async () => {
        if (!isReady) {
            await Tone.start();
            await Tone.loaded();
            isReady = true;
        } else {
            await Tone.getContext().resume();
        }

        audioEnabled = true;
        Tone.Destination.mute = false;
        Tone.Transport.start();

        for (const entry of playerRegistry.values()) {
            ensureLoopStarted(entry.loop);
        }
    };

    const stopAudio = async () => {
        audioEnabled = false;
        Tone.Destination.mute = true;
        Tone.Transport.pause();
    };

    const toggleAudio = async () => {
        if (audioEnabled) {
            await stopAudio();
        } else {
            await startAudio();
        }
    };

    const attachPointerListener = () => {
        if (pointerListenerAttached || typeof window === 'undefined') return;

        pointerListenerAttached = true;
        const onFirstPointer = () => startAudio();
        const options = { once: true, passive: true };

        window.addEventListener('pointerdown', onFirstPointer, options);
        window.addEventListener('touchstart', onFirstPointer, options);
        window.addEventListener('keydown', onFirstPointer, options);

        onDestroy(() => {
            window.removeEventListener('pointerdown', onFirstPointer, options);
            window.removeEventListener('touchstart', onFirstPointer, options);
            window.removeEventListener('keydown', onFirstPointer, options);
        });
    };

    onMount(() => {
        attachPointerListener();
    });

    $effect(() => {
        const grouped = groupByCategory(data);
        const assignments = grouped;
        syncPlayers(assignments);

        const signature = assignments
            .map((entry) => `${entry.category}:${entry.average.toFixed(3)}`)
            .join('|');

        if (signature && signature !== lastSignature) {
            lastSignature = signature;
            if (audioEnabled) {
                for (const entry of playerRegistry.values()) {
                    entry.loop.stop();
                    entry.loop.start(0);
                }
            }
        }
    });

    onDestroy(() => {
        for (const entry of playerRegistry.values()) {
            stopAndDispose(entry);
        }
        playerRegistry.clear();
    });
</script>

<div class="sonification">
    <button
        class="enable-audio"
        type="button"
        on:click={toggleAudio}
        aria-pressed={audioEnabled}
    >
        {audioEnabled ? 'Disable audio' : 'Enable audio'}
    </button>
</div>

<style>
    .sonification {
        position: fixed;
        top: 1rem;
        right: 1rem;
        z-index: 2000;
        pointer-events: auto;
    }

    .enable-audio {
        background: #1d1f26;
        color: #f7f3ea;
        border: 1px solid #3c3f4c;
        border-radius: 999px;
        padding: 0.5rem 0.9rem;
        font-size: 0.85rem;
        letter-spacing: 0.02em;
        cursor: pointer;
    }

    .enable-audio[disabled] {
        opacity: 0.6;
        cursor: default;
    }
</style>
