const API_BASE_URL = 'http://localhost:8000/api';

// --- Chat History API Functions ---

export async function fetchSessions() {
    const res = await fetch(`${API_BASE_URL}/chat/sessions`);
    if (!res.ok) throw new Error('Failed to fetch chat sessions');
    return res.json();
}

export async function fetchSessionMessages(sessionId) {
    const res = await fetch(`${API_BASE_URL}/chat/sessions/${sessionId}/messages`);
    if (!res.ok) throw new Error('Failed to fetch session messages');
    return res.json();
}

export async function createSession(systemPrompt, title = 'New Chat') {
    const res = await fetch(`${API_BASE_URL}/chat/sessions`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ system_prompt: systemPrompt, title })
    });
    if (!res.ok) throw new Error('Failed to create session');
    return res.json();
}

export async function streamChatAPI(messages, systemPrompt, customPrompt, onChunk, sessionId, onSessionCreated) {
    const response = await fetch(`${API_BASE_URL}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
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
                    if (parsed.session_id && onSessionCreated) {
                        onSessionCreated(parsed.session_id);
                    }
                    if (parsed.content) {
                        onChunk(parsed.content);
                    }
                } catch (e) {
                    console.error("JSON parse error on stream chunk:", e);
                }
            }
        }
    }
}

// --- Invoice Extraction API Function (This was the missing piece!) ---

export async function extractInvoiceAPI(rawText) {
    const response = await fetch(`${API_BASE_URL}/extract`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ raw_text: rawText })
    });

    if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Server error: ${response.statusText}`);
    }

    return response.json();
}