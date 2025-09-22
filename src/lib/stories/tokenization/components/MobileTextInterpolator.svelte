<script>
// Helper: highlight nouns and verbs
const sentence = "the quick brown fox jumped over the lazy dog";
const words = sentence.split(" ");
// For this sentence, nouns: fox, dog; verbs: jumped
const nounSet = new Set(["fox", "dog"]);
const verbSet = new Set(["jumped"]);
export let progress = 0; // 0=start, 1=end
export let currentStep = 0; // current step index


</script>

<div class="centered-text">
        {#if currentStep === 1}
            <p>
                <span style="font-size: 16px"><span class="circle"></span>noun</span>
                <span style="font-size: 16px"><span class="circle" style="background-color: red"></span>verb</span><br>
                {#each words as word, i}
                    {#if nounSet.has(word)}
                        <span style="color: #2979ff; font-weight: bold">{word}</span>
                    {:else if verbSet.has(word)}
                        <span style="color: red; font-weight: bold">{word}</span>
                    {:else}
                        {word}
                    {/if}
                    {i < words.length - 1 ? ' ' : ''}
                {/each}
            </p>
        {:else if currentStep >= 2}
            <p class="technicolor">
            <span style="font-size: 0.9rem; border: 1px solid #333; padding: 2px 6px; border-radius: 4px; margin-right: 8px; display: inline-block;">
                token
            </span><br>
            {#each words as word, i}
                <span style="color: #000; border: 2px solid #000; padding: 2px 6px; border-radius: 4px; margin-right: 2px; display: inline-block;">
                {word}
                </span>{i < words.length - 1 ? ' ' : ''}
            {/each}
            </p>
        {:else}
            <p>{sentence}</p>
        {/if}
</div>

<style>
    
    .circle {
        display: inline-block;
        width: 12px;
        height: 12px;
        background-color: #2979ff;
        border-radius: 50%;
        margin-right: 6px;
        position: relative;
        top: 2px;
    }
    .centered-text {
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        height: 100vh;
    }
    .centered-text p {
        font-size: 1.5rem;
        text-align: center;
        margin: 0;
    }
</style>