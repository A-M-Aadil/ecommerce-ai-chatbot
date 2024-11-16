export type Message = {
  id: string;
  content: string;
  role: 'user' | 'assistant';
  timestamp: Date;
  products?: Product[];
};

export type Product = {
  id: string;
  name: string;
  price: number;
  description: string;
  image: string;
  rating: number;
  reviews: number;
};

export type ChatState = {
  messages: Message[];
  isTyping: boolean;
};

export type UserData = {
  name: string;
  email: string;
  lastOrder?: {
    id: string;
    status: string;
    date: Date;
    items: Product[];
  };
};