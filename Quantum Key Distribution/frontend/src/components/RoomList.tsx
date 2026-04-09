import React, { useState } from 'react';
import styled from 'styled-components';
import { useChat } from '../context/ChatContext';
import { useAuth } from '../context/AuthContext';
import { ChatRoom } from '../types/chat';

const RoomListContainer = styled.div`
  display: flex;
  flex-direction: column;
  height: 100%;
`;

const Header = styled.div`
  padding: 1rem;
  border-bottom: 1px solid rgba(0, 212, 255, 0.3);
  background: rgba(0, 0, 0, 0.5);
`;

const Title = styled.h3`
  color: #00d4ff;
  margin: 0;
  font-size: 1.2rem;
`;

const CreateRoomButton = styled.button`
  background: linear-gradient(45deg, #00d4ff, #ff00f7);
  border: none;
  border-radius: 6px;
  padding: 0.5rem 1rem;
  color: #000;
  font-weight: 600;
  cursor: pointer;
  margin-top: 1rem;
  transition: all 0.3s ease;

  &:hover {
    transform: translateY(-1px);
    box-shadow: 0 2px 8px rgba(0, 212, 255, 0.3);
  }
`;

const RoomListItems = styled.div`
  flex: 1;
  overflow-y: auto;

  &::-webkit-scrollbar {
    width: 4px;
  }

  &::-webkit-scrollbar-track {
    background: rgba(255, 255, 255, 0.1);
  }

  &::-webkit-scrollbar-thumb {
    background: rgba(0, 212, 255, 0.5);
    border-radius: 2px;
  }
`;

const RoomItem = styled.div<{ isSelected: boolean }>`
  padding: 1rem;
  cursor: pointer;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  background: ${props =>
    props.isSelected
      ? 'rgba(0, 212, 255, 0.1)'
      : 'transparent'
  };
  transition: background 0.2s ease;

  &:hover {
    background: rgba(255, 255, 255, 0.05);
  }
`;

const RoomName = styled.div`
  font-weight: 600;
  color: #ffffff;
  margin-bottom: 0.25rem;
`;

const RoomDescription = styled.div`
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.6);
  margin-bottom: 0.5rem;
`;

const RoomMeta = styled.div`
  display: flex;
  justify-content: space-between;
  font-size: 0.8rem;
  color: rgba(255, 255, 255, 0.5);
`;

const LastMessage = styled.div`
  font-size: 0.85rem;
  color: rgba(255, 255, 255, 0.7);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
`;

const CreateRoomModal = styled.div`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
`;

const ModalContent = styled.div`
  background: rgba(0, 0, 0, 0.95);
  border: 1px solid rgba(0, 212, 255, 0.3);
  border-radius: 12px;
  padding: 2rem;
  width: 90%;
  max-width: 400px;
`;

const ModalTitle = styled.h3`
  color: #00d4ff;
  margin: 0 0 1rem 0;
`;

const FormGroup = styled.div`
  margin-bottom: 1rem;
`;

const Label = styled.label`
  display: block;
  color: #ffffff;
  margin-bottom: 0.5rem;
  font-size: 0.9rem;
`;

const Input = styled.input`
  width: 100%;
  padding: 0.75rem;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 6px;
  color: #ffffff;
  font-size: 1rem;

  &:focus {
    outline: none;
    border-color: #00d4ff;
  }
`;

const Select = styled.select`
  width: 100%;
  padding: 0.75rem;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 6px;
  color: #ffffff;
  font-size: 1rem;

  &:focus {
    outline: none;
    border-color: #00d4ff;
  }
`;

const ButtonGroup = styled.div`
  display: flex;
  gap: 1rem;
  margin-top: 1.5rem;
`;

const ModalButton = styled.button`
  flex: 1;
  padding: 0.75rem;
  border: none;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
`;

