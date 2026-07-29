import React, { useState } from 'react';
import Navbar from './components/Navbar';
import ChatView from './components/ChatView';
import ExtractorView from './components/ExtractorView';

export default function App() {
  const [activeTab, setActiveTab] = useState('chat');

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      <Navbar activeTab={activeTab} setActiveTab={setActiveTab} />
      <main style={{ flex: 1 }}>
        {activeTab === 'chat' ? <ChatView /> : <ExtractorView />}
      </main>
    </div>
  );
}