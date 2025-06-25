// src/routes/api/export/+server.js
import { json } from '@sveltejs/kit';
import { render } from 'svelte/server';
import { Dashboard } from 'allotaxonometer-ui/ssr';
import { combElems, rank_turbulence_divergence, diamond_count, wordShift_dat, balanceDat } from 'allotaxonometer-ui';
import * as d3 from 'd3';
import puppeteer from 'puppeteer';

function createHTML(dashboardHTML, title1, title2) {
    return `
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>${title1} vs ${title2} - Allotaxonometer Dashboard</title>
    <style>
        body {
            margin: 0;
            padding: 20px;
            font-family: "EB Garamond", "Garamond", serif;
            background: white;
        }
        @media print {
            body { margin: 0; padding: 0; }
        }
    </style>
</head>
<body>
    ${dashboardHTML}
</body>
</html>`;
}

export async function POST({ request }) {
    try {
        const { 
            dat, 
            rtd, 
            barData, 
            balanceData, 
            maxlog10, 
            max_count_log, 
            max_shift, 
            alpha, 
            title1, 
            title2, 
            format = 'pdf' 
        } = await request.json();
        
        console.log('Using pre-computed data for export');
        
        // Convert string 'Infinity' back to number
        const alphaNum = alpha === 'Infinity' ? Infinity : parseFloat(alpha);
        
        // No computation needed - just use the data!
        const dashboardProps = {
            dat,
            alpha: alphaNum,
            divnorm: rtd.normalization,
            barData,
            balanceData,
            title: [title1, title2],
            maxlog10,
            max_count_log,
            width: 4200,
            height: 2970,
            DashboardWidth: 4200,
            DashboardHeight: 2970,
            marginInner: 160,
            marginDiamond: 40,
            xDomain: [-max_shift * 1.5, max_shift * 1.5]
        };

        const dashboardResult = render(Dashboard, { props: dashboardProps });
        const fullHTML = createHTML(dashboardResult.body, title1, title2);
        
        if (format === 'html') {
            return new Response(fullHTML, {
                headers: {
                    'Content-Type': 'text/html',
                    'Content-Disposition': `attachment; filename="${title1}_vs_${title2}.html"`
                }
            });
        }
        
        const browser = await puppeteer.launch({
            headless: true,
            args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
        });
        
        const page = await browser.newPage();
        await page.setContent(fullHTML, { 
            waitUntil: 'networkidle0',
            timeout: 3000 
        });
        
        const pdfBuffer = await page.pdf({
            format: 'A3',
            landscape: true,
            printBackground: true,
            preferCSSPageSize: false,
            margin: {
                top: '20mm',
                left: '40mm',
            },
            scale: 1.0
        });
        
        await browser.close();
        
        return new Response(pdfBuffer, {
            headers: {
                'Content-Type': 'application/pdf',
                'Content-Disposition': `attachment; filename="${title1}_vs_${title2}.pdf"`
            }
        });
        
    } catch (error) {
        console.error('Export error:', error);
        console.error('Error stack:', error.stack);
        return json({ 
            error: error.message,
            details: error.stack 
        }, { status: 500 });
    }
}