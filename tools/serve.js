// Simple static file server with keep-alive + correct Content-Length.
// Usage:
//   node serve.js <root> <port> [--tls <tlsPort> <certFile> <keyFile>]
// If --tls is not given, the server looks for <root>/certs/server.pem and
// <root>/certs/server-key.pem and starts HTTPS on port 8443 automatically.
const http = require('http');
const https = require('https');
const fs = require('fs');
const path = require('path');

const root = path.resolve(process.argv[2] || process.cwd());
const port = parseInt(process.argv[3] || '8000', 10);

let tlsPort = null;
let tlsCert = null;
let tlsKey = null;
const tlsIdx = process.argv.indexOf('--tls');
if (tlsIdx !== -1) {
  tlsPort = parseInt(process.argv[tlsIdx + 1], 10);
  tlsCert = process.argv[tlsIdx + 2];
  tlsKey = process.argv[tlsIdx + 3];
}
if (!tlsPort || !tlsCert || !tlsKey) {
  const defCert = path.join(root, 'certs', 'server.pem');
  const defKey = path.join(root, 'certs', 'server-key.pem');
  if (fs.existsSync(defCert) && fs.existsSync(defKey)) {
    tlsPort = 8443;
    tlsCert = defCert;
    tlsKey = defKey;
  }
}

const MIME = {
  '.html': 'text/html; charset=utf-8',
  '.htm': 'text/html; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8',
  '.mjs': 'text/javascript; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.wasm': 'application/wasm',
  '.css': 'text/css; charset=utf-8',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.gif': 'image/gif',
  '.webp': 'image/webp',
  '.svg': 'image/svg+xml',
  '.ico': 'image/x-icon',
  '.ttf': 'font/ttf',
  '.otf': 'font/otf',
  '.woff': 'font/woff',
  '.woff2': 'font/woff2',
  '.map': 'application/json',
  '.bin': 'application/octet-stream',
  '.txt': 'text/plain; charset=utf-8',
  '.webmanifest': 'application/manifest+json',
  '.crt': 'application/x-x509-ca-cert',
  '.cer': 'application/x-x509-ca-cert',
  '.pem': 'application/x-pem-file',
};

function handle(req, res) {
  let p = decodeURIComponent((req.url || '/').split('?')[0].split('#')[0]);
  if (p.endsWith('/')) p += 'index.html';
  const file = path.resolve(path.join(root, p));
  if (!file.startsWith(root)) {
    res.writeHead(403, { 'Content-Type': 'text/plain' });
    res.end('forbidden');
    return;
  }
  fs.stat(file, (err, st) => {
    if (err || !st.isFile()) {
      res.writeHead(404, { 'Content-Type': 'text/plain' });
      res.end('not found: ' + p);
      return;
    }
    res.writeHead(200, {
      'Content-Type': MIME[path.extname(file).toLowerCase()] || 'application/octet-stream',
      'Content-Length': st.size,
      'Cache-Control': 'no-cache',
      'Access-Control-Allow-Origin': '*',
    });
    if (req.method === 'HEAD') {
      res.end();
      return;
    }
    const stream = fs.createReadStream(file);
    stream.on('error', () => res.destroy());
    stream.pipe(res);
  });
}

function listenCarefully(server, portNum, scheme) {
  server.on('error', (err) => {
    if (err && err.code === 'EADDRINUSE') {
      console.log('port ' + portNum + ' is already in use (' + scheme + ') - is the server already running?');
    } else {
      console.error('server error: ' + (err && err.message));
    }
  });
  server.listen(portNum, '0.0.0.0', () => {
    console.log('serving ' + root + ' on ' + scheme + '://0.0.0.0:' + portNum);
  });
}

listenCarefully(http.createServer(handle), port, 'http');

if (tlsPort && tlsCert && tlsKey) {
  try {
    const options = {
      cert: fs.readFileSync(tlsCert),
      key: fs.readFileSync(tlsKey),
    };
    listenCarefully(https.createServer(options, handle), tlsPort, 'https');
  } catch (err) {
    console.error('TLS server not started: ' + err.message);
  }
}
