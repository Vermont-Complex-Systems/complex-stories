<script>
    import Markdown from 'svelte-exmarkdown';
    import { gfmPlugin } from 'svelte-exmarkdown/gfm';
    import 'katex/dist/katex.min.css';
    import rehypeKatex from 'rehype-katex';
    import remarkMath from 'remark-math';
    import rehypeRaw from 'rehype-raw';
    import rehypeHighlight from 'rehype-highlight';
    import 'highlight.js/styles/github.css';
    import { base } from '$app/paths';
    
    // Import specific languages like in their docs
    import javascript from 'highlight.js/lib/languages/javascript';
    import typescript from 'highlight.js/lib/languages/typescript';
    import css from 'highlight.js/lib/languages/css';
    import xml from 'highlight.js/lib/languages/xml';

    let { text } = $props();

    const plugins = [
        gfmPlugin(),
        { 
            remarkPlugin: [remarkMath], 
            rehypePlugin: [rehypeKatex]
        },
        { 
            rehypePlugin: [rehypeRaw]
        },
        {
            rehypePlugin: [
                rehypeHighlight, 
                { 
                    ignoreMissing: true, 
                    languages: { 
                        javascript,
                        js: javascript,
                        typescript,
                        ts: typescript,
                        css,
                        html: xml,
                        xml,
                        svelte: xml
                    }
                }
            ]
        }
    ];

    function processContent(content) {
        if (!content) {
            return "";
        }

        content = content.replace(/\[\^(\d+)\]/g, '');
        
        // Split content by code blocks and process non-code parts
        const parts = content.split(/(```[\s\S]*?```)/);
        const processed = parts.map((part, index) => {
            // Even indices are non-code content, odd indices are code blocks
            if (index % 2 === 0) {
                // Remove leading whitespace only from non-code content
                return part.replace(/^[ \t]+/gm, '');
            }
            return part; // Preserve code blocks as-is
        });
        content = processed.join('');
        
        content = content.replace(/(src|href)="\/([^"]*?)"/g, `$1="${base}/$2"`);

        return content;
    }
</script>

<Markdown md={processContent(text)} {plugins} />