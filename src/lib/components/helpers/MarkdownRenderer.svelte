<script>
    import Markdown from 'svelte-exmarkdown';
    import 'katex/dist/katex.min.css';
    import rehypeKatex from 'rehype-katex';
    import remarkMath from 'remark-math';
    import rehypeRaw from 'rehype-raw'; // Add this import

    let { text } = $props();

    const plugins = [
        { 
            remarkPlugin: [remarkMath], 
            rehypePlugin: [rehypeKatex]
        },
        { 
            rehypePlugin: [rehypeRaw] // Add this plugin to enable HTML
        }
    ];

    function processContent(content) {
        if (!content) {
            return "";
        }

        // Remove reference markers like [^1]
        content = content.replace(/\[\^(\d+)\]/g, '');

        // Remove leading whitespace at the beginning of each line
        return content.replace(/^[ \t]+/gm, '');
    }
</script>

<Markdown md={processContent(text)} {plugins} />