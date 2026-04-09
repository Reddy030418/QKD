import React, { useState, useEffect, useRef } from 'react';
import styled from 'styled-components';
import { useChat } from '../context/ChatContext';
import { useAuth } from '../context/AuthContext';
import Message from './Message';
import MessageInput from './MessageInput';
import RoomList from './RoomList';
import RoomHeader from './RoomHeader';
import { ChatMessage } from '../types/chat';

const ChatContainer = styled.div`
  display: flex;
  height: 100vh;
  background: rgba(0, 0, 0, 0.9);
`;

const Sidebar = styled.div`
  width: 300px;
  background: rgba(0, 0, 0, 0.7);
  border-right: 1px solid rgba(0, 212, 255, 0.3);
  display: flex;
  flex-direction: column;
`;

const MainChat = styled.div`
  flex: 1;
  display: flex;
  flex-direction: column;
`;

const MessagesContainer = styled.div`
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;

  &::-webkit-scrollbar {
    width: 6px;
  }

  &::-webkit-scrollbar-track {
    background: rgba(255, 255, 255, 0.1);
  }

  &::-webkit-scrollbar-thumb {
    background: rgba(0, 212, 255, 0.5);
    border-radius: 3px;
  }
`;

const EmptyState = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: rgba(255, 255, 255, 0.6);
  font-size: 1.2rem;
  text-align: center;
`;

const LoadingState = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #00d4ff;
  font-size: 1.2rem;
`;

const ChatWindow: React.FC = () => {
  const { user } = useAuth();
  const {
    currentRoom,
    messages,
    isConnected,
    isLoading,
    error,
    joinRoom,
    leaveRoom,
    sendMessage,
    loadMessages,
    connect,
  } = useChat();

  const [selectedRoomId, setSelectedRoomId] = useState<number | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Connect to chat when component mounts
  useEffect(() => {
    if (user && !isConnected) {
      connect();
    }
  }, [user, isConnected, connect]);

  // Handle room selection
  const handleRoomSelect = async (roomId: number) => {
    if (currentRoom?.id === roomId) return;

    if (currentRoom) {
      leaveRoom();
    }

    setSelectedRoomId(roomId);
    await joinRoom(roomId);
  };

  // Handle sending message
  const handleSendMessage = async (content: string) => {
    if (!currentRoom) return;
    await sendMessage(content);
  };

  // Handle loading more messages
  const handleLoadMoreMessages = async () => {
    if (!currentRoom) return;
    await loadMessages(currentRoom.id, 50, messages.length);
  };

  if (error) {
    return (
      <ChatContainer>
        <EmptyState>
          <div>
            <h3>Connection Error</h3>
            <p>{error}</p>
            <button
              onClick={connect}
              style={{
                background: '#00d4ff',
                color: 'black',
                border: 'none',
                padding: '0.5rem 1rem',
                borderRadius: '4px',
                cursor: 'pointer',
                marginTop: '1rem'
              }}
            >
              Reconnect
            </button>
          </div>
        </EmptyState>
      </ChatContainer>
    );
  }

  return (
    <ChatContainer>
      <Sidebar>
        <RoomList onRoomSelect={handleRoomSelect} selectedRoomId={selectedRoomId} />
      </Sidebar>

      <MainChat>
        {currentRoom ? (
          <>
            <RoomHeader room={currentRoom} />

            <MessagesContainer>
              {messages.length > 0 ? (
                <>
                  {messages.map((message) => (
                    <Message key={message.id} message={message} />
                  ))}
                  <div ref={messagesEndRef} />
                </>
              ) : (
                <EmptyState>
                  <div>
                    <h3>Welcome to {currentRoom.name}</h3>
                    <p>Start a conversation by sending a message below.</p>
                  </div>
                </EmptyState>
              )}
            </MessagesContainer>

            <MessageInput
              onSendMessage={handleSendMessage}
              disabled={!isConnected}
              placeholder={
                isConnected
                  ? "Type your message..."
                  : "Connecting to chat server..."
              }
            />
          </>
        ) : (
          <EmptyState>
            <div>
              <h3>Quantum Key Distribution Chat</h3>
              <p>Select a chat room from the sidebar to start messaging.</p>
              <p style={{ fontSize: '0.9rem', marginTop: '1rem', opacity: 0.7 }}>
                💡 Tip: Chat rooms can be linked to QKD sessions for discussing quantum key distribution protocols.
              </p>
            </div>
          </EmptyState>
        )}
      </MainChat>
    </ChatContainer>
  );
};

export default ChatWindow;
