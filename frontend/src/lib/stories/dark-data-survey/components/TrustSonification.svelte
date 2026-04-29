<script>
    import * as Tone from 'tone';
    import { onDestroy, onMount } from 'svelte';
    import softPianoUrl from '../data/sounds/soft-piano.wav';

    // Tempo bounds when all groups are playing together.
    const ALL_MIN_TEMPO_BPM = 2;
    const ALL_MAX_TEMPO_BPM = 30;
    // Tempo bounds when the highlight feature isolates a single group.
    const HIGHLIGHT_MIN_TEMPO_BPM = 10;
    const HIGHLIGHT_MAX_TEMPO_BPM = 120;
    // true  → higher trust value = faster tempo
    // false → higher trust value = slower tempo
    const HIGH_VALUE_IS_FAST = true;
    // Expected data range for tempo mapping — values outside this range are clamped by the linear scale.
    const DATA_VALUE_MIN = 2;
    const DATA_VALUE_MAX = 6;

    // Component inputs: raw trust rows and the currently highlighted Trust_Category (e.g. "TP_Platform").
    // When highlightCircle is set, only the corresponding group plays.
    let { data = [], highlightCircle = '', highlightedValue = null } = $props();

    // Runtime flags/registries for audio session management.
    let isReady = $state(false);
    let playerRegistry = new Map();
    let masterLimiter = null;
    let pointerListenerAttached = false;
    let audioEnabled = $state(false);
    let lastSignature = $state('');

    // Plain JS ref read by every loop callback. Updated by the highlight $effect.
    // activeGroup: null means all groups play; a group name isolates to that group.
    // activeNote: when set, overrides the group's default note with the specific institution's note.
    const highlightRef = { activeGroup: null, activeNote: null };

    // Maps survey trust categories to broader musical groups.
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
        intimate: 'C3',
        professional: 'D3',
        'semi-institutional': 'Eb3',
        sensitive: 'G4',
        commercial: 'A4',
        unknown: 'B4'
    };

    // Per-institution notes used when a specific ring is highlighted.
    // Institutions within the same group (e.g. TP_Platform/TP_Police/TP_Medical → "sensitive")
    // would otherwise all play the same group note — this gives each its own pitch.
    const institutionNoteMap = {
        'TP_Friend':          'C3',
        'TP_Relative':        'D3',
        'TP_Neighbor':        'E3',
        'TP_Acquaintance':    'F3',
        'TP_Co_worker':       'G3',
        'TP_School':          'A3',
        'TP_Employer':        'B3',
        'TP_Researcher':      'C4',
        'TP_NonProf':         'D4',
        'TP_Platform':        'E4',
        'TP_Gov':             'F4',
        'TP_Police':          'G4',
        'TP_Financial':       'A4',
        'TP_Medical':         'B4',
        'TP_Company_cust':    'C5',
        'TP_Company_notcust': 'D5',
        'TP_Stranger':        'E5'
    };

    const groupVolumeMap = {
        intimate: -18,
        professional: -20,
        'semi-institutional': -22,
        sensitive: -24,
        commercial: -21,
        unknown: -26
    };

    // Aggregate raw rows into a per-group average trust value.
    const groupByCategory = (rows) => {
        const totals = new Map();
        const counts = new Map();

        for (const row of rows || []) {
            const rawCategory = row?.Trust_Category;
            const value = Number(row?.Average_Trust);
            if (!rawCategory || Number.isNaN(value)) continue;

            // Convert granular category into our broader sonification bucket.
            const category = institutionGroupMap[rawCategory] || rawCategory;

            // console.log(`Processing row with category "${rawCategory}" mapped to "${category}" and value ${value}`);

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

    // Linearly map a trust value to a tempo. Direction controlled by HIGH_VALUE_IS_FAST.
    const tempoFromValue = (value, dataMin, dataMax, tempoMin, tempoMax) => {
        if (dataMax <= dataMin) return tempoMin;
        const normalized = (value - dataMin) / (dataMax - dataMin);
        return HIGH_VALUE_IS_FAST
            ? tempoMin + normalized * (tempoMax - tempoMin)
            : tempoMax - normalized * (tempoMax - tempoMin);
    };

    // Defensive teardown helper for a category player.
    const stopAndDispose = (entry) => {
        try {
            entry.loop.stop();
        } catch {
            // Ignore if already stopped.
        }
        entry.loop.dispose();
        entry.synth.dispose();
    };

    // Loops are only started when audio has been explicitly enabled.
    const ensureLoopStarted = (loop) => {
        if (audioEnabled && loop.state !== 'started') {
            loop.start(0);
        }
    };

    // Reconcile existing synth/loop players with latest grouped assignments.
    const syncPlayers = (assignments) => {
        // Remove players for categories no longer present in the data.
        const activeCategories = new Set(assignments.map((entry) => entry.category));
        for (const [category, entry] of playerRegistry.entries()) {
            if (!activeCategories.has(category)) {
                stopAndDispose(entry);
                playerRegistry.delete(category);
            }
        }

        if (!assignments.length) return;

        for (const entry of assignments) {
            // Lazily create a synth + loop for each category the first time it appears.
            const existing = playerRegistry.get(entry.category);
            if (!existing) {
                if (!masterLimiter) {
                    masterLimiter = new Tone.Limiter(-3).toDestination();
                }

                const synth = new Tone.Sampler({
                    urls: { C4: softPianoUrl }
                }).connect(masterLimiter);

                const noteRef = { value: 'C4' };
                const volumeRef = { value: -12 };
                const groupCategory = entry.category;

                const loop = new Tone.Loop((time) => {
                    const active = highlightRef.activeGroup;
                    if (active !== null && active !== groupCategory) return;
                    synth.volume.value = volumeRef.value;
                    synth.triggerAttack(highlightRef.activeNote ?? noteRef.value, time);
                }, 1);

                playerRegistry.set(entry.category, { synth, loop, noteRef, volumeRef });
                ensureLoopStarted(loop);
            }

            const registryEntry = playerRegistry.get(entry.category);
            if (!registryEntry) continue;

            // Keep timbre fixed by group, but vary tempo from trust strength.
            const bpm = tempoFromValue(entry.average, DATA_VALUE_MIN, DATA_VALUE_MAX, ALL_MIN_TEMPO_BPM, ALL_MAX_TEMPO_BPM);
            const intervalSeconds = 60 / bpm;
            registryEntry.loop.interval = intervalSeconds;
            registryEntry.noteRef.value = groupNoteMap[entry.category] || 'C4';
            registryEntry.volumeRef.value = groupVolumeMap[entry.category] ?? -12;
        }
    };

    // Initialize/resume WebAudio and start all loops.
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

    // Pause transport and silence output without disposing players.
    const stopAudio = async () => {
        audioEnabled = false;
        Tone.Destination.mute = true;
        Tone.Transport.pause();
    };

    // UI handler for enable/disable button.
    const toggleAudio = async () => {
        if (audioEnabled) {
            await stopAudio();
        } else {
            await startAudio();
        }
    };

    // Browsers require a user gesture before audio can start; attach one-time listeners.
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

    // Reactively recompute category assignments whenever `data` changes.
    $effect(() => {
        const grouped = groupByCategory(data);
        const assignments = grouped;
        syncPlayers(assignments);

        // Signature lets us detect meaningful data changes and re-phase loops.
        const signature = assignments
            .map((entry) => `${entry.category}:${entry.average.toFixed(3)}`)
            .join('|');

        if (signature && signature !== lastSignature) {
            lastSignature = signature;
            if (audioEnabled) {
                // Restart loops together so updates sound synchronized.
                for (const entry of playerRegistry.values()) {
                    entry.loop.stop();
                    entry.loop.start(0);
                }
            }
        }
    });

    // Keep highlightRef in sync with the prop. All loop callbacks read highlightRef.activeGroup
    // at fire time, so this takes effect on the next trigger of each loop.
    $effect(() => {
        highlightRef.activeGroup = highlightCircle ? institutionGroupMap[highlightCircle] : null;
        highlightRef.activeNote  = highlightCircle ? (institutionNoteMap[highlightCircle] ?? null) : null;

        // When a specific institution is highlighted, drive its loop tempo from the
        // live trust value (1–7 Likert scale) rather than the group average.
        if (highlightedValue !== null && highlightRef.activeGroup) {
            const bpm = tempoFromValue(highlightedValue, DATA_VALUE_MIN, DATA_VALUE_MAX, HIGHLIGHT_MIN_TEMPO_BPM, HIGHLIGHT_MAX_TEMPO_BPM);
            const player = playerRegistry.get(highlightRef.activeGroup);
            if (player) player.loop.interval = 60 / bpm;
        }
    });

    // Full cleanup on component teardown.
    onDestroy(() => {
        for (const entry of playerRegistry.values()) {
            stopAndDispose(entry);
        }
        playerRegistry.clear();
        masterLimiter?.dispose();
        masterLimiter = null;
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
