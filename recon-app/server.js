import express from 'express';
import cors from 'cors';
import { spawn } from 'child_process';

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
app.listen(PORT, () => {
  console.log(`Recon server listening on port ${PORT}`);
});
