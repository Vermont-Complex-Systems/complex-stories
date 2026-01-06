<script>
    let { onAccept, userFingerprint, saveAnswer } = $props();

    let showPopup = $state(true);

    async function handleAccept() {
        showPopup = false;
        // Parent component (Index.svelte) will handle fingerprint generation and consent saving
        await onAccept();
    }

    function handleDecline() {
        showPopup = false;
        // No tracking if user declines - fingerprint is never generated
    }
</script>

{#if showPopup}
<div class="popup-overlay" onclick={handleDecline}>
    <div class="popup-content" onclick={(e) => e.stopPropagation()}>
        <div class="popup-body">
            <p>This is an interactive data essay on privacy preferences and data sharing behaviors.</p>
            <p>As part of the story, we ask a few anonymous questions about privacy preferences and demographics to inform the interactive story, and, conditional on consent, inform our ongoing research on the topic.</p>
        </div>

        <div class="popup-actions">
            <button class="btn-decline" onclick={handleDecline}>Decline</button>
            <button class="btn-accept" onclick={handleAccept}>I Consent</button>
        </div>
    </div>
</div>
{/if}

<style>
    .popup-overlay {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0, 0, 0, 0.8);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 10000;
        padding: 1rem;
    }

    .popup-content {
        background: #1a1a1a;
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 12px;
        max-width: 400px;
        width: 100%;
        max-height: 90vh;
        overflow-y: auto;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5);
    }

    h2 {
        margin: 0;
        padding: 1.5rem;
        font-size: 1.5rem;
        font-weight: 600;
        color: whitesmoke;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    }

    .popup-body {
        padding: 1.5rem;
        color: rgba(255, 255, 255, 0.9);
        line-height: 1.6;
    }

    .popup-body p {
        margin: 0 0 1rem 0;
    }

    .popup-body ul {
        margin: 0.5rem 0 1rem 1.5rem;
        padding: 0;
    }

    .popup-body li {
        margin: 0.25rem 0;
    }

    .popup-body strong {
        color: whitesmoke;
    }

    .popup-actions {
        padding: 1rem 1.5rem 1.5rem;
        display: flex;
        gap: 1rem;
        justify-content: flex-end;
        border-top: 1px solid rgba(255, 255, 255, 0.1);
    }

    button {
        padding: 0.75rem 1.5rem;
        border-radius: 6px;
        font-size: 1rem;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.2s ease;
        border: none;
    }

    .btn-decline {
        background: rgba(255, 255, 255, 0.1);
        color: rgba(255, 255, 255, 0.7);
    }

    .btn-decline:hover {
        background: rgba(255, 255, 255, 0.15);
        color: whitesmoke;
    }

    .btn-accept {
        background: #0891b2;
        color: white;
    }

    .btn-accept:hover {
        background: #0e7490;
    }

    @media (max-width: 640px) {
        .popup-content {
            max-height: 95vh;
        }

        h2 {
            font-size: 1.25rem;
            padding: 1rem;
        }

        .popup-body {
            padding: 1rem;
            font-size: 0.9rem;
        }

        .popup-actions {
            flex-direction: column-reverse;
        }

        button {
            width: 100%;
        }
    }
</style>
