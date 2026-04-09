import React from 'react';
import styled from 'styled-components';
import { useChat } from '../context/ChatContext';
import { ChatRoom } from '../types/chat';

const HeaderContainer = styled.div`
  padding: 1rem;
  background: rgba(0, 0, 0, 0.8);
  border-bottom: 1px solid rgba(0, 212, 255, 0.3);
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const RoomInfo = styled.div`
  flex: 1;
`;

const RoomName = styled.h3`
  color: #00d4ff;
  margin: 0 0 0.25rem 0;
  font-size: 1.3rem;
`;

const RoomDescription = styled.p`
  color: rgba(255, 255, 255, 0.7);
  margin: 0;
  font-size: 0.9rem;
`;

const RoomMeta = styled.div`
  display: flex;
  gap: 1rem;
  font-size: 0.8rem;
  color: rgba(255, 255, 255, 0.5);
`;

const ParticipantsButton = styled.button`
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 6px;
  padding: 0.5rem 1rem;
  color: #ffffff;
  cursor: pointer;
  transition: all 0.3s ease;

  &:hover {
    background: rgba(255, 255, 255, 0.2);
    border-color: #00d4ff;
  }
`;

const LeaveButton = styled.button`
  background: rgba(220, 53, 69, 0.2);
  border: 1px solid rgba(220, 53, 69, 0.3);
  border-radius: 6px;
  padding: 0.5rem 1rem;
  color: #ff6b6b;
  cursor: pointer;
  transition: all 0.3s ease;

  &:hover {
    background: rgba(220, 53, 69, 0.3);
  }
`;

interface RoomHeaderProps {
  room: ChatRoom;
}

const RoomHeader: React.FC<RoomHeaderProps> = ({ room }) => {
  const { participants, leaveRoom } = useChat();

  const handleLeaveRoom = () => {
    leaveRoom();
  };

  const formatRoomType = (type: string) => {
    switch (type) {
      case 'general':
        return '💬 General';
      case 'qkd_session':
        return '🔐 QKD Session';
      case 'private':
        return '🔒 Private';
      default:
        return type;
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <HeaderContainer>
      <RoomInfo>
        <RoomName>{room.name}</RoomName>
        {room.description && (
          <RoomDescription>{room.description}</RoomDescription>
        )}
        <RoomMeta>
          <span>{formatRoomType(room.room_type)}</span>
          <span>•</span>
          <span>{participants.length} participants</span>
          <span>•</span>
          <span>Created {formatDate(room.created_at)}</span>
        </RoomMeta>
      </RoomInfo>

      <div style={{ display: 'flex', gap: '0.5rem' }}>
        <ParticipantsButton>
          👥 {participants.length}
        </ParticipantsButton>
        <LeaveButton onClick={handleLeaveRoom}>
          Leave
        </LeaveButton>
      </div>
    </HeaderContainer>
  );
};

export default RoomHeader;
