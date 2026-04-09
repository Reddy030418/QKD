import React from 'react';
import styled from 'styled-components';
import { ChatMessage } from '../types/chat';
import { useAuth } from '../context/AuthContext';

const MessageContainer = styled.div`
  display: flex;
  margin-bottom: 1rem;
  padding: 0 1rem;
`;

const Avatar = styled.div`
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: linear-gradient(45deg, #00d4ff, #ff00f7);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: bold;
  margin-right: 1rem;
  flex-shrink: 0;
`;

const MessageContent = styled.div`
  flex: 1;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  padding: 1rem;
  border: 1px solid rgba(255, 255, 255, 0.1);
`;

const MessageHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
`;

const Username = styled.span`
  font-weight: 600;
  color: #00d4ff;
  font-size: 0.9rem;
`;

const Timestamp = styled.span`
  font-size: 0.8rem;
  color: rgba(255, 255, 255, 0.5);
`;

const MessageText = styled.div`
  color: #ffffff;
  line-height: 1.5;
  word-wrap: break-word;

  pre {
    background: rgba(0, 0, 0, 0.3);
    padding: 0.5rem;
    border-radius: 4px;
    overflow-x: auto;
    margin: 0.5rem 0;
  }

  code {
    background: rgba(0, 0, 0, 0.3);
    padding: 0.2rem 0.4rem;
    border-radius: 3px;
    font-family: 'Courier New', monospace;
  }
`;

const SystemMessage = styled.div`
  background: rgba(255, 193, 7, 0.1);
  border: 1px solid rgba(255, 193, 7, 0.3);
  color: #ffc107;
  text-align: center;
  padding: 0.5rem 1rem;
  border-radius: 8px;
  font-style: italic;
`;

const AIMessage = styled.div`
  background: rgba(40, 167, 69, 0.1);
  border: 1px solid rgba(40, 167, 69, 0.3);
  color: #28a745;
`;

interface MessageProps {
  message: ChatMessage;
}

const Message: React.FC<MessageProps> = ({ message }) => {
  const { user } = useAuth();
  const isOwnMessage = user?.id === message.user_id;
  const isSystemMessage = message.message_type === 'system';
  const isAIMessage = message.message_type === 'ai_response';

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diff = now.getTime() - date.getTime();

    if (diff < 60000) return 'Just now';
    if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`;
    if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`;
    return date.toLocaleDateString();
  };

  if (isSystemMessage) {
    return (
      <MessageContainer style={{ justifyContent: 'center' }}>
        <SystemMessage>
          {message.content}
        </SystemMessage>
      </MessageContainer>
    );
  }

  return (
    <MessageContainer style={{ flexDirection: isOwnMessage ? 'row-reverse' : 'row' }}>
      <Avatar>
        {message.sender?.username?.charAt(0).toUpperCase() || '?'}
      </Avatar>

      <MessageContent style={{
        marginLeft: isOwnMessage ? '1rem' : '0',
        marginRight: isOwnMessage ? '0' : '1rem',
        background: isAIMessage ? 'rgba(40, 167, 69, 0.1)' : 'rgba(255, 255, 255, 0.05)',
        border: isAIMessage ? '1px solid rgba(40, 167, 69, 0.3)' : '1px solid rgba(255, 255, 255, 0.1)'
      }}>
        <MessageHeader>
          <Username>
            {isAIMessage ? '🤖 AI Assistant' : (message.sender?.username || 'Unknown User')}
          </Username>
          <Timestamp>{formatTimestamp(message.created_at)}</Timestamp>
        </MessageHeader>

        <MessageText style={{ color: isAIMessage ? '#28a745' : '#ffffff' }}>
          {message.content}
        </MessageText>
      </MessageContent>
    </MessageContainer>
  );
};

export default Message;
