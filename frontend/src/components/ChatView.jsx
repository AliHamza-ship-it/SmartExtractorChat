import React, { useState, useRef, useEffect } from 'react';
import { streamChatAPI } from '../services/api';
import { Send, Bot, User, Settings } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

const PRESET_PROMPTS = [
    "AI Tech Mentor",
    "Executive Assistant",
    "Creative Writer",
    "Strict Code Auditor"
];

export default function ChatView() {
    const [messages, setMessages] = useState([
        { role: 'assistant', content: 'Hello! I am your AI assistant. Choose a role or ask me anything!' }
    ]);
    const [input, setInput] = useState('');
    const [systemPrompt, setSystemPrompt] = useState('AI Tech Mentor');
    const [customPrompt, setCustomPrompt] = useState('');
    const [showConfig, setShowConfig] = useState(false);
    const [isGenerating, setIsGenerating] = useState(false);

    // 1. Create a reference to the bottom of the chat
    const messagesEndRef = useRef(null);

    // 2. Automatically scroll to the bottom whenever 'messages' change
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    const handleSend = async () => {
        if (!input.trim() || isGenerating) return;

        const userMessage = { role: 'user', content: input };
        const newMessages = [...messages, userMessage];
        setMessages(newMessages);
        setInput('');
        setIsGenerating(true);

        const assistantIndex = newMessages.length;
        setMessages(prev => [...prev, { role: 'assistant', content: '' }]);

        try {
            await streamChatAPI(newMessages, systemPrompt, customPrompt, (chunk) => {
                setMessages(prev => {
                    const updated = [...prev];
                    // FIX: Create a brand new object to prevent React StrictMode double-mutation bugs
                    updated[assistantIndex] = {
                        ...updated[assistantIndex],
                        content: updated[assistantIndex].content + chunk
                    };
                    return updated;
                });
            });
        } catch (err) {
            setMessages(prev => {
                const updated = [...prev];
                // FIX: Same here, create a new object
                updated[assistantIndex] = {
                    ...updated[assistantIndex],
                    content: updated[assistantIndex].content + `\n[Error: ${err.message}]`
                };
                return updated;
            });
        } finally {
            setIsGenerating(false);
        }
    };

    return (
        <div style={{ display: 'grid', gridTemplateColumns: showConfig ? '300px 1fr' : '1fr', gap: '20px', height: 'calc(100vh - 120px)', padding: '0 40px 20px' }}>

            {/* Settings Sidebar */}
            {showConfig && (
                <div className="glass-panel" style={{ padding: '20px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
                    <h3 style={{ fontSize: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <Settings size={18} /> System Prompt Config
                    </h3>
                    <div>
                        <label style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Role Preset</label>
                        <select
                            className="glass-select"
                            value={systemPrompt}
                            onChange={(e) => { setSystemPrompt(e.target.value); setCustomPrompt(''); }}
                            style={{ marginTop: '6px' }}
                        >
                            {PRESET_PROMPTS.map(p => <option key={p} value={p} style={{ background: '#0f172a' }}>{p}</option>)}
                        </select>
                    </div>
                    <div>
                        <label style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Override Custom Prompt</label>
                        <textarea
                            className="glass-textarea"
                            rows={5}
                            placeholder="Enter custom instructions..."
                            value={customPrompt}
                            onChange={(e) => setCustomPrompt(e.target.value)}
                            style={{ marginTop: '6px' }}
                        />
                    </div>
                </div>
            )}

            {/* Main Chat Box */}
            <div className="glass-panel" style={{ display: 'flex', flexDirection: 'column', height: '100%', overflow: 'hidden' }}>

                {/* Header toolbar */}
                <div style={{ padding: '16px 20px', borderBottom: '1px solid var(--glass-border)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div style={{ fontSize: '14px', color: 'var(--text-muted)' }}>
                        Active Persona: <span style={{ color: 'var(--accent-cyan)', fontWeight: '600' }}>{customPrompt ? "Custom Persona" : systemPrompt}</span>
                    </div>
                    <button className="glass-button" style={{ padding: '6px 12px', fontSize: '12px' }} onClick={() => setShowConfig(!showConfig)}>
                        <Settings size={14} /> {showConfig ? 'Hide Config' : 'Configure Prompt'}
                    </button>
                </div>

                {/* Message Stream Container */}
                <div style={{ flex: 1, padding: '20px', overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '16px' }}>
                    {messages.map((m, i) => (
                        <div key={i} style={{ display: 'flex', gap: '12px', justifyContent: m.role === 'user' ? 'flex-end' : 'flex-start' }}>
                            {m.role === 'assistant' && (
                                <div style={{ background: 'linear-gradient(135deg, #8b5cf6, #06b6d4)', width: '32px', height: '32px', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                                    <Bot size={18} color="#fff" />
                                </div>
                            )}
                            <div style={{
                                maxWidth: '70%',
                                padding: '12px 16px',
                                borderRadius: '16px',
                                background: m.role === 'user' ? 'linear-gradient(135deg, rgba(139, 92, 246, 0.4), rgba(6, 182, 212, 0.4))' : 'rgba(15, 23, 42, 0.7)',
                                border: '1px solid var(--glass-border)',
                                lineHeight: '1.5',
                                overflowX: 'auto', // Allows tables to scroll horizontally if they are too wide
                            }}>
                                {m.role === 'user' ? (
                                    // User messages don't need markdown, but need line breaks preserved
                                    <div style={{ whiteSpace: 'pre-wrap' }}>{m.content}</div>
                                ) : (
                                    // Assistant messages are parsed with React Markdown
                                    <div className="markdown-body">
                                        <ReactMarkdown remarkPlugins={[remarkGfm]}>
                                            {m.content || (isGenerating && i === messages.length - 1 ? "Typing..." : "")}
                                        </ReactMarkdown>
                                    </div>
                                )}
                            </div>
                            {m.role === 'user' && (
                                <div style={{ background: 'rgba(255, 255, 255, 0.1)', width: '32px', height: '32px', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                                    <User size={18} color="#fff" />
                                </div>
                            )}
                        </div>
                    ))}

                    <div ref={messagesEndRef} />
                </div>

                {/* Input Bar */}
                <div style={{ padding: '16px', borderTop: '1px solid var(--glass-border)', display: 'flex', gap: '12px', alignItems: 'flex-end' }}>
                    <textarea
                        className="glass-textarea"
                        placeholder="Type your message... (Shift + Enter for new line)"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyDown={(e) => {
                            if (e.key === 'Enter' && !e.shiftKey) {
                                e.preventDefault(); // Prevents adding a new line when you press Enter
                                handleSend();
                            }
                        }}
                        rows={1}
                        style={{
                            flex: 1,
                            resize: 'none',
                            minHeight: '45px',
                            maxHeight: '150px',
                            overflowY: 'auto'
                        }}
                    />
                    <button className="glass-button" style={{ height: '45px' }} onClick={handleSend} disabled={isGenerating}>
                        <Send size={18} />
                    </button>
                </div>

            </div>
        </div>
    );
}