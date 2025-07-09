<!-- ScrollyMarkdown.svelte -->
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
    
    import javascript from 'highlight.js/lib/languages/javascript';
    import typescript from 'highlight.js/lib/languages/typescript';
    import css from 'highlight.js/lib/languages/css';
    import xml from 'highlight.js/lib/languages/xml';

    let { text, isGirls = true } = $props();

    // Name mappings
    const nameMappings = {
        girls: {
            topName2023: 'Alice',
            secondName2023: 'Florence',
            surpriseName: 'Charlie',
            topName1980: 'Julie',
            lastName1980: 'Ysabelle',
            secondLastName1990: 'Xiomara',
        },
        boys: {
            topName2023: 'Eric',
            secondName2023: 'Jonathan',
            surpriseName: 'Noah',
            topName1980: 'Noah',
            lastName1980: 'JEFFERY',
            secondLastName1990: 'Tomasz'

        }
    };

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

        // Your existing processing...
        content = content.replace(/\[\^(\d+)\]/g, '');
        
        const parts = content.split(/(```[\s\S]*?```)/);
        const processed = parts.map((part, index) => {
            if (index % 2 === 0) {
                return part.replace(/^[ \t]+/gm, '');
            }
            return part;
        });
        content = processed.join('');
        
        content = content.replace(/(src|href)="\/([^"]*?)"/g, `$1="${base}/$2"`);

        // Replace name placeholders
        const currentNames = isGirls ? nameMappings.girls : nameMappings.boys;
        Object.entries(currentNames).forEach(([placeholder, name]) => {
            const regex = new RegExp(`\\{\\{${placeholder}\\}\\}`, 'g');
            content = content.replace(regex, name);
        });

        return content;
    }
</script>

<div class="scrolly-markdown" class:girls-mode={isGirls} class:boys-mode={!isGirls}>
    <Markdown md={processContent(text)} {plugins} />
</div>

<style>
    /* Base scrolly markdown styles */
    .scrolly-markdown {
        font-family: "New York", "Times New Roman", Georgia, serif;
        font-size: 1.1rem;
        line-height: 1.6;
        color: var(--color-fg);
    }

    .scrolly-markdown :global(p) {
        margin: 1.2rem 0;
        font-weight: 400;
        line-height: 1.7;
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
    }

    /* Name highlighting - responds to gender toggle */
    .scrolly-markdown :global(.name-highlight) {
        font-weight: 600;
        padding: 0.1rem 0.3rem;
        border-radius: 0.25rem;
        transition: all 300ms cubic-bezier(0.4, 0, 0.2, 1);
        text-decoration: underline;
        text-decoration-thickness: 2px;
        text-underline-offset: 3px;
    }

    /* Gender-specific name styling */
    .scrolly-markdown.girls-mode :global(.name-highlight) {
        background: rgba(236, 72, 153, 0.1);
        color: #be185d;
        text-decoration-color: #ec4899;
    }

    .scrolly-markdown.boys-mode :global(.name-highlight) {
        background: rgba(59, 130, 246, 0.1);
        color: #1e40af;
        text-decoration-color: #3b82f6;
    }

    /* Year highlighting */
    .scrolly-markdown :global(.year-1980) {
        background: rgb(230, 230, 230);
        color: #374151;
        font-weight: 600;
        padding: 0.15rem 0.4rem;
        border-radius: 0.3rem;
        font-family: var(--mono);
    }

    .scrolly-markdown :global(.year-2023) {
        background: rgb(195, 230, 243);
        color: #0f172a;
        font-weight: 600;
        padding: 0.15rem 0.4rem;
        border-radius: 0.3rem;
        font-family: var(--mono);
    }

    /* Interactive elements */
    .scrolly-markdown :global(.interactive-term) {
        cursor: help;
        border-bottom: 1px dotted currentColor;
        transition: all 200ms ease;
    }

    .scrolly-markdown :global(.interactive-term:hover) {
        background: rgba(59, 130, 246, 0.1);
        border-bottom: 1px solid #3b82f6;
    }

    /* Dark mode */
    :global(.dark) .scrolly-markdown.girls-mode :global(.name-highlight) {
        background: rgba(236, 72, 153, 0.2);
        color: #fbb6ce;
    }

    :global(.dark) .scrolly-markdown.boys-mode :global(.name-highlight) {
        background: rgba(59, 130, 246, 0.2);
        color: #93c5fd;
    }

    /* Dark mode adjustments */
    :global(.dark) .scrolly-markdown.girls-mode :global(.name-highlight) {
        background: rgba(236, 72, 153, 0.2);
        color: #fbb6ce;
    }

    :global(.dark) .scrolly-markdown.boys-mode :global(.name-highlight) {
        background: rgba(59, 130, 246, 0.2);
        color: #93c5fd;
    }

    :global(.dark) .scrolly-markdown :global(.year-1980) {
        background: rgba(230, 230, 230, 0.9);
        color: #1f2937;
    }

    :global(.dark) .scrolly-markdown :global(.year-2023) {
        background: rgba(195, 230, 243, 0.9);
        color: #1f2937;
    }
</style>