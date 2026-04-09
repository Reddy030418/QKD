import React, { useEffect, useMemo, useState } from 'react';
import styled, { useTheme } from 'styled-components';
import { toast } from 'react-toastify';
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  Line,
  LineChart,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import { useAuth } from '../context/AuthContext';

const DashboardContainer = styled.div`
  max-width: 1400px;
  margin: 0 auto;
  padding: 2rem;
`;

const Title = styled.h1`
  text-align: center;
  margin-bottom: 2rem;
  background: linear-gradient(45deg, ${({ theme }) => theme.colors.accent}, #ff6a00);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  font-size: 2.5rem;
`;

const StatsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 1.2rem;
  margin-bottom: 2rem;
`;

const StatCard = styled.div`
  background: ${({ theme }) => theme.colors.cardBackground};
  border-radius: 16px;
  padding: 1.3rem;
  border: 1px solid ${({ theme }) => theme.colors.cardBorder};
  text-align: center;
`;

const StatValue = styled.div<{ color?: string }>`
  font-size: 2rem;
  font-weight: bold;
  margin-bottom: 0.5rem;
  color: ${({ color, theme }) => color || theme.colors.accent};
`;

const StatLabel = styled.div`
  color: ${({ theme }) => theme.colors.mutedText};
  font-size: 0.95rem;
`;

const ChartsGrid = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.2rem;

  @media (max-width: 900px) {
    grid-template-columns: 1fr;
  }
`;

const ChartCard = styled.div`
  background: ${({ theme }) => theme.colors.cardBackground};
  border-radius: 16px;
  padding: 1.2rem;
  border: 1px solid ${({ theme }) => theme.colors.cardBorder};
`;

const ChartTitle = styled.h3`
  color: ${({ theme }) => theme.colors.accent};
  margin-bottom: 1rem;
  text-align: center;
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
    border: 3px solid ${({ theme }) => `${theme.colors.accent}55`};
    border-top: 3px solid ${({ theme }) => theme.colors.accent};
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }

  @keyframes spin {
    0% {
      transform: rotate(0deg);
    }
    100% {
      transform: rotate(360deg);
    }
  }
`;

type Session = {
  eavesdropper_present: boolean;
  security_status: string;
  quantum_error_rate: number | null;
  status: string;
};

type SummaryStats = {
  total_sessions: number;
  successful_sessions: number;
  compromised_sessions: number;
  success_rate: number;
  compromise_rate: number;
  average_error_rate: number;
  average_key_length: number;
};

type RocPoint = {
  threshold: number;
  fpr: number;
  tpr: number;
};

