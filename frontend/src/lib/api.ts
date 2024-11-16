import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000',
});

export const sendMessage = async (content: string, userId?: string) => {
  const response = await api.post('/chat?user_id=user1', {
    message: content,
    user_id: userId,
  });
  console.log(response.data);
  return response.data;
};

