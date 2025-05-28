// Utility: parse SVG <text> and <tspan> elements into { id, text, x, y, opacity }, accounting for parent <g> transforms
function getCumulativeTranslate(el) {
    let x = 0, y = 0;
    let node = el.parentNode;
    while (node && node.nodeType === 1 && node.tagName !== 'svg') {
        const transform = node.getAttribute('transform');
        if (transform) {
            const match = /translate\\(([-\\d.]+)[ ,]+([\\-\\d.]+)\\)/.exec(transform);
            if (match) {
                x += parseFloat(match[1]);
                y += parseFloat(match[2]);
            }
        }
        node = node.parentNode;
    }
    return { x, y };
}

export function extractTextElementsFromSVG(svgStringOrNode) {
    let svg;
    if (typeof svgStringOrNode === 'string') {
        const parser = new DOMParser();
        const doc = parser.parseFromString(svgStringOrNode, 'image/svg+xml');
        svg = doc.querySelector('svg');
    } else {
        svg = svgStringOrNode;
    }

    if (!svg) return [];

    const texts = [];
    Array.from(svg.querySelectorAll('text')).forEach((el, i) => {
        const baseId = el.id || `text-${i}`;
        const baseOpacity = el.hasAttribute('opacity') ? parseFloat(el.getAttribute('opacity')) : 1;
        const groupTrans = getCumulativeTranslate(el);

        // If there are tspans, extract each one
        const tspans = el.querySelectorAll('tspan');
        if (tspans.length > 0) {
            tspans.forEach((tspan, j) => {
                const tspanTrans = getCumulativeTranslate(tspan);
                texts.push({
                    id: tspan.id || `${baseId}-tspan-${j}`,
                    text: tspan.textContent,
                    x: parseFloat(tspan.getAttribute('x') || el.getAttribute('x') || 0) + groupTrans.x + tspanTrans.x,
                    y: parseFloat(tspan.getAttribute('y') || el.getAttribute('y') || 0) + groupTrans.y + tspanTrans.y,
                    opacity: tspan.hasAttribute('opacity') ? parseFloat(tspan.getAttribute('opacity')) : baseOpacity
                });
            });
        } else {
            texts.push({
                id: baseId,
                text: el.textContent,
                x: parseFloat(el.getAttribute('x') || 0) + groupTrans.x,
                y: parseFloat(el.getAttribute('y') || 0) + groupTrans.y,
                opacity: baseOpacity
            });
        }
    });
    return texts;
}