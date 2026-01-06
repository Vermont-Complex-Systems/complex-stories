// Browser fingerprinting using FingerprintJS library
import FingerprintJS from '@fingerprintjs/fingerprintjs';

// Cache the FingerprintJS agent promise to avoid re-initialization
let fpPromise = null;

/**
 * Generate a stable browser fingerprint using FingerprintJS.
 * Returns a high-entropy visitor ID that persists across page loads.
 *
 * @returns {Promise<string>} The visitor ID (fingerprint)
 */
export async function generateFingerprint() {
    // Initialize FingerprintJS once and cache the promise
    if (!fpPromise) {
        fpPromise = FingerprintJS.load();
    }

    try {
        const fp = await fpPromise;
        const result = await fp.get();

        // Returns a stable, high-entropy visitor ID
        return result.visitorId;
    } catch (error) {
        console.error('Error generating fingerprint:', error);
        // Fallback to a basic fingerprint if FingerprintJS fails
        return getFallbackFingerprint();
    }
}

/**
 * Fallback fingerprint using basic browser characteristics.
 * Only used if FingerprintJS fails to load or encounters an error.
 *
 * @returns {string} A basic fingerprint hash
 */
function getFallbackFingerprint() {
    const data = {
        userAgent: navigator.userAgent,
        language: navigator.language,
        screen: `${screen.width}x${screen.height}x${screen.colorDepth}`,
        timezone: Intl.DateTimeFormat().resolvedOptions().timeZone
    };

    const str = JSON.stringify(data);
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
        const char = str.charCodeAt(i);
        hash = ((hash << 5) - hash) + char;
        hash = hash & hash;
    }
    return `fallback-${Math.abs(hash).toString(36)}`;
}
