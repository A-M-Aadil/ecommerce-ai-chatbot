import React from 'react';
import { Bot, User } from 'lucide-react';
import type { Message } from '../types';

interface ChatMessageProps {
  message: Message;
}

export function ChatMessage({ message }: ChatMessageProps) {
  const isBot = message.role === 'assistant';

  return (
    <div className={`flex gap-3 ${isBot ? 'bg-gray-50' : ''} p-4`}>
      <div className={`flex h-8 w-8 shrink-0 select-none items-center justify-center rounded-full ${
        isBot ? 'bg-blue-600 text-white' : 'bg-gray-300 text-gray-600'
      }`}>
        {isBot ? <Bot size={18} /> : <User size={18} />}
      </div>
      <div className="flex-1 space-y-2">
        <p className="text-sm font-medium text-gray-900">
          {isBot ? 'AI Assistant' : 'You'}
        </p>
        <div className="prose prose-sm max-w-none text-gray-700">
          {message.content}
        </div>
        {message.products && (
          <div className="flex flex-wrap gap-4 mt-2">
            {message.products.map((product) => (
              <div key={product.id} className="flex flex-col gap-2 p-2 border rounded-lg bg-gray-50 max-w-[200px]">
                <img src={product.image} alt={product.name} className="h-24 w-full object-cover rounded-lg" />
                <div>
                  <p className="text-sm font-medium text-gray-900">{product.name}</p>
                  <p className="text-sm text-gray-500">{product.price}</p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}