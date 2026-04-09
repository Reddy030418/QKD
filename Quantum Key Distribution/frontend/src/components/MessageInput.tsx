import React, { useState, KeyboardEvent } from 'react';
import styled from 'styled-components';

const InputContainer = styled.div`
  padding: 1rem;
  background: rgba(0, 0, 0, 0.8);
  border-top: 1px solid rgba(0, 212, 255, 0.3);
  display: flex;
  gap: 1rem;
  align-items: center;
`;

const TextInput = styled.textarea`
  flex: 1;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  padding: 0.75rem;
  color: #ffffff;
  font-family: inherit;
  font-size: 1rem;
  resize: none;
  min-height: 40px;
  max-height: 120px;

  &:focus {
    outline: none;
    border-color: #00d4ff;
    box-shadow: 0 0 0 2px rgba(0, 212, 255, 0.2);
  }

  &::placeholder {
    color: rgba(255, 255, 255, 0.5);
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
`;

const SendButton = styled.button`
  background: linear-gradient(45deg, #00d4ff, #ff00f7);
  border: none;
  border-radius: 8px;
  padding: 0.75rem 1.5rem;
  color: #000;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  min-width: 80px;

  &:hover:not(:disabled) {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 212, 255, 0.3);
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
    transform: none;
  }
`;

const CharacterCount = styled.div`
  font-size: 0.8rem;
  color: rgba(255, 255, 255, 0.5);
  text-align: right;
  min-width: 60px;
`;

interface MessageInputProps {
  onSendMessage: (message: string) => void;
  disabled?: boolean;
  placeholder?: string;
  maxLength?: number;
}

const MessageInput: React.FC<MessageInputProps> = ({
  onSendMessage,
  disabled = false,
  placeholder = "Type your message...",
  maxLength = 1000,
}) => {
  const [message, setMessage] = useState('');

  const handleSend = () => {
    if (message.trim() && !disabled) {
      onSendMessage(message.trim());
      setMessage('');
    }
  };

  const handleKeyPress = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const value = e.target.value;
    if (value.length <= maxLength) {
      setMessage(value);
    }
  };

  return (
    <InputContainer>
      <TextInput
        value={message}
        onChange={handleInputChange}
        onKeyPress={handleKeyPress}
        placeholder={disabled ? "Connecting..." : placeholder}
        disabled={disabled}
        rows={1}
      />
      <CharacterCount>
        {message.length}/{maxLength}
      </CharacterCount>
      <SendButton
        onClick={handleSend}
        disabled={disabled || !message.trim()}
      >
        Send
      </SendButton>
    </InputContainer>
  );
};

export default MessageInput;
