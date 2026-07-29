import React, { useState } from 'react';
import { extractInvoiceAPI } from '../services/api';
import { FileCode, Zap, CheckCircle, AlertTriangle, Copy, Check } from 'lucide-react';

const SAMPLE_TEXT = `Invoice #INV-2026-8890
Issued by: Apex Cloud Technologies LLC
Billed to: Cyberdyne Systems
Date: July 20, 2026

Items:
1. Kubernetes Cluster Node GPU Instance - 4 units @ $250.00 each = $1,000.00
2. Enterprise Support SLA 24/7 - 1 unit @ $350.00 = $350.00

Subtotal: $1,350.00
Tax (10%): $135.00
Total Amount Due: $1,485.00 USD`;

export default function ExtractorView() {
    const [text, setText] = useState(SAMPLE_TEXT);
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState(null);
    const [copied, setCopied] = useState(false);

    const handleExtract = async () => {
        if (!text.trim()) return;
        setLoading(true);
        setResult(null);
        try {
            const res = await extractInvoiceAPI(text);
            setResult(res);
        } catch (err) {
            setResult({ success: false, error: err.message });
        } finally {
            setLoading(false);
        }
    };

    const copyToClipboard = () => {
        if (result && result.data) {
            navigator.clipboard.writeText(JSON.stringify(result.data, null, 2));
            setCopied(true);
            setTimeout(() => setCopied(false), 2000);
        }
    };

    return (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px', height: 'calc(100vh - 120px)', padding: '0 40px 20px' }}>

            {/* Left Text Input */}
            <div className="glass-panel" style={{ padding: '20px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <h3 style={{ fontSize: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <FileCode size={18} color="var(--accent-cyan)" /> Raw Input Text
                    </h3>
                    <button className="glass-button" style={{ padding: '4px 10px', fontSize: '12px' }} onClick={() => setText(SAMPLE_TEXT)}>
                        Load Preset Sample
                    </button>
                </div>

                <textarea
                    className="glass-textarea"
                    style={{ flex: 1, resize: 'none', fontFamily: 'monospace', fontSize: '13px' }}
                    placeholder="Paste raw invoice text or receipt email here..."
                    value={text}
                    onChange={(e) => setText(e.target.value)}
                />

                <button className="glass-button" style={{ justifyContent: 'center', padding: '14px' }} onClick={handleExtract} disabled={loading}>
                    <Zap size={18} /> {loading ? "Extracting & Validating..." : "Extract Structured JSON"}
                </button>
            </div>

            {/* Right JSON Output */}
            <div className="glass-panel" style={{ padding: '20px', display: 'flex', flexDirection: 'column', gap: '16px', overflow: 'hidden' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <h3 style={{ fontSize: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                        Verified JSON Output
                    </h3>
                    {result && result.success && (
                        <button className="glass-button" style={{ padding: '4px 10px', fontSize: '12px' }} onClick={copyToClipboard}>
                            {copied ? <Check size={14} color="#10b981" /> : <Copy size={14} />} {copied ? 'Copied!' : 'Copy JSON'}
                        </button>
                    )}
                </div>

                {/* Metadata Banner */}
                {result && (
                    <div style={{
                        display: 'flex', gap: '16px', padding: '12px', borderRadius: '12px',
                        background: result.success ? 'rgba(16, 185, 129, 0.1)' : 'rgba(239, 68, 68, 0.1)',
                        border: `1px solid ${result.success ? 'rgba(16, 185, 129, 0.3)' : 'rgba(239, 68, 68, 0.3)'}`
                    }}>
                        {result.success ? <CheckCircle size={20} color="#10b981" /> : <AlertTriangle size={20} color="#ef4444" />}
                        <div style={{ fontSize: '12px', flex: 1 }}>
                            <p style={{ fontWeight: '600', color: result.success ? '#10b981' : '#ef4444' }}>
                                {result.success ? `Successfully validated (Attempts: ${result.attempts})` : 'Extraction Failed'}
                            </p>
                            {result.tokens_used && (
                                <p style={{ color: 'var(--text-muted)', marginTop: '2px' }}>
                                    Tokens: {result.tokens_used.total_tokens} | Est. Cost: ${result.estimated_cost}
                                </p>
                            )}
                        </div>
                    </div>
                )}

                {/* Code display window */}
                <div style={{
                    flex: 1,
                    background: 'rgba(15, 23, 42, 0.8)',
                    borderRadius: '12px',
                    border: '1px solid var(--glass-border)',
                    padding: '16px',
                    overflowY: 'auto',
                    fontFamily: 'monospace',
                    fontSize: '13px',
                    color: '#38bdf8'
                }}>
                    {loading ? (
                        <div style={{ color: 'var(--text-muted)', textAlign: 'center', marginTop: '40px' }}>
                            Extracting fields into Pydantic model...
                        </div>
                    ) : result ? (
                        <pre>{JSON.stringify(result.data || result.error, null, 2)}</pre>
                    ) : (
                        <div style={{ color: 'var(--text-muted)', textAlign: 'center', marginTop: '40px' }}>
                            Click "Extract Structured JSON" to view results.
                        </div>
                    )}
                </div>

            </div>
        </div>
    );
}