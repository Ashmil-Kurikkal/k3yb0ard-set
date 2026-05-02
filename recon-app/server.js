import express from 'express';
import cors from 'cors';
import { spawn } from 'child_process';
import fs from 'fs';
import os from 'os';
import path from 'path';

const app = express();
app.use(cors());
app.use(express.json());

app.post('/api/scan', (req, res) => {
  const { target, options } = req.body;
  
  if (!target) {
    return res.status(400).json({ error: 'Target is required' });
  }

  // Basic validation to prevent command injection
  const validOptions = /^[a-zA-Z0-9\s\-.,:]+$/;
  if (options && !validOptions.test(options)) {
    return res.status(400).json({ error: 'Invalid options format' });
  }

  const args = [];
  if (options) {
    args.push(...options.split(' ').filter(Boolean));
  }
  args.push(target);

  res.setHeader('Content-Type', 'text/plain');
  res.setHeader('Transfer-Encoding', 'chunked');

  const nmap = spawn('nmap', args);

  nmap.stdout.on('data', (data) => {
    res.write(data);
  });

  nmap.stderr.on('data', (data) => {
    res.write(`ERROR: ${data}`);
  });

  nmap.on('close', (code) => {
    res.write(`\n--- Scan Completed (Code: ${code}) ---`);
    res.end();
  });
  
  nmap.on('error', (err) => {
    res.write(`\nFailed to start nmap: ${err.message}`);
    res.end();
  });
});

const PORT = 3001;

app.post('/api/add-host', (req, res) => {
  const { ip, hostname } = req.body;
  
  if (!ip || !hostname) {
    return res.status(400).json({ error: 'IP and hostname are required' });
  }

  // Basic validation
  const ipRegex = /^[0-9a-f.:]+$/i;
  const hostRegex = /^[a-zA-Z0-9.-]+$/;
  
  if (!ipRegex.test(ip) || !hostRegex.test(hostname)) {
    return res.status(400).json({ error: 'Invalid IP or hostname format' });
  }

  const hostsFile = os.platform() === 'win32' 
    ? 'C:\\Windows\\System32\\drivers\\etc\\hosts' 
    : '/etc/hosts';

  const entry = `\n${ip}\t${hostname}\n`;

  try {
    fs.appendFileSync(hostsFile, entry);
    res.json({ success: true, message: `Added ${hostname} (${ip}) to hosts file.` });
  } catch (err) {
    if (err.code === 'EACCES') {
      res.status(403).json({ error: 'Permission denied. You might need to run the server as root/Administrator.' });
    } else {
      res.status(500).json({ error: `Failed to update hosts file: ${err.message}` });
    }
  }
});

app.listen(PORT, () => {
  console.log(`Recon server listening on port ${PORT}`);
});
