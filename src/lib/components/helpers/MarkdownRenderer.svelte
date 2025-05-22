<script>
    import Markdown from 'svelte-exmarkdown';
    import { gfmPlugin } from 'svelte-exmarkdown/gfm';
    
    let { text } = $props();

    const plugins = [gfmPlugin()];

    function processContent(content) {
        if (!content) {
            return ""; // Return empty string if content is undefined or null
        }

        // Remove reference markers like [^1]
        content = content.replace(/\[\^(\d+)\]/g, '');

        // Remove leading whitespace at the beginning of each line
        return content.replace(/^[ \t]+/gm, '');
    }
</script>

<Markdown md={processContent(text)} {plugins} />