export interface ChatUser {
  id: number;
  username: string;
  email: string;
}

export interface ChatRoom {
  id: number;
  name: string;
  description?: string;
  room_type: 'general' | 'qkd_session' | 'private';
  session_id?: number;
  created_by: number;
  created_at: string;
  message_count?: number;
  last_message?: {
    content: string;
    created_at: string;
    user_id: number;
  };
}

export interface ChatMessage {
  id: number;
  content: string;
  message_type: 'text' | 'system' | 'ai_response';
  metadata?: any;
  room_id: number;
  user_id: number;
  created_at: string;
  updated_at: string;
  sender?: ChatUser;
}

export interface ChatParticipant {
  id: number;
  room_id: number;
  user_id: number;
  role: 'admin' | 'moderator' | 'member';
  joined_at: string;
  last_seen_at: string;
}

export interface AIAgent {
  id: number;
  name: string;
  description?: string;
  model_type: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface AIConversation {
  id: number;
  agent_id: number;
  user_id: number;
  room_id?: number;
  title?: string;
  context?: any;
  created_at: string;
  updated_at: string;
}

export interface AIMessage {
  id: number;
  conversation_id: number;
  role: 'user' | 'assistant' | 'system';
  content: string;
  tokens_used?: number;
  model_response?: any;
  created_at: string;
}

export interface ChatState {
  currentRoom: ChatRoom | null;
  rooms: ChatRoom[];
  messages: ChatMessage[];
  participants: ChatParticipant[];
  isConnected: boolean;
  isLoading: boolean;
  error: string | null;
}

export interface ChatContextType extends ChatState {
  connect: () => void;
  disconnect: () => void;
  joinRoom: (roomId: number) => void;
  leaveRoom: () => void;
  sendMessage: (content: string, messageType?: 'text' | 'system' | 'ai_response') => void;
  createRoom: (name: string, description?: string, roomType?: string, sessionId?: number) => Promise<ChatRoom>;
  loadRooms: () => Promise<void>;
  loadMessages: (roomId: number, limit?: number, offset?: number) => Promise<void>;
  searchMessages: (roomId: number, query: string) => Promise<ChatMessage[]>;
}
