import React, { useEffect, useMemo, useState } from 'react';
import styled from 'styled-components';
import { toast } from 'react-toastify';
import axios from 'axios';
import { apiGet } from '../utils/api';

type SessionItem = {
  id: number;
  session_id: string;
  final_key_length: number;
  quantum_error_rate: number;
  security_status: 'secure' | 'compromised' | string;
  status: string;
  created_at: string;
};

const HistoryContainer = styled.div`
  max-width: 1400px;
  margin: 0 auto;
  padding: 2rem;
`;

const Title = styled.h1`
  text-align: center;
  margin-bottom: 1.5rem;
  background: linear-gradient(45deg, #00d4ff, #ff00f7);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  font-size: 2.3rem;
`;

const FiltersRow = styled.div`
  display: grid;
  grid-template-columns: 2fr 1fr 1fr;
  gap: 0.8rem;
  margin-bottom: 1.2rem;

  @media (max-width: 900px) {
    grid-template-columns: 1fr;
  }
`;

const Input = styled.input`
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: #fff;
  border-radius: 8px;
  padding: 0.7rem;
`;

const Select = styled.select`
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: #fff;
  border-radius: 8px;
  padding: 0.7rem;
`;

const SessionsGrid = styled.div`
  display: grid;
  gap: 1rem;
`;

const SessionCard = styled.div`
  background: rgba(255, 255, 255, 0.05);
  border-radius: 16px;
  padding: 1.2rem;
  border: 1px solid rgba(255, 255, 255, 0.1);
`;

const SessionHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.8rem;
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

  ${(props) =>
    props.status === 'completed' &&
    `
      background: rgba(0, 255, 136, 0.2);
      color: #00ff88;
    `}

  ${(props) =>
    props.status !== 'completed' &&
    `
      background: rgba(255, 170, 0, 0.2);
      color: #ffaa00;
    `}
`;

const SessionStats = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 0.8rem;
`;

const Stat = styled.div`
  text-align: center;
`;

const StatLabel = styled.div`
  color: #cccccc;
  font-size: 0.78rem;
  margin-bottom: 0.2rem;
`;

const StatValue = styled.div<{ color?: string }>`
  font-size: 1.05rem;
  font-weight: bold;
  color: ${(props) => props.color || '#ffffff'};
`;

const LoadingSpinner = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  height: 180px;

  &::after {
    content: '';
    width: 36px;
    height: 36px;
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
  const [sessions, setSessions] = useState<SessionItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [securityFilter, setSecurityFilter] = useState<'all' | 'secure' | 'compromised'>('all');
  const [statusFilter, setStatusFilter] = useState<'all' | 'completed' | 'running' | 'error'>('all');

  useEffect(() => {
    const fetchSessions = async () => {
      try {
        const data = await apiGet<SessionItem[]>('/sessions/');
        setSessions(data);
      } catch (error) {
        if (axios.isAxiosError(error) && error.response?.status === 401) {
          toast.error('Session expired. Please login again.');
        } else {
          toast.error('Failed to load session history.');
        }
      } finally {
        setIsLoading(false);
      }
    };

    fetchSessions();
  }, []);

  const filteredSessions = useMemo(() => {
    return sessions.filter((session) => {
      const matchSearch =
        search.trim().length === 0 ||
        session.session_id.toLowerCase().includes(search.toLowerCase());
      const matchSecurity = securityFilter === 'all' || session.security_status === securityFilter;
      const matchStatus = statusFilter === 'all' || session.status === statusFilter;
      return matchSearch && matchSecurity && matchStatus;
    });
  }, [sessions, search, securityFilter, statusFilter]);

  if (isLoading) {
    return (
      <HistoryContainer>
        <Title>Session History</Title>
        <LoadingSpinner />
      </HistoryContainer>
    );
  }

  return (
    <HistoryContainer>
      <Title>Session History</Title>

      <FiltersRow>
        <Input
          placeholder="Search by session ID"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
        <Select
          value={securityFilter}
          onChange={(e) => setSecurityFilter(e.target.value as 'all' | 'secure' | 'compromised')}
        >
          <option value="all">All Security States</option>
          <option value="secure">Secure Only</option>
          <option value="compromised">Compromised Only</option>
        </Select>
        <Select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value as 'all' | 'completed' | 'running' | 'error')}
        >
          <option value="all">All Status</option>
          <option value="completed">Completed</option>
          <option value="running">Running</option>
          <option value="error">Error</option>
        </Select>
      </FiltersRow>

      {filteredSessions.length === 0 ? (
        <div style={{ textAlign: 'center', color: '#cccccc', marginTop: '2rem' }}>
          No sessions match the selected filters.
        </div>
      ) : (
        <SessionsGrid>
          {filteredSessions.map((session) => (
            <SessionCard key={session.id}>
              <SessionHeader>
                <SessionId>{session.session_id}</SessionId>
                <StatusBadge status={session.status}>{session.status.toUpperCase()}</StatusBadge>
              </SessionHeader>

              <SessionStats>
                <Stat>
                  <StatLabel>Key Length</StatLabel>
                  <StatValue>{session.final_key_length}</StatValue>
                </Stat>

                <Stat>
                  <StatLabel>Error Rate</StatLabel>
                  <StatValue color={session.quantum_error_rate <= 11 ? '#00ff88' : '#ff557a'}>
                    {session.quantum_error_rate.toFixed(2)}%
                  </StatValue>
                </Stat>

                <Stat>
                  <StatLabel>Security</StatLabel>
                  <StatValue color={session.security_status === 'secure' ? '#00ff88' : '#ff557a'}>
                    {session.security_status.toUpperCase()}
                  </StatValue>
                </Stat>

                <Stat>
                  <StatLabel>Created</StatLabel>
                  <StatValue>{new Date(session.created_at).toLocaleDateString()}</StatValue>
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
