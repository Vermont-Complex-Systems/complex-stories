<!-- InsightBox.svelte -->
<script>
    import { Info, AlertTriangle, Flame, Megaphone, Lightbulb } from '@lucide/svelte';
    
    let { type = 'note', children } = $props();
    
    const icons = {
        note: Info,
        warning: AlertTriangle,
        tip: Lightbulb,
        important: Megaphone,
        caution: Flame
    };
    
    const colors = {
        note: '#3b82f6',
        warning: '#f59e0b',
        tip: '#10b981',
        important: '#8b5cf6',
        caution: '#ef4444'
    };
    
    const IconComponent = $derived(icons[type]);
    const iconColor = $derived(colors[type]);
</script>

<div class="insight-box {type}">
    <div class="icon-wrapper">
        <IconComponent size={16} color={iconColor} />
    </div>
    <p>{@render children()}</p>
</div>

<style>
    
  .insight-box {
        background-color: #dbeafe;
        border: 1px solid #3b82f6;
        border-radius: 6px;
        padding: 16px;
        margin: 16px 0;
        display: flex;
        gap: 8px;
        margin-bottom: 2rem;
    }

    .icon-wrapper {
        display: flex;
        align-items: center;
        height: 21px; /* Match the line-height of your text (14px * 1.5) */
        flex-shrink: 0;
    }

    .insight-box p {
        margin: 0;
        color: #1e40af;
        font-size: 14px;
        line-height: 1.5;
        flex: 1;
    }
    
    .insight-icon {
        flex-shrink: 0;
        margin-top: 2px; /* Align with text baseline */
    }


    /* Style images within the insight box */
    .insight-box :global(img) {
        max-width: 100%;
        height: auto;
        border-radius: 4px;
        margin-top: 12px;
        display: block;
        border: 1px solid #ccc;
        box-shadow: 5px 5px 10px rgba(0, 0, 0, 0.2);
    }

    /* Variants */
    .insight-box.warning {
        background-color: #fef3c7;
        border-color: #f59e0b;
    }

    .insight-box.warning p {
        color: #92400e;
    }

    .insight-box.caution {
        background-color: #fee2e2;
        border-color: #ef4444;
    }

    .insight-box.caution p {
        color: #dc2626;
    }

    .insight-box.important {
        background-color: #f3e8ff;
        border-color: #8b5cf6;
    }

    .insight-box.important p {
        color: #7c3aed;
    }

    .insight-box.tip {
        background-color: 	#ECFFDC;
        border-color: #355E3B;
    }

    .insight-box.tip p {
        color: #355E3B;
    }
</style>