import React from 'react';
import Chatbot from './Chatbot';

const ChatPage = () => {
  return (
    <div className="min-h-screen bg-gray-50 pt-20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900">College Guide Assistant</h1>
          <p className="mt-2 text-lg text-gray-600">
            Ask me anything about colleges, admissions, or placements
          </p>
        </div>
        <Chatbot />
      </div>
    </div>
  );
};

export default ChatPage;