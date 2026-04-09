import axios from 'axios';
import { ChatRoom, ChatMessage, ChatParticipant, AIAgent, AIConversation, AIMessage } from '../types/chat';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

class ChatService {
  private api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
      'Content-Type': 'application/json',
    },
  });

  // Set auth token for requests
  setAuthToken(token: string) {
    this.api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
  }

  // Remove auth token
  removeAuthToken() {
    delete this.api.defaults.headers.common['Authorization'];
  }

  // Chat Room endpoints
  async getUserRooms(): Promise<ChatRoom[]> {
    const response = await this.api.get('/api/chat/rooms');
    return response.data;
  }

  async createRoom(
    name: string,
    description?: string,
    roomType: string = 'general',
    sessionId?: number
  ): Promise<ChatRoom> {
    const response = await this.api.post('/api/chat/rooms', {
      name,
      description,
      room_type: roomType,
      session_id: sessionId,
    });
    return response.data;
  }

  async getRoom(roomId: number): Promise<ChatRoom> {
    const response = await this.api.get(`/api/chat/rooms/${roomId}`);
    return response.data;
  }

  async getRoomMessages(
    roomId: number,
    limit: number = 50,
    offset: number = 0
  ): Promise<ChatMessage[]> {
    const response = await this.api.get(`/api/chat/rooms/${roomId}/messages`, {
      params: { limit, offset },
    });
    return response.data;
  }

  async sendMessage(
    roomId: number,
    content: string,
    messageType: 'text' | 'system' | 'ai_response' = 'text',
    metadata?: any
  ): Promise<ChatMessage> {
    const response = await this.api.post(`/api/chat/rooms/${roomId}/messages`, {
      content,
      message_type: messageType,
      metadata,
    });
    return response.data;
  }

  async getRoomParticipants(roomId: number): Promise<ChatParticipant[]> {
    const response = await this.api.get(`/api/chat/rooms/${roomId}/participants`);
    return response.data;
  }

  async addParticipant(roomId: number, userId: number, role: string = 'member'): Promise<ChatParticipant> {
    const response = await this.api.post(`/api/chat/rooms/${roomId}/participants`, {
      user_id: userId,
      role,
    });
    return response.data;
  }

  async searchMessages(roomId: number, query: string): Promise<ChatMessage[]> {
    const response = await this.api.get('/api/chat/messages/search', {
      params: { room_id: roomId, q: query },
    });
    return response.data;
  }

  // AI Agent endpoints
  async getAIAgents(): Promise<AIAgent[]> {
    const response = await this.api.get('/api/chat/ai/agents');
    return response.data;
  }

  async createAIAgent(
    name: string,
    description?: string,
    modelType: string = 'gpt-3.5-turbo',
    apiEndpoint?: string,
    apiKey?: string,
    systemPrompt?: string
  ): Promise<AIAgent> {
    const response = await this.api.post('/api/chat/ai/agents', {
      name,
      description,
      model_type: modelType,
      api_endpoint: apiEndpoint,
      api_key: apiKey,
      system_prompt: systemPrompt,
    });
    return response.data;
  }

  async getAIConversations(): Promise<AIConversation[]> {
    const response = await this.api.get('/api/chat/ai/conversations');
    return response.data;
  }

  async createAIConversation(
    agentId: number,
    title?: string,
    context?: any
  ): Promise<AIConversation> {
    const response = await this.api.post('/api/chat/ai/conversations', {
      agent_id: agentId,
      title,
      context,
    });
    return response.data;
  }

  async getAIConversationMessages(conversationId: number): Promise<AIMessage[]> {
    const response = await this.api.get(`/api/chat/ai/conversations/${conversationId}/messages`);
    return response.data;
  }

  async sendAIMessage(conversationId: number, content: string): Promise<{
    user_message: AIMessage;
    ai_message: AIMessage;
  }> {
    const response = await this.api.post(`/api/chat/ai/conversations/${conversationId}/messages`, {
      content,
    });
    return response.data;
  }
}

export const chatService = new ChatService();