const Dashboard: React.FC = () => {
  const [stats, setStats] = useState<SummaryStats | null>(null);
  const [sessions, setSessions] = useState<Session[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const { token } = useAuth();
  const theme = useTheme() as any;

  const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

  useEffect(() => {
    const load = async () => {
      if (!token) {
        setIsLoading(false);
        return;
      }

      try {
        const [summaryRes, sessionsRes] = await Promise.all([
          fetch(`${API_URL}/sessions/stats/summary`, {
            headers: { Authorization: `Bearer ${token}` },
          }),
          fetch(`${API_URL}/sessions/`, {
            headers: { Authorization: `Bearer ${token}` },
          }),
        ]);

        if (!summaryRes.ok || !sessionsRes.ok) {
          throw new Error('Failed to fetch dashboard data');
        }

        const summaryData = await summaryRes.json();
        const sessionsData = await sessionsRes.json();
        setStats(summaryData);
        setSessions(Array.isArray(sessionsData) ? sessionsData : []);
      } catch (error) {
        console.error(error);
        toast.error('Failed to load dashboard statistics');
      } finally {
        setIsLoading(false);
      }
    };

    load();
  }, [API_URL, token]);

  const evaluation = useMemo(() => {
    let tp = 0;
    let tn = 0;
    let fp = 0;
    let fn = 0;

    const valid = sessions.filter((s) => s.status === 'completed');

    valid.forEach((s) => {
      const actualAttack = Boolean(s.eavesdropper_present);
      const predictedAttack = s.security_status === 'compromised';

      if (predictedAttack && actualAttack) tp += 1;
      if (!predictedAttack && !actualAttack) tn += 1;
      if (predictedAttack && !actualAttack) fp += 1;
      if (!predictedAttack && actualAttack) fn += 1;
    });

    const precision = tp + fp > 0 ? tp / (tp + fp) : 0;
    const recall = tp + fn > 0 ? tp / (tp + fn) : 0;
    const f1 = precision + recall > 0 ? (2 * precision * recall) / (precision + recall) : 0;

    const rocThresholds = [0, 5, 10, 15, 20, 25, 30, 40, 50];
    const rocPoints: RocPoint[] = rocThresholds
      .map((threshold) => {
        let rocTp = 0;
        let rocTn = 0;
        let rocFp = 0;
        let rocFn = 0;

        valid.forEach((s) => {
          const score = s.quantum_error_rate ?? 0;
          const actualAttack = Boolean(s.eavesdropper_present);
          const predictedAttack = score >= threshold;

          if (predictedAttack && actualAttack) rocTp += 1;
          if (!predictedAttack && !actualAttack) rocTn += 1;
          if (predictedAttack && !actualAttack) rocFp += 1;
          if (!predictedAttack && actualAttack) rocFn += 1;
        });

        const tpr = rocTp + rocFn > 0 ? rocTp / (rocTp + rocFn) : 0;
        const fpr = rocFp + rocTn > 0 ? rocFp / (rocFp + rocTn) : 0;

        return { threshold, tpr, fpr };
      })
      .sort((a, b) => a.fpr - b.fpr);

    const auc = rocPoints.reduce((area, point, index) => {
      if (index === 0) return 0;
      const prev = rocPoints[index - 1];
      const width = point.fpr - prev.fpr;
      const avgHeight = (point.tpr + prev.tpr) / 2;
      return area + width * avgHeight;
    }, 0);

    return {
      tp,
      tn,
      fp,
      fn,
      precision,
      recall,
      f1,
      rocPoints,
      auc,
    };
  }, [sessions]);

  if (isLoading) {
    return (
      <DashboardContainer>
        <Title>Dashboard</Title>
        <LoadingSpinner />
      </DashboardContainer>
    );
  }

  if (!token) {
    return (
      <DashboardContainer>
        <Title>Dashboard</Title>
        <div style={{ textAlign: 'center', color: theme.colors.mutedText, marginTop: '2rem' }}>
          Please log in to view dashboard statistics.
        </div>
      </DashboardContainer>
    );
  }

  if (!stats) {
    return (
      <DashboardContainer>
        <Title>Dashboard</Title>
        <div style={{ textAlign: 'center', color: theme.colors.mutedText, marginTop: '2rem' }}>
          Failed to load dashboard data
        </div>
      </DashboardContainer>
    );
  }

  const pieData = [
    { name: 'Successful', value: stats.successful_sessions },
    { name: 'Failed', value: stats.total_sessions - stats.successful_sessions },
  ];

  const errorRateData = [{ name: 'Avg Error Rate', value: stats.average_error_rate }];

  const confusionData = [
    { label: 'TP', value: evaluation.tp, fill: '#1fa463' },
    { label: 'FP', value: evaluation.fp, fill: '#ff8c42' },
    { label: 'FN', value: evaluation.fn, fill: '#d94343' },
    { label: 'TN', value: evaluation.tn, fill: '#2f7cff' },
  ];

  return (
    <DashboardContainer>
      <Title>QKD System Dashboard</Title>

      <StatsGrid>
        <StatCard>
          <StatValue>{stats.total_sessions}</StatValue>
          <StatLabel>Total Sessions</StatLabel>
        </StatCard>
        <StatCard>
          <StatValue color="#1fa463">{stats.successful_sessions}</StatValue>
          <StatLabel>Successful Sessions</StatLabel>
        </StatCard>
        <StatCard>
          <StatValue color="#d94343">{stats.compromised_sessions}</StatValue>
          <StatLabel>Compromised Sessions</StatLabel>
        </StatCard>
        <StatCard>
          <StatValue color="#ff8c42">{stats.success_rate.toFixed(1)}%</StatValue>
          <StatLabel>Success Rate</StatLabel>
        </StatCard>
        <StatCard>
          <StatValue color="#2f7cff">{evaluation.f1.toFixed(3)}</StatValue>
          <StatLabel>F1 Score (Attack Detection)</StatLabel>
        </StatCard>
        <StatCard>
          <StatValue color="#8a4dff">{evaluation.auc.toFixed(3)}</StatValue>
          <StatLabel>ROC-AUC</StatLabel>
        </StatCard>
      </StatsGrid>

      <ChartsGrid>
        <ChartCard>
          <ChartTitle>Session Success Distribution</ChartTitle>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie data={pieData} cx="50%" cy="50%" outerRadius={80} dataKey="value" label>
                {pieData.map((entry, index) => (
                  <Cell key={`cell-${entry.name}`} fill={index === 0 ? '#1fa463' : '#d94343'} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </ChartCard>

        <ChartCard>
          <ChartTitle>Average Error Rate</ChartTitle>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={errorRateData}>
              <CartesianGrid strokeDasharray="3 3" stroke={theme.colors.cardBorder} />
              <XAxis dataKey="name" stroke={theme.colors.mutedText} />
              <YAxis stroke={theme.colors.mutedText} />
              <Tooltip />
              <Bar dataKey="value" fill={theme.colors.accent} />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>

        <ChartCard>
          <ChartTitle>ROC Curve (QBER Threshold Sweep)</ChartTitle>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={evaluation.rocPoints}>
              <CartesianGrid strokeDasharray="3 3" stroke={theme.colors.cardBorder} />
              <XAxis dataKey="fpr" stroke={theme.colors.mutedText} label={{ value: 'FPR', position: 'insideBottom', offset: -5 }} />
              <YAxis stroke={theme.colors.mutedText} label={{ value: 'TPR', angle: -90, position: 'insideLeft' }} />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="tpr" name="ROC" stroke="#2f7cff" strokeWidth={2} dot={{ r: 3 }} />
            </LineChart>
          </ResponsiveContainer>
        </ChartCard>

        <ChartCard>
          <ChartTitle>Confusion Matrix</ChartTitle>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={confusionData}>
              <CartesianGrid strokeDasharray="3 3" stroke={theme.colors.cardBorder} />
              <XAxis dataKey="label" stroke={theme.colors.mutedText} />
              <YAxis stroke={theme.colors.mutedText} allowDecimals={false} />
              <Tooltip />
              <Bar dataKey="value">
                {confusionData.map((entry) => (
                  <Cell key={entry.label} fill={entry.fill} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>
      </ChartsGrid>

      <ChartCard style={{ marginTop: '1.2rem' }}>
        <ChartTitle>Model Quality Summary</ChartTitle>
        <StatsGrid>
          <StatCard>
            <StatValue color="#2f7cff">{evaluation.precision.toFixed(3)}</StatValue>
            <StatLabel>Precision</StatLabel>
          </StatCard>
          <StatCard>
            <StatValue color="#1fa463">{evaluation.recall.toFixed(3)}</StatValue>
            <StatLabel>Recall</StatLabel>
          </StatCard>
          <StatCard>
            <StatValue color="#ff8c42">{stats.average_key_length.toFixed(1)}</StatValue>
            <StatLabel>Average Key Length</StatLabel>
          </StatCard>
          <StatCard>
            <StatValue color="#d94343">{stats.compromise_rate.toFixed(1)}%</StatValue>
            <StatLabel>Compromise Rate</StatLabel>
          </StatCard>
        </StatsGrid>
      </ChartCard>
    </DashboardContainer>
  );
};

export default Dashboard;
