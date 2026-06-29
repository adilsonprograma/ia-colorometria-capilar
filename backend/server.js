import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { INITIAL_PROMPT, processInput } from './estudo_capilar/estudo.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const PROJECT_ROOT = path.resolve(__dirname, '..');
const FRONTEND_DIR = path.join(PROJECT_ROOT, 'frontend');

const STATIC_ROUTES = {
    '/': 'index.html',
    '/index.html': 'index.html',
    '/style.css': 'style.css',
    '/index.js': 'index.js',
    '/sw.js': 'sw.js',
    '/manifest.json': 'manifest.json'
};

const MIME_TYPES = {
    '.html': 'text/html; charset=utf-8',
    '.css': 'text/css; charset=utf-8',
    '.js': 'application/javascript; charset=utf-8',
    '.json': 'application/json; charset=utf-8'
};

const server = http.createServer((req, res) => {
    // CORS Headers
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
    res.setHeader('Cache-Control', 'no-store');

    if (req.method === 'OPTIONS') {
        res.writeHead(204);
        return res.end();
    }

    const urlPath = new URL(req.url, `http://${req.headers.host}`).pathname;

    if (req.method === 'GET') {
        if (urlPath === '/api/health') {
            res.writeHead(200, { 'Content-Type': 'application/json; charset=utf-8' });
            return res.end(JSON.stringify({
                status: 'ok',
                appName: 'ColorIA',
                initialPrompt: INITIAL_PROMPT
            }));
        }

        if (STATIC_ROUTES[urlPath]) {
            const filePath = path.join(FRONTEND_DIR, STATIC_ROUTES[urlPath]);
            if (fs.existsSync(filePath)) {
                const ext = path.extname(filePath);
                res.writeHead(200, { 'Content-Type': MIME_TYPES[ext] || 'application/octet-stream' });
                return res.end(fs.readFileSync(filePath));
            }
        }

        if (urlPath.startsWith('/api/')) {
            res.writeHead(404, { 'Content-Type': 'application/json; charset=utf-8' });
            return res.end(JSON.stringify({ error: 'Rota da API nao encontrada.' }));
        }

        res.writeHead(404, { 'Content-Type': 'text/plain; charset=utf-8' });
        return res.end('Pagina nao encontrada.');
    }

    if (req.method === 'POST') {
        if (urlPath !== '/api/chat') {
            res.writeHead(404, { 'Content-Type': 'application/json; charset=utf-8' });
            return res.end(JSON.stringify({ error: 'Rota da API nao encontrada.' }));
        }

        let body = '';
        req.on('data', chunk => body += chunk.toString());
        req.on('end', () => {
            try {
                const payload = JSON.parse(body || '{}');
                const message = (payload.message || '').trim();
                const context = payload.context || null;

                if (!message) {
                    res.writeHead(400, { 'Content-Type': 'application/json; charset=utf-8' });
                    return res.end(JSON.stringify({ error: 'A mensagem nao pode estar vazia.', context }));
                }

                const result = processInput(message, context);
                res.writeHead(200, { 'Content-Type': 'application/json; charset=utf-8' });
                res.end(JSON.stringify(result));
            } catch (e) {
                res.writeHead(400, { 'Content-Type': 'application/json; charset=utf-8' });
                res.end(JSON.stringify({ error: 'JSON invalido.' }));
            }
        });
    }
});

const PORT = process.env.PORT || 8000;
const HOST = process.env.HOST || '0.0.0.0';

server.listen(PORT, HOST, () => {
    console.log(`ColorIA Node Server disponivel em http://${HOST}:${PORT}`);
});
