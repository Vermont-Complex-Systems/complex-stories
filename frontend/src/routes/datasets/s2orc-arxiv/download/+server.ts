import { API_BASE } from '$env/static/private';
import { error } from '@sveltejs/kit';

export async function GET({ url, cookies }) {
    try {
        // Get query parameters
        const format = url.searchParams.get('format') || 'ndjson';
        const year = url.searchParams.get('year');

        // Build backend URL
        const apiBaseUrl = `${API_BASE || 'http://localhost:3001'}/datasets`;
        let backendUrl = `${apiBaseUrl}/s2orc/arxiv/stream?format=${format}`;
        if (year) {
            backendUrl += `&year=${year}`;
        }

        // Get auth token from cookies
        const token = cookies.get('auth_token');
        if (!token) {
            throw error(401, 'Authentication required - please log in');
        }

        // Proxy the request to the backend with authentication
        const response = await fetch(backendUrl, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (!response.ok) {
            throw error(response.status, `Backend request failed: ${response.statusText}`);
        }

        // Generate filename for download
        const filename = year ? `arxiv_s2orc_${year}.${format}` : `arxiv_s2orc_all.${format}`;
        const mediaType = format === 'ndjson' ? 'application/x-ndjson' : 'text/csv';

        // Return the streaming response
        return new Response(response.body, {
            status: response.status,
            headers: {
                'Content-Type': mediaType,
                'Content-Disposition': `attachment; filename="${filename}"`,
                'X-Content-Type-Options': 'nosniff'
            }
        });

    } catch (err) {
        console.error('Download proxy error:', err);
        if (err.status) {
            throw err;
        }
        throw error(500, 'Internal server error');
    }
}