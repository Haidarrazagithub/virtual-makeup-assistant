import React, { useRef, useEffect } from 'react';
import { Send, Loader2 } from 'lucide-react';
import type { ChatMessage } from '../services/api';

interface ChatAssistantProps {
  originalImage: string | null;
  chatInput: string;
  setChatInput: (input: string) => void;
  chatHistory: ChatMessage[];
  sendChatMessage: () => void;
  loading: boolean;
}

export const ChatAssistant: React.FC<ChatAssistantProps> = ({
  originalImage,
  chatInput,
  setChatInput,
  chatHistory,
  sendChatMessage,
  loading,
}) => {
  const transcriptEndRef = useRef<HTMLDivElement | null>(null);

  // Auto-scroll to bottom on new messages
  useEffect(() => {
    if (transcriptEndRef.current) {
      transcriptEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [chatHistory]);

  return (
    <div className="chat-container fade-in flex flex-col justify-between h-[450px]">
      <div className="chat-transcript flex-grow overflow-y-auto flex flex-col gap-3 max-h-[350px] pr-2 scroll-smooth">
        {chatHistory.map((msg, i) => (
          <div 
            key={i} 
            className={`chat-bubble ${msg.sender === 'user' ? 'user bg-purple-600 text-white self-end rounded-tr-none' : 'bot bg-white/5 border border-white/10 text-gray-300 self-start rounded-tl-none'}`}
          >
            {msg.text}
          </div>
        ))}
        <div ref={transcriptEndRef} />
      </div>

      {!originalImage ? (
        <div className="text-center py-6 text-sm text-gray-500">
          Upload or capture a photo to start chatting with the AI.
        </div>
      ) : (
        <div className="chat-input-bar">
          <input 
            type="text" 
            placeholder="Type a look request (e.g. 'purple eyeshadow')..."
            value={chatInput}
            onChange={(e) => setChatInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && sendChatMessage()}
            className="chat-text-input"
          />
          <button 
            onClick={sendChatMessage}
            disabled={loading}
            className="chat-send-btn flex items-center justify-center disabled:opacity-50 border-0 cursor-pointer"
          >
            {loading ? <Loader2 className="w-4.5 h-4.5 animate-spin" /> : <Send className="w-4 h-4" />}
          </button>
        </div>
      )}
    </div>
  );
};