const CancelButton = styled(ModalButton)`
  background: rgba(255, 255, 255, 0.1);
  color: #ffffff;

  &:hover {
    background: rgba(255, 255, 255, 0.2);
  }
`;

const SubmitButton = styled(ModalButton)`
  background: linear-gradient(45deg, #00d4ff, #ff00f7);
  color: #000;
`;

interface RoomListProps {
  onRoomSelect: (roomId: number) => void;
  selectedRoomId: number | null;
}

const RoomList: React.FC<RoomListProps> = ({ onRoomSelect, selectedRoomId }) => {
  const { user } = useAuth();
  const { rooms, createRoom, isLoading } = useChat();
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newRoomName, setNewRoomName] = useState('');
  const [newRoomDescription, setNewRoomDescription] = useState('');
  const [newRoomType, setNewRoomType] = useState('general');

  const handleCreateRoom = async () => {
    if (!newRoomName.trim()) return;

    try {
      await createRoom(newRoomName, newRoomDescription, newRoomType);
      setNewRoomName('');
      setNewRoomDescription('');
      setNewRoomType('general');
      setShowCreateModal(false);
    } catch (error) {
      console.error('Failed to create room:', error);
    }
  };

  const formatLastMessageTime = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diff = now.getTime() - date.getTime();

    if (diff < 60000) return 'Just now';
    if (diff < 3600000) return `${Math.floor(diff / 60000)}m`;
    if (diff < 86400000) return `${Math.floor(diff / 3600000)}h`;
    return date.toLocaleDateString();
  };

  return (
    <RoomListContainer>
      <Header>
        <Title>Chat Rooms</Title>
        <CreateRoomButton onClick={() => setShowCreateModal(true)}>
          + New Room
        </CreateRoomButton>
      </Header>

      <RoomListItems>
        {rooms.map((room) => (
          <RoomItem
            key={room.id}
            isSelected={selectedRoomId === room.id}
            onClick={() => onRoomSelect(room.id)}
          >
            <RoomName>{room.name}</RoomName>
            {room.description && (
              <RoomDescription>{room.description}</RoomDescription>
            )}
            <RoomMeta>
              <span>{room.room_type}</span>
              {room.last_message && (
                <span>{formatLastMessageTime(room.last_message.created_at)}</span>
              )}
            </RoomMeta>
            {room.last_message && (
              <LastMessage>
                {room.last_message.user_id === user?.id ? 'You: ' : ''}
                {room.last_message.content}
              </LastMessage>
            )}
          </RoomItem>
        ))}
      </RoomListItems>

      {showCreateModal && (
        <CreateRoomModal onClick={() => setShowCreateModal(false)}>
          <ModalContent onClick={(e) => e.stopPropagation()}>
            <ModalTitle>Create New Room</ModalTitle>

            <FormGroup>
              <Label>Room Name</Label>
              <Input
                type="text"
                value={newRoomName}
                onChange={(e) => setNewRoomName(e.target.value)}
                placeholder="Enter room name"
              />
            </FormGroup>

            <FormGroup>
              <Label>Description (optional)</Label>
              <Input
                type="text"
                value={newRoomDescription}
                onChange={(e) => setNewRoomDescription(e.target.value)}
                placeholder="Enter room description"
              />
            </FormGroup>

            <FormGroup>
              <Label>Room Type</Label>
              <Select
                value={newRoomType}
                onChange={(e) => setNewRoomType(e.target.value)}
              >
                <option value="general">General</option>
                <option value="qkd_session">QKD Session</option>
                <option value="private">Private</option>
              </Select>
            </FormGroup>

            <ButtonGroup>
              <CancelButton onClick={() => setShowCreateModal(false)}>
                Cancel
              </CancelButton>
              <SubmitButton onClick={handleCreateRoom} disabled={!newRoomName.trim()}>
                Create
              </SubmitButton>
            </ButtonGroup>
          </ModalContent>
        </CreateRoomModal>
      )}
    </RoomListContainer>
  );
};

export default RoomList;
