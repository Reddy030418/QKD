import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { toast } from 'react-toastify';
import { useAuth } from '../context/AuthContext';

const HistoryContainer = styled.div`
  max-width: 1400px;
  margin: 0 auto;
  padding: 2rem;
  transition: all 0.3s ease;

  &:hover {
    transform: translateY(-5px) scale(1.02);
    box-shadow: 0 10px 40px rgba(0, 212, 255, 0.3);
  }
`;

const Title = styled.h1`
  text-align: center;
  margin-bottom: 2rem;
  background: linear-gradient(45deg, #00d4ff, #ff00f7);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  font-size: 2.5rem;
`;

const SessionsGrid = styled.div`
  display: grid;
  gap: 1rem;
`;

const SessionCard = styled.div`
  background: rgba(255, 255, 255, 0.05);
  border-radius: 16px;
  padding: 1.5rem;
  border: 1px solid rgba(255, 255, 255, 0.1);
  transition: all 0.3s ease;

  &:hover {
    transform: translateY(-2px);
    border-color: #00d4ff;
  }
`;

const SessionHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
`;

const SessionId = styled.div`
  color: #00d4ff;
  font-weight: 600;
  font-family: 'Courier New', monospace;
`;

const StatusBadge = styled.span<{ status: string }>`
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 500;

  ${props => props.status === 'completed' && `
    background: rgba(0, 255, 136, 0.2);
    color: #00ff88;
  `}

  ${props => props.status === 'running' && `
    background: rgba(255, 170, 0, 0.2);
    color: #ffaa00;
  `}

  ${props => props.status === 'error' && `
    background: rgba(255, 68, 68, 0.2);
    color: #ff4444;
  `}
`;

const SessionStats = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 1rem;
  margin-top: 1rem;
`;

const Stat = styled.div`
  text-align: center;
`;

const StatLabel = styled.div`
  color: #cccccc;
  font-size: 0.8rem;
  margin-bottom: 0.25rem;
`;

const StatValue = styled.div<{ color?: string }>`
  font-size: 1.2rem;
  font-weight: bold;
  color: ${props => props.color || '#ffffff'};
`;

const LoadingSpinner = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  height: 200px;

  &::after {
    content: '';
    width: 40px;
    height: 40px;
    border: 3px solid rgba(0, 212, 255, 0.3);
    border-top: 3px solid #00d4ff;
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }

  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
`;

const SessionHistory: React.FC = () => {
  const [sessions, setSessions] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const { token } = useAuth();

  const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

  useEffect(() => {
    fetchSessions();
  }, []);

  const fetchSessions = async () => {
    if (!token) {
      setIsLoading(false);
      return;
    }

    try {
      const response = await fetch(`${API_URL}/sessions/`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to fetch sessions');
      }

      const data = await response.json();
      setSessions(data);
    } catch (error) {
      console.error('Error fetching sessions:', error);
      toast.error('Failed to load session history');
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return (
      <HistoryContainer>
        <Title>📜 Session History</Title>
        <LoadingSpinner />
      </HistoryContainer>
    );
  }

  return (
    <HistoryContainer>
      <Title>📜 Session History</Title>

      {sessions.length === 0 ? (
        <div style={{ textAlign: 'center', color: '#cccccc', marginTop: '2rem' }}>
          No sessions found. Start by running a QKD simulation!
        </div>
      ) : (
        <SessionsGrid>
          {sessions.map((session) => (
            <SessionCard key={session.id}>
              <SessionHeader>
                <SessionId>{session.session_id}</SessionId>
                <StatusBadge status={session.status}>
                  {session.status.toUpperCase()}
                </StatusBadge>
              </SessionHeader>

              <SessionStats>
                <Stat>
                  <StatLabel>Key Length</StatLabel>
                  <StatValue>{session.final_key_length}</StatValue>
                </Stat>

                <Stat>
                  <StatLabel>Error Rate</StatLabel>
                  <StatValue color={session.quantum_error_rate <= 11 ? '#00ff88' : '#ff4444'}>
                    {session.quantum_error_rate.toFixed(2)}%
                  </StatValue>
                </Stat>

                <Stat>
                  <StatLabel>Security</StatLabel>
                  <StatValue color={session.security_status === 'secure' ? '#00ff88' : '#ff4444'}>
                    {session.security_status.toUpperCase()}
                  </StatValue>
                </Stat>

                <Stat>
                  <StatLabel>Created</StatLabel>
                  <StatValue>
                    {new Date(session.created_at).toLocaleDateString()}
                  </StatValue>
                </Stat>
              </SessionStats>
            </SessionCard>
          ))}
        </SessionsGrid>
      )}
    </HistoryContainer>
  );
};

export default SessionHistory;
