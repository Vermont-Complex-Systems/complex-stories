// Simple browser fingerprinting for duplicate prevention
export function generateFingerprint() {
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    
    // Canvas fingerprinting
    ctx.textBaseline = 'top';
    ctx.font = '14px Arial';
    ctx.fillText('Browser fingerprint', 2, 2);
    const canvasFingerprint = canvas.toDataURL();
    
    // Collect browser characteristics
    const fingerprint = {
        userAgent: navigator.userAgent,
        language: navigator.language,
        platform: navigator.platform,
        screen: `${screen.width}x${screen.height}x${screen.colorDepth}`,
        timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
        canvas: canvasFingerprint.slice(-50), // Last 50 chars of canvas data
        webgl: getWebGLFingerprint(),
        fonts: getFontFingerprint()
    };
    
    // Create simple hash
    const fingerprintString = JSON.stringify(fingerprint);
    return simpleHash(fingerprintString);
}

function getWebGLFingerprint() {
    try {
        const canvas = document.createElement('canvas');
        const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
        if (!gl) return 'no-webgl';
        
        const renderer = gl.getParameter(gl.RENDERER);
        const vendor = gl.getParameter(gl.VENDOR);
        return `${vendor}-${renderer}`.slice(0, 50);
    } catch (e) {
        return 'webgl-error';
    }
}

function getFontFingerprint() {
    // Simple font detection
    const testFonts = ['Arial', 'Helvetica', 'Times', 'Courier', 'Verdana', 'Georgia'];
    const available = [];
    
    testFonts.forEach(font => {
        if (isFontAvailable(font)) {
            available.push(font);
        }
    });
    
    return available.join(',');
}

function isFontAvailable(font) {
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    
    ctx.font = `12px ${font}, monospace`;
    const withFont = ctx.measureText('test').width;
    
    ctx.font = '12px monospace';
    const withoutFont = ctx.measureText('test').width;
    
    return withFont !== withoutFont;
}

// Simple hash function (not cryptographic, just for fingerprinting)
function simpleHash(str) {
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
        const char = str.charCodeAt(i);
        hash = ((hash << 5) - hash) + char;
        hash = hash & hash; // Convert to 32-bit integer
    }
    return Math.abs(hash).toString(36).slice(0, 8); // 8-char alphanumeric
}