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

<div class="markdown-content">
    <Markdown md={processContent(text)} {plugins} />
</div>

<style>
    /* Move all the content styles from blog [slug] page here */
    .markdown-content {
        font-family: "New York", "Times New Roman", Georgia, serif;
        font-size: 1.3rem;
        line-height: 1.5; /* Change from 1.2 to 1.5 - much more readable */
        color: var(--color-fg);
    }

    .markdown-content :global(p) {
        margin: 1.5rem 0;
        font-weight: 400;
        line-height: 1.6; /* Even more generous for paragraphs */
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
    }

    
    .markdown-content :global(li) {
        margin: 0.75rem 0;
        line-height: 1.5; /* Change from 1.2 to 1.5 */
    }

    .markdown-content :global(li) {
        margin: 0.75rem 0;
        line-height: 1.2;
    }

    .markdown-content :global(ol) {
        margin: 1.5rem 0;
        padding-left: 1.5rem;
    }

    /* Blockquotes */
    .markdown-content :global(blockquote) {
        border: none;
        margin: 2rem 0;
        padding: 0 0 0 1.5rem;
        background: none;
        font-size: 1.2em;
        line-height: 1.2;
        color: #2c5aa0;
        border-left: 3px solid #2c5aa0;
    }

    .markdown-content :global(blockquote p) {
        margin: 0;
    }

    /* Code blocks */
    .markdown-content :global(pre) {
        background: var(--color-input-bg);
        border-radius: var(--border-radius);
        padding: 1rem;
        margin: 1.5rem 0;
        overflow-x: auto;
        font-family: var(--mono);
        font-size: 0.7em;
        line-height: 1.4;
        white-space: pre;
    }

    .markdown-content :global(pre code) {
        background: none;
        padding: 0;
        border: none;
        white-space: pre;
        font-family: inherit;
        font-size: inherit;
    }

    /* Inline code */
    .markdown-content :global(p code),
    .markdown-content :global(li code) {
        font-family: var(--mono);
        font-size: 0.75em;
        background: var(--color-input-bg);
        padding: 0.125rem 0.25rem;
        border-radius: 2px;
    }

    /* Dark mode styles */
    :global(.dark) .markdown-content :global(blockquote) {
        color: #4a90e2;
        border-left-color: #4a90e2;
    }

    :global(.dark) .markdown-content :global(pre) {
        background: var(--color-gray-800);
    }

    :global(.dark) .markdown-content :global(p code),
    :global(.dark) .markdown-content :global(li code) {
        background: var(--color-gray-800);
    }

    /* Image grids */
    .markdown-content :global(.image-grid) {
        display: flex;
        gap: 1rem;
        margin: 2rem 0;
    }

    .markdown-content :global(.image-item) {
        flex: 1;
        display: flex;
        flex-direction: column;
    }

    .markdown-content :global(.image-item a) {
        display: block;
        text-decoration: none;
        border-radius: var(--border-radius);
        overflow: hidden;
        margin-bottom: 0.5rem;
        height: 200px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        transition: transform var(--transition-medium), box-shadow var(--transition-medium);
    }

    .markdown-content :global(.image-item a:hover) {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
    }

    .markdown-content :global(.image-grid img) {
        width: 100%;
        height: 100%;
        object-fit: cover;
        border-radius: 0;
        box-shadow: none;
        display: block;
    }

    .markdown-content :global(.image-caption) {
        font-family: var(--sans);
        font-size: var(--font-size-small);
        color: var(--color-secondary-gray);
        text-align: center;
        margin: 0;
        padding: 0 0.5rem;
        line-height: 1.3;
        font-weight: 500;
    }

    /* Mobile styles */
    @media (max-width: 768px) {
        .markdown-content :global(.image-grid) {
            flex-direction: column;
            align-items: center;
        }
        
        .markdown-content :global(.image-item) {
            max-width: 90%;
        }
        
        .markdown-content :global(.image-grid img) {
            height: 250px;
        }
    }
</style>