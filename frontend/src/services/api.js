export async function streamChatAPI(messages, systemPrompt, customPrompt, onChunk) {
    const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            messages,
            system_prompt: systemPrompt,
            custom_system_prompt: customPrompt || null,
            temperature: 0.7
        })
    });

    if (!response.ok) {
        throw new Error(`Chat HTTP Error: ${response.status}`);
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';

    while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
            if (line.startsWith('data: ')) {
                const dataStr = line.replace('data: ', '').trim();
                if (dataStr === '[DONE]') return;
                try {
                    const parsed = JSON.parse(dataStr);
                    if (parsed.content) onChunk(parsed.content);
                    if (parsed.error) throw new Error(parsed.error);
                } catch (e) {
                    console.error("SSE parse error", e);
                }
            }
        }
    }
}

export async function extractInvoiceAPI(rawText) {
    const response = await fetch('/api/extract', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ raw_text: rawText })
    });

    if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Extraction request failed');
    }

    return await response.json();
}