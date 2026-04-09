import React, { useState } from 'react';
import styled from 'styled-components';
import ChatWindow from './ChatWindow';

const ToggleButton = styled.button`
  position: fixed;
  bottom: 20px;
  right: 20px;
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: linear-gradient(45deg, #00d4ff, #ff00f7);
  border: none;
  color: #000;
  font-size: 1.5rem;
  cursor: pointer;
  box-shadow: 0 4px 20px rgba(0, 212, 255, 0.3);
  transition: all 0.3s ease;
  z-index: 1000;

  &:hover {
    transform: scale(1.1);
    box-shadow: 0 6px 25px rgba(0, 212, 255, 0.4);
  }

  &:active {
    transform: scale(0.95);
  }
`;

const ChatModal = styled.div`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.8);
  z-index: 999;
  display: flex;
  align-items: center;
  justify-content: center;
`;

const ChatModalContent = styled.div`
  width: 90vw;
  height: 90vh;
  max-width: 1200px;
  background: rgba(0, 0, 0, 0.95);
  border-radius: 12px;
  border: 1px solid rgba(0, 212, 255, 0.3);
  overflow: hidden;
  position: relative;
`;

const CloseButton = styled.button`
  position: absolute;
  top: 1rem;
  right: 1rem;
  background: rgba(220, 53, 69, 0.2);
  border: 1px solid rgba(220, 53, 69, 0.3);
  border-radius: 50%;
  width: 40px;
  height: 40px;
  color: #ff6b6b;
  font-size: 1.2rem;
  cursor: pointer;
  z-index: 1001;
  transition: all 0.3s ease;

  &:hover {
    background: rgba(220, 53, 69, 0.3);
    transform: scale(1.1);
  }
`;

const NotificationBadge = styled.div`
  position: absolute;
  top: -5px;
  right: -5px;
  background: #ff4444;
  color: white;
  border-radius: 50%;
  width: 20px;
  height: 20px;
  font-size: 0.7rem;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
`;

interface ChatToggleProps {
  unreadCount?: number;
}

const ChatToggle: React.FC<ChatToggleProps> = ({ unreadCount = 0 }) => {
  const [isChatOpen, setIsChatOpen] = useState(false);

  const toggleChat = () => {
    setIsChatOpen(!isChatOpen);
  };

  return (
    <>
      <ToggleButton onClick={toggleChat}>
        💬
        {unreadCount > 0 && <NotificationBadge>{unreadCount}</NotificationBadge>}
      </ToggleButton>

      {isChatOpen && (
        <ChatModal onClick={() => setIsChatOpen(false)}>
          <ChatModalContent onClick={(e) => e.stopPropagation()}>
            <CloseButton onClick={() => setIsChatOpen(false)}>
              ×
            </CloseButton>
            <ChatWindow />
          </ChatModalContent>
        </ChatModal>
      )}
    </>
  );
};

export default ChatToggle;
