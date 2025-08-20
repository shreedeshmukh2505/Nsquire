import React, { useState, useRef, useEffect } from "react";
import axios from "axios";
import { Send, Loader, RefreshCw, Download, Trash2, AlertCircle } from "lucide-react";

const styles = `
.cutoff-container {
  background: white;
  border-radius: 8px;
  overflow: hidden;
}

.college-name {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1a365d;
  padding: 1rem;
  background: #e2e8f0;
  margin: 0;
}

.branches-container {
  padding: 1rem;
}

.branch-item {
  margin-bottom: 1.5rem;
  border-bottom: 1px solid #e2e8f0;
  padding-bottom: 1rem;
}

.branch-item:last-child {
  border-bottom: none;
  margin-bottom: 0;
}

.branch-name {
  font-size: 1.1rem;
  font-weight: 500;
  color: #2d3748;
  margin-bottom: 0.5rem;
}

.cutoff-details {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 0.5rem;
}

.category-item {
  display: flex;
  align-items: center;
  background: #f7fafc;
  padding: 0.5rem;
  border-radius: 4px;
}

.category {
  font-weight: 500;
  margin-right: 0.5rem;
  color: #4a5568;
}

.rank {
  color: #2b6cb0;
  font-weight: 600;
}
`;

function Chatbot() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const messagesEndRef = useRef(null);
  
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };
  

  useEffect(() => {
    const styleSheet = document.createElement("style");
    styleSheet.textContent = styles;
    document.head.appendChild(styleSheet);
    return () => document.head.removeChild(styleSheet);
  }, []);

  // Create a sanitized HTML render function
  const createMarkup = (html) => {
    return { __html: html };
  };

  const sendMessage = async (e) => {
    e?.preventDefault();
    setError(null);
    
    if (!input.trim()) return;
  
    const userMessage = { sender: "user", text: input, timestamp: new Date().toISOString() };
    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);
  
    try {
      const response = await axios.post("http://localhost:5002/chat", 
        { message: input },
        {
          headers: {
            'Content-Type': 'application/json'
          }
        }
      );
      
      const botMessage = { 
        sender: "bot", 
        text: response.data.response,
        timestamp: new Date().toISOString()
      };
      
      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      console.error("Full error details:", error.response || error.message);
      setError(error.response?.data?.error || "Failed to connect to the server");
    } finally {
      setIsLoading(false);
      setInput("");
    }
  };

  const clearChat = () => {
    if (window.confirm("Are you sure you want to clear the chat history?")) {
      setMessages([]);
    }
  };

  const exportChat = () => {
    const chatHistory = messages.map(msg => (
      `[${new Date(msg.timestamp).toLocaleTimeString()}] ${msg.sender}: ${msg.text}`
    )).join('\n');
    
    const blob = new Blob([chatHistory], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'chat-history.txt';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="h-[80vh] max-w-4xl mx-auto bg-white rounded-xl shadow-lg border border-gray-200">
      {/* Header */}
      <div className="p-4 border-b border-gray-200 flex justify-between items-center bg-gray-50 rounded-t-xl">
        <h2 className="text-xl font-semibold text-gray-800">College Assistant</h2>
        <div className="flex space-x-2">
          <button
            onClick={() => window.location.reload()}
            className="p-2 hover:bg-gray-200 rounded-full transition-colors"
            title="Refresh conversation"
          >
            <RefreshCw className="w-5 h-5 text-gray-600" />
          </button>
          <button
            onClick={exportChat}
            className="p-2 hover:bg-gray-200 rounded-full transition-colors"
            title="Export chat"
          >
            <Download className="w-5 h-5 text-gray-600" />
          </button>
          <button
            onClick={clearChat}
            className="p-2 hover:bg-gray-200 rounded-full transition-colors"
            title="Clear chat"
          >
            <Trash2 className="w-5 h-5 text-gray-600" />
          </button>
        </div>
      </div>

      {/* Messages Container */}
      <div className="flex-1 overflow-y-auto p-6 space-y-4 h-[calc(80vh-8rem)]">
        {error && (
          <div className="bg-red-50 border-l-4 border-red-500 p-4 mb-4 rounded">
            <div className="flex items-center">
              <AlertCircle className="w-5 h-5 text-red-500 mr-2" />
              <p className="text-red-700">{error}</p>
            </div>
          </div>
        )}
        
        {messages.length === 0 && (
          <div className="text-center text-gray-500 mt-8 space-y-2">
            <h3 className="text-xl font-semibold">Welcome to College Assistant!</h3>
            <p>Start a conversation by asking about any college admissions, courses, or placement details.</p>
          </div>
        )}
        
        {messages.map((msg, index) => (
          <div
            key={index}
            className={`flex ${msg.sender === "user" ? "justify-end" : "justify-start"}`}
          >
            <div
              className={`max-w-[80%] rounded-xl px-4 py-2 shadow-sm ${
                msg.sender === "user"
                  ? "bg-blue-600 text-white"
                  : "bg-gray-100 text-gray-900"
              }`}
            >
              <div 
                className="mb-1"
                dangerouslySetInnerHTML={createMarkup(msg.text)}
              />
              <div className={`text-xs ${msg.sender === "user" ? "text-blue-200" : "text-gray-500"}`}>
                {new Date(msg.timestamp).toLocaleTimeString()}
              </div>
            </div>
          </div>
        ))}
        
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-gray-100 rounded-xl px-4 py-2 flex items-center space-x-2">
              <Loader className="w-4 h-4 animate-spin" />
              <span>Thinking...</span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Form */}
      <form onSubmit={sendMessage} className="p-4 border-t border-gray-200 bg-gray-50 rounded-b-xl">
        <div className="flex space-x-4">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about college cutoffs, fees, packages..."
            className="flex-1 px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
          <button
            type="submit"
            disabled={isLoading || !input.trim()}
            className="bg-blue-600 text-white px-6 py-3 rounded-xl hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
          >
            <Send className="w-5 h-5" />
            <span>Send</span>
          </button>
        </div>
      </form>
    </div>
  );
}

export default Chatbot;