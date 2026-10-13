#!/usr/bin/env node
/**
 * Serve Mission Control and give its buttons a brain, with no API key.
 *
 * Built-in Node modules only. It serves the dashboard as static files
 * and accepts POST /generate, which pipes your prompt to the Claude
 * Code CLI you are already logged into. No key, no account, no cost
 * beyond the subscription you already have.
 *
 *   node scripts/proxy.js
 *   open http://localhost:3001/records/mission-control/index.html
 *
 * Open it through this URL rather than file://, or the browser will not
 * reach /generate.
 *
 * It binds to 127.0.0.1. Anything it writes obeys the same rules as the
 * agents: no claim, stat or testimonial that is not in the brand files.
 */
const http = require('http');
const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');

const ROOT = path.resolve(__dirname, '..');
const PORT = Number(process.env.PROXY_PORT || 3001);
const MAX_BODY = 32 * 1024;

const TYPES = {
  '.html': 'text/html; charset=utf-8', '.css': 'text/css; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8', '.json': 'application/json; charset=utf-8',
  '.png': 'image/png', '.jpg': 'image/jpeg', '.svg': 'image/svg+xml',
  '.webp': 'image/webp', '.mp4': 'video/mp4', '.woff2': 'font/woff2',
};

function send(res, code, body, type = 'text/plain; charset=utf-8') {
  res.writeHead(code, { 'Content-Type': type, 'Cache-Control': 'no-store' });
  res.end(body);
}

function serveStatic(req, res) {
  const url = decodeURIComponent(req.url.split('?')[0]);
  const target = path.join(ROOT, url === '/' ? 'records/mission-control/index.html' : url);
  // Never serve outside the repo, whatever the URL says.
  if (!target.startsWith(ROOT)) return send(res, 403, 'outside the repo');
  fs.readFile(target, (err, data) => {
    if (err) return send(res, 404, 'not found');
    send(res, 200, data, TYPES[path.extname(target)] || 'application/octet-stream');
  });
}

function generate(req, res) {
  let body = '';
  let tooBig = false;
  req.on('data', (chunk) => {
    body += chunk;
    if (body.length > MAX_BODY) { tooBig = true; req.destroy(); }
  });
  req.on('end', () => {
    if (tooBig) return send(res, 413, 'prompt too large');
    let parsed;
    try { parsed = JSON.parse(body); } catch { return send(res, 400, 'expected JSON'); }
    const { prompt, system } = parsed;
    if (!prompt) return send(res, 400, 'expected { prompt, system? }');

    const full = system ? `${system}\n\n---\n${prompt}` : prompt;
    const claude = spawn('claude', ['-p', full], { cwd: ROOT });
    let out = '', err = '';
    claude.stdout.on('data', (d) => { out += d; });
    claude.stderr.on('data', (d) => { err += d; });
    claude.on('error', () => send(res, 500, JSON.stringify({
      error: 'claude is not on PATH for this process',
    }), 'application/json; charset=utf-8'));
    claude.on('close', (code) => {
      if (res.writableEnded) return;
      if (code !== 0) {
        return send(res, 500, JSON.stringify({ error: err.trim() || `claude exited ${code}` }),
          'application/json; charset=utf-8');
      }
      send(res, 200, JSON.stringify({ text: out.trim() }), 'application/json; charset=utf-8');
    });
  });
}

http.createServer((req, res) => {
  if (req.method === 'POST' && req.url.split('?')[0] === '/generate') return generate(req, res);
  if (req.method === 'GET') return serveStatic(req, res);
  send(res, 405, 'method not allowed');
}).listen(PORT, '127.0.0.1', () => {
  console.log(`proxy on http://localhost:${PORT}`);
  console.log(`dashboard: http://localhost:${PORT}/records/mission-control/index.html`);
  console.log('POST /generate  { "prompt": "...", "system": "..." }  -> { "text": "..." }');
});
