import { useState, useRef, useEffect } from 'react';
import {
  Terminal, Shield, Activity, Zap, Server,
  Search, Play, AlertCircle, Eye, Network,
  Globe, Save, CheckCircle
} from 'lucide-react';

const NMAP_OPTIONS = [
  { id: 'sS', flag: '-sS', title: 'TCP SYN Scan', desc: 'Default stealthy scan. Fast and relatively unobtrusive.', icon: <Zap size={16} /> },
  { id: 'sT', flag: '-sT', title: 'TCP Connect Scan', desc: 'Full connection scan. Leaves logs but doesn\'t require raw packets.', icon: <Network size={16} /> },
  { id: 'O', flag: '-O', title: 'OS Detection', desc: 'Attempts to determine the operating system of the target.', icon: <Server size={16} /> },
  { id: 'sV', flag: '-sV', title: 'Service Version', desc: 'Probes open ports to determine service/version info.', icon: <Search size={16} /> },
  { id: 'A', flag: '-A', title: 'Aggressive Scan', desc: 'Enables OS detection, version detection, script scanning, and traceroute.', icon: <Activity size={16} /> },
  { id: 'Pn', flag: '-Pn', title: 'Skip Ping', desc: 'Treat all hosts as online. Skips host discovery.', icon: <Eye size={16} /> },
  { id: 'T4', flag: '-T4', title: 'Aggressive Timing', desc: 'Speeds up the scan. Good for reliable networks.', icon: <Zap size={16} /> },
  { id: 'v', flag: '-v', title: 'Verbose Mode', desc: 'Increases verbosity level to show more details during scan.', icon: <Terminal size={16} /> }
];

function App() {
  const [target, setTarget] = useState('scanme.nmap.org');
  const [selectedOptions, setSelectedOptions] = useState(['sS', 'v']);
  const [output, setOutput] = useState('');
  const [isScanning, setIsScanning] = useState(false);
  
  // DNS State
  const [dnsIp, setDnsIp] = useState('10.10.10.10');
  const [dnsHostname, setDnsHostname] = useState('example.htb');
  const [dnsStatus, setDnsStatus] = useState('');
  const [isAddingHost, setIsAddingHost] = useState(false);

  const terminalRef = useRef(null);

  const toggleOption = (id) => {
    setSelectedOptions(prev =>
      prev.includes(id) ? prev.filter(o => o !== id) : [...prev, id]
    );
  };

  const getCommandString = () => {
    const flags = selectedOptions.map(id => NMAP_OPTIONS.find(o => o.id === id).flag).join(' ');
    return `nmap ${flags} ${target}`;
  };

  const handleScan = async () => {
    if (!target) return;

    setIsScanning(true);
    setOutput(`$ ${getCommandString()}\nStarting scan...\n\n`);

    const flags = selectedOptions.map(id => NMAP_OPTIONS.find(o => o.id === id).flag).join(' ');

    try {
      const response = await fetch('http://localhost:3001/api/scan', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ target, options: flags }),
      });

      if (!response.body) throw new Error('ReadableStream not supported');

      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        const chunk = decoder.decode(value, { stream: true });
        setOutput(prev => prev + chunk);
      }
    } catch (error) {
      setOutput(prev => prev + `\n\n[ERROR] ${error.message}`);
    } finally {
      setIsScanning(false);
    }
  };

  useEffect(() => {
    if (terminalRef.current) {
      terminalRef.current.scrollTop = terminalRef.current.scrollHeight;
    }
  }, [output]);

  return (
    <div className="app-container">
      <div className="sidebar">
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '24px' }}>
          <Shield color="var(--accent-primary)" size={32} />
          <h1>K3yb0ard Recon</h1>
        </div>

        <div className="input-group">
          <label>Target IP / Hostname</label>
          <input
            type="text"
            className="text-input"
            value={target}
            onChange={(e) => setTarget(e.target.value)}
            placeholder="e.g. 192.168.1.1 or example.com"
          />
        </div>

        <div className="glass-panel" style={{ padding: '16px', background: 'rgba(0, 255, 204, 0.05)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
            <Terminal size={16} color="var(--accent-primary)" />
            <span style={{ fontSize: '14px', fontWeight: '600' }}>Preview</span>
          </div>
          <div style={{ fontFamily: 'var(--font-mono)', fontSize: '12px', color: 'var(--text-secondary)' }}>
            $ {getCommandString()}
          </div>
        </div>

        <button
          className="btn btn-primary"
          onClick={handleScan}
          disabled={isScanning || !target}
          style={{ marginTop: 'auto', opacity: isScanning || !target ? 0.5 : 1 }}
        >
          {isScanning ? (
            <>
              <div className="loader"></div>
              Scanning...
            </>
          ) : (
            <>
              <Play size={18} />
              Launch Scan
            </>
          )}
        </button>
      </div>

      <div className="main-content">
        <div className="top-bar">
          <h2>Scan Configuration</h2>
          {isScanning && (
            <div className="scanning-indicator">
              <Activity size={18} />
              <span>Active Reconnaissance in Progress</span>
            </div>
          )}
        </div>

        <div className="content-area">
          <div className="glass-panel section-panel full-width">
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px' }}>
              <AlertCircle size={20} color="var(--accent-secondary)" />
              <h2>Tactical Nmap Options</h2>
            </div>

            <div className="options-grid">
              {NMAP_OPTIONS.map(opt => {
                const isSelected = selectedOptions.includes(opt.id);
                return (
                  <div
                    key={opt.id}
                    className={`option-item ${isSelected ? 'selected' : ''}`}
                    onClick={() => toggleOption(opt.id)}
                  >
                    <input
                      type="checkbox"
                      className="option-checkbox"
                      checked={isSelected}
                      readOnly
                    />
                    <div className="option-content">
                      <div className="option-title">
                        {opt.icon}
                        {opt.title}
                        <span className="option-flag">{opt.flag}</span>
                      </div>
                      <div className="option-desc">{opt.desc}</div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          <div className="terminal-container glass-panel">
            <div className="terminal-header">
              <div className="terminal-dots">
                <div className="dot red"></div>
                <div className="dot yellow"></div>
                <div className="dot green"></div>
              </div>
              <span style={{ fontFamily: 'var(--font-mono)', fontSize: '12px', color: 'var(--text-secondary)' }}>
                recon_terminal@nexus
              </span>
            </div>
            <div className="terminal-body" ref={terminalRef}>
              {output || 'System ready. Awaiting command...'}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
