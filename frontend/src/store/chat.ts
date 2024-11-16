import { create } from 'zustand';
import type { Message, ChatState } from '../types'; // Ensure these types are defined in your `types.ts`
import { sendMessage } from '../lib/api'; // Assuming this is the API function to send a message.

interface ChatStore extends ChatState {
  sendMessage: (content: string) => Promise<void>;
  setTyping: (isTyping: boolean) => void;
}

export const useChatStore = create<ChatStore>((set) => ({
  messages: [
    {
      id: '1',
      content: "Say 'Hi' to start a conversation.",
      role: 'assistant',
      timestamp: new Date(),
    },
  ],
  isTyping: false,

  // Function to send a message and handle the response from the AI
  sendMessage: async (content: string) => {
    // Add user message
    const userMessage: Message = {
      id: `user-${Date.now()}`, // Using a prefix for clarity
      content,
      role: 'user',
      timestamp: new Date(),
    };

    set((state) => ({
      messages: [...state.messages, userMessage],
      isTyping: true,
    }));

    try {
      // Call the sendMessage API (assumed to be async)
      const response = await sendMessage(content);

      // Add the bot's reply
      const botMessage: Message = {
        id: `assistant-${Date.now() + 1}`, // Prefix to avoid collisions
        content: response.response,
        role: 'assistant',
        timestamp: new Date(),
        products: response.products ? response.products : [], // Assuming the response includes products
      };

      set((state) => ({
        messages: [...state.messages, botMessage],
        isTyping: false,
      }));
    } catch (error) {
      // Log the error to the console for debugging
      console.error("Error sending message:", error);

      // Add a generic error message from the assistant
      const errorMessage: Message = {
        id: `error-${Date.now()}`,
        content: 'Sorry, I encountered an error. Please try again.',
        role: 'assistant',
        timestamp: new Date(),
      };

      set((state) => ({
        messages: [...state.messages, errorMessage],
        isTyping: false,
      }));
    }
  },

  // Function to update typing status
  setTyping: (isTyping: boolean) => set({ isTyping }),
}));
