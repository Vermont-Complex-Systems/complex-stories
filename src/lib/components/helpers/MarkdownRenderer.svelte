<script>
    // import type { Plugin } from 'svelte-exmarkdown';

    import Markdown from 'svelte-exmarkdown';
    import 'katex/dist/katex.min.css';
	import rehypeKatex from 'rehype-katex';
	import remarkMath from 'remark-math';

    let { text } = $props();

    const plugins = [
		{ remarkPlugin: [remarkMath], rehypePlugin: [rehypeKatex] }
	];

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