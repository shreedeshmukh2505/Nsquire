import React, { useRef, useEffect, useState } from 'react';
import { MessageCircle, Send, Paperclip, Smile } from 'lucide-react';
import Chatbot from './Chatbot';

const ChatPage = () => {
  const chatContainerRef = useRef(null);
  const [inputValue, setInputValue] = useState('');

  const handleSubmit = () => {
    // Call Chatbot component to handle the user's input
    // and update the chat history
    if (inputValue.trim() !== '') {
      // Clear the input field
      setInputValue('');

      // Scroll to the bottom of the chat container
      if (chatContainerRef.current) {
        chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
      }
    }
  };

  useEffect(() => {
    // Scroll to the bottom of the chat container when the component mounts
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
    }
  }, []);

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col pt-16">
      <div className="max-w-5xl mx-auto w-full flex-grow flex flex-col px-4 sm:px-6 lg:px-8 py-8">
        {/* Chat Header */}
        <div className="bg-white shadow-sm rounded-t-xl p-6 border-b border-gray-100 flex items-center">
          <div className="bg-blue-100 text-blue-600 p-3 rounded-full mr-4">
            <MessageCircle className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">College Guide Assistant</h1>
            <p className="text-sm text-gray-600">
              AI-powered guidance for college admissions and placements
            </p>
          </div>
        </div>

        {/* Chatbot Container */}
        <div className="flex-grow bg-white shadow-md rounded-b-xl overflow-hidden">
          <div className="h-full flex flex-col">
            {/* Chatbot Component */}
            <div className="flex-grow overflow-y-auto p-6" ref={chatContainerRef}>
              <Chatbot />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatPage;