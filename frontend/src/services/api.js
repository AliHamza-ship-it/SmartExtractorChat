const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

// --- Auth Helper ---
const getHeaders = () => {
    const token = localStorage.getItem('access_token');
    return {
        'Content-Type': 'application/json',
        ...(token ? { 'Authorization': `Bearer ${token}` } : {})
    };
};

// --- Auth Endpoints ---
export async function registerAPI(data) {
    const res = await fetch(`${API_BASE_URL}/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    });
    if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail?.[0]?.msg || err.detail || 'Registration failed');
    }
    return res.json();
}

export async function verifyOtpAPI(email, otp) {
    const res = await fetch(`${API_BASE_URL}/auth/verify`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, otp })
    });
    if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || 'Verification failed');
    }
    return res.json();
}

export async function loginAPI(email, password) {
    const res = await fetch(`${API_BASE_URL}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
    });
    if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || 'Login failed');
    }
    return res.json();
}

// --- Chat History API Functions ---
export async function fetchSessions() {
    const res = await fetch(`${API_BASE_URL}/chat/sessions`, { headers: getHeaders() });
    if (!res.ok) throw new Error('Failed to fetch chat sessions');
    return res.json();
}

export async function fetchSessionMessages(sessionId) {
    const res = await fetch(`${API_BASE_URL}/chat/sessions/${sessionId}/messages`, { headers: getHeaders() });
    if (!res.ok) throw new Error('Failed to fetch session messages');
    return res.json();
}

export async function createSession(systemPrompt, title = 'New Chat') {
    const res = await fetch(`${API_BASE_URL}/chat/sessions`, {
        method: 'POST',
        headers: getHeaders(),
        body: JSON.stringify({ system_prompt: systemPrompt, title })
    });
    if (!res.ok) throw new Error('Failed to create session');
    return res.json();
}

// CRITICAL FIX: Added 'signal' parameter to handle stream aborting
export async function streamChatAPI(messages, systemPrompt, customPrompt, onChunk, sessionId, onSessionCreated, signal) {
    const response = await fetch(`${API_BASE_URL}/chat`, {
        method: 'POST',
        headers: getHeaders(),
        signal, // Attach the abort signal here
        body: JSON.stringify({
            messages,
            system_prompt: systemPrompt,
            custom_system_prompt: customPrompt,
            session_id: sessionId
        })
    });

    if (!response.ok) {
        throw new Error(`Server error: ${response.statusText}`);
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';

    while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop();

        for (const line of lines) {
            if (line.startsWith('data: ')) {
                const data = line.slice(6).trim();
                if (data === '[DONE]') return;
                try {
                    const parsed = JSON.parse(data);
                    if (parsed.session_id && onSessionCreated) onSessionCreated(parsed.session_id);
                    if (parsed.content) onChunk(parsed.content);
                } catch (e) {
                    console.error("JSON parse error on stream chunk:", e);
                }
            }
        }
    }
}

// --- Invoice Extraction ---
export async function extractInvoiceAPI(rawText) {
    const response = await fetch(`${API_BASE_URL}/extract`, {
        method: 'POST',
        headers: getHeaders(),
        body: JSON.stringify({ raw_text: rawText })
    });

    if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Server error: ${response.statusText}`);
    }

    return response.json();
}