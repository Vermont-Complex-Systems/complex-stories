<script>
    import Markdown from 'svelte-exmarkdown';
    import 'katex/dist/katex.min.css';
    import rehypeKatex from 'rehype-katex';
    import remarkMath from 'remark-math';
    import rehypeRaw from 'rehype-raw';
    import { base } from '$app/paths';

    let { text } = $props();

    const plugins = [
        { 
            remarkPlugin: [remarkMath], 
            rehypePlugin: [rehypeKatex]
        },
        { 
            rehypePlugin: [rehypeRaw]
        }
    ];

    function processContent(content) {
        if (!content) {
            return "";
        }

        // Remove reference markers like [^1]
        content = content.replace(/\[\^(\d+)\]/g, '');

        // Remove leading whitespace at the beginning of each line
        content = content.replace(/^[ \t]+/gm, '');

        // Add base path to relative URLs that start with /
        // Only for src and href attributes
        content = content.replace(/(src|href)="\/([^"]*?)"/g, `$1="${base}/$2"`);

        return content;
    }
</script>

<Markdown md={processContent(text)} {plugins} />