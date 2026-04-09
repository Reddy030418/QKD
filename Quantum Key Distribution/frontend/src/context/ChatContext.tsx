import React, { createContext, useContext, useState, useEffect, useCallback, ReactNode } from 'react';
import { io, Socket } from 'socket.io-client';
import { toast } from 'react-toastify';
import { useAuth } from './AuthContext';
import { chatService } from '../services/chatService';
import { ChatContextType, ChatRoom, ChatMessage, ChatParticipant } from '../types/chat';

const ChatContext = createContext<ChatContextType | undefined>(undefined);

export const useChat = () => {
  const context = useContext(ChatContext);
  if (context === undefined) {
    throw new Error('useChat must be used within a ChatProvider');
  }
  return context;
};

interface ChatProviderProps {
  children: ReactNode;
}

export const ChatProvider: React.FC<ChatProviderProps> = ({ children }) => {
  const { user, token } = useAuth();
  const [socket, setSocket] = useState<Socket | null>(null);
  const [currentRoom, setCurrentRoom] = useState<ChatRoom | null>(null);
  const [rooms, setRooms] = useState<ChatRoom[]>([]);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [participants, setParticipants] = useState<ChatParticipant[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const WS_URL = process.env.REACT_APP_WS_URL || 'ws://localhost:8000';

  // Initialize socket connection
  const connect = useCallback(() => {
    if (!token || socket?.connected) return;

    try {
      const newSocket = io(WS_URL, {
        auth: { token },
        transports: ['websocket', 'polling'],
      });

      newSocket.on('connect', () => {
        console.log('Connected to chat server');
        setIsConnected(true);
        setError(null);
      });

      newSocket.on('disconnect', () => {
        console.log('Disconnected from chat server');
        setIsConnected(false);
      });

      newSocket.on('connect_error', (error) => {
        console.error('Connection error:', error);
        setError('Failed to connect to chat server');
        setIsConnected(false);
      });

      newSocket.on('message', (message: ChatMessage) => {
        if (currentRoom && message.room_id === currentRoom.id) {
          setMessages(prev => [...prev, message]);
        }
        // Update room's last message
        setRooms(prev => prev.map(room =>
          room.id === message.room_id
            ? { ...room, last_message: { content: message.content, created_at: message.created_at, user_id: message.user_id } }
            : room
        ));
      });

      newSocket.on('user_joined', (data: { user_id: number; room_id: number }) => {
        if (currentRoom && data.room_id === currentRoom.id) {
          toast.info('A user joined the room');
          loadParticipants(data.room_id);
        }
      });

      newSocket.on('user_left', (data: { user_id: number; room_id: number }) => {
        if (currentRoom && data.room_id === currentRoom.id) {
          toast.info('A user left the room');
          loadParticipants(data.room_id);
        }
      });

      setSocket(newSocket);

      return () => {
        newSocket.close();
        setSocket(null);
        setIsConnected(false);
      };
    } catch (error) {
      console.error('Failed to connect to chat server:', error);
      setError('Failed to connect to chat server');
    }
  }, [token, socket, currentRoom, WS_URL]);

  // Disconnect from socket
  const disconnect = useCallback(() => {
    if (socket) {
      socket.disconnect();
      setSocket(null);
      setIsConnected(false);
    }
  }, [socket]);

  // Load chat rooms
  const loadRooms = useCallback(async () => {
    if (!token) return;

    setIsLoading(true);
    try {
      chatService.setAuthToken(token);
      const userRooms = await chatService.getUserRooms();
      setRooms(userRooms);
      setError(null);
    } catch (error) {
      console.error('Failed to load rooms:', error);
      setError('Failed to load chat rooms');
      toast.error('Failed to load chat rooms');
    } finally {
      setIsLoading(false);
    }
  }, [token]);

  // Join a chat room
  const joinRoom = useCallback(async (roomId: number) => {
    try {
      const room = await chatService.getRoom(roomId);
      setCurrentRoom(room);

      // Load messages and participants
      await Promise.all([
        loadMessages(roomId),
        loadParticipants(roomId),
      ]);

      // Join room via socket if connected
      if (socket) {
        socket.emit('join_room', { room_id: roomId });
      }

      setError(null);
    } catch (error) {
      console.error('Failed to join room:', error);
      setError('Failed to join chat room');
      toast.error('Failed to join chat room');
    }
  }, [socket]);

  // Leave current room
  const leaveRoom = useCallback(() => {
    if (socket && currentRoom) {
      socket.emit('leave_room', { room_id: currentRoom.id });
    }
    setCurrentRoom(null);
    setMessages([]);
    setParticipants([]);
  }, [socket, currentRoom]);

  // Load messages for a room
  const loadMessages = useCallback(async (roomId: number, limit: number = 50, offset: number = 0) => {
    try {
      const roomMessages = await chatService.getRoomMessages(roomId, limit, offset);
      setMessages(roomMessages);
    } catch (error) {
      console.error('Failed to load messages:', error);
      toast.error('Failed to load messages');
    }
  }, []);

  // Load participants for a room
  const loadParticipants = useCallback(async (roomId: number) => {
    try {
      const roomParticipants = await chatService.getRoomParticipants(roomId);
      setParticipants(roomParticipants);
    } catch (error) {
      console.error('Failed to load participants:', error);
      toast.error('Failed to load participants');
    }
  }, []);

  // Send a message
  const sendMessage = useCallback(async (
    content: string,
    messageType: 'text' | 'system' | 'ai_response' = 'text'
  ) => {
    if (!currentRoom || !content.trim()) return;

    try {
      const message = await chatService.sendMessage(currentRoom.id, content, messageType);

      // Add message to local state immediately for better UX
      setMessages(prev => [...prev, message]);

      // Update room's last message
      setRooms(prev => prev.map(room =>
        room.id === currentRoom.id
          ? { ...room, last_message: { content, created_at: message.created_at, user_id: message.user_id } }
          : room
      ));

      // Emit via socket for real-time updates
      if (socket) {
        socket.emit('send_message', {
          room_id: currentRoom.id,
          content,
          message_type: messageType,
        });
      }
    } catch (error) {
      console.error('Failed to send message:', error);
      toast.error('Failed to send message');
    }
  }, [currentRoom, socket]);

  // Create a new room
  const createRoom = useCallback(async (
    name: string,
    description?: string,
    roomType: string = 'general',
    sessionId?: number
  ): Promise<ChatRoom> => {
    try {
      const newRoom = await chatService.createRoom(name, description, roomType, sessionId);
      setRooms(prev => [...prev, newRoom]);
      toast.success('Chat room created successfully');
      return newRoom;
    } catch (error) {
      console.error('Failed to create room:', error);
      toast.error('Failed to create chat room');
      throw error;
    }
  }, []);

  // Search messages in current room
  const searchMessages = useCallback(async (roomId: number, query: string): Promise<ChatMessage[]> => {
    try {
      return await chatService.searchMessages(roomId, query);
    } catch (error) {
      console.error('Failed to search messages:', error);
      toast.error('Failed to search messages');
      return [];
    }
  }, []);

  // Load rooms when user changes
  useEffect(() => {
    if (user && token) {
      loadRooms();
    } else {
      setRooms([]);
      setCurrentRoom(null);
      setMessages([]);
      setParticipants([]);
    }
  }, [user, token, loadRooms]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (socket) {
        socket.disconnect();
      }
    };
  }, [socket]);

  const value: ChatContextType = {
    currentRoom,
    rooms,
    messages,
    participants,
    isConnected,
    isLoading,
    error,
    connect,
    disconnect,
    joinRoom,
    leaveRoom,
    sendMessage,
    createRoom,
    loadRooms,
    loadMessages,
    searchMessages,
  };

  return (
    <ChatContext.Provider value={value}>
      {children}
    </ChatContext.Provider>
  );
};
