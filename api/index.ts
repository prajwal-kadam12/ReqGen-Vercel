import type { VercelRequest, VercelResponse } from '@vercel/node';

const PYTHON_BACKEND_URL = process.env.PYTHON_BACKEND_URL || 'https://prajwalk12-reqgen-api.hf.space';

export default async function handler(req: VercelRequest, res: VercelResponse) {
    // Enable CORS
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');

    if (req.method === 'OPTIONS') {
        return res.status(200).end();
    }

    const path = req.url?.replace('/api', '') || '/';

    // Health check
    if (path === '/health' || path === '/') {
        return res.status(200).json({
            status: 'healthy',
            message: 'ReqGen API is running',
            pythonBackend: PYTHON_BACKEND_URL
        });
    }

    // Proxy to Python backend for audio/ML routes
    if (path.startsWith('/python/') || path.startsWith('/process-audio') || path.startsWith('/transcribe') || path.startsWith('/summarize')) {
        try {
            const pythonPath = path.startsWith('/python/') ? path.replace('/python', '') : path;
            const targetUrl = `${PYTHON_BACKEND_URL}/api${pythonPath}`;

            console.log(`Proxying to Python backend: ${targetUrl}`);

            const response = await fetch(targetUrl, {
                method: req.method,
                headers: {
                    'Content-Type': req.headers['content-type'] || 'application/json',
                },
                body: req.method !== 'GET' ? JSON.stringify(req.body) : undefined,
            });

            const data = await response.json();
            return res.status(response.status).json(data);
        } catch (error: any) {
            console.error('Proxy error:', error);
            return res.status(500).json({
                error: 'Failed to communicate with Python backend',
                details: error.message
            });
        }
    }

    return res.status(404).json({ error: 'Not found' });
}
