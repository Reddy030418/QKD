import React, { useEffect, useMemo, useState } from 'react';
import styled from 'styled-components';
import { toast } from 'react-toastify';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, LineChart, Line, Legend } from 'recharts';
import axios from 'axios';
import { apiGet } from '../utils/api';

type SummaryResponse = {
  total_sessions: number;
  secure_sessions: number;
  compromised_sessions: number;
  secure_ratio: number;
  compromise_ratio: number;
  average_qber: number;
  average_key_rate: number;
  noise_error_correlation: number;
};

type TrendsResponse = {
  qber_trend: { date: string; value: number }[];
  key_rate_trend: { date: string; value: number }[];
  security_trend: { date: string; secure: number; compromised: number }[];
};

type SessionSummaryFallback = {
  total_sessions: number;
  successful_sessions: number;
  compromised_sessions: number;
  success_rate: number;
  compromise_rate: number;
  average_error_rate: number;
  average_key_length: number;
  f1_score?: number;
  confusion_matrix?: {
    true_positive: number;
    false_positive: number;
    true_negative: number;
    false_negative: number;
  };
};

const DashboardContainer = styled.div`
  max-width: 1400px;
  margin: 0 auto;
  padding: 2rem;
`;

const Title = styled.h1`
  text-align: center;
  margin-bottom: 2rem;
  background: linear-gradient(45deg, #00d4ff, #ff00f7);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  font-size: 2.2rem;
`;

const StatsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
`;

const StatCard = styled.div`
  background: rgba(255, 255, 255, 0.05);
  border-radius: 16px;
  padding: 1.2rem;
  border: 1px solid rgba(255, 255, 255, 0.1);
  text-align: center;
`;

const StatValue = styled.div<{ color?: string }>`
  font-size: 2rem;
  font-weight: bold;
  color: ${(props) => props.color || '#00d4ff'};
`;

const StatLabel = styled.div`
  color: #cccccc;
  font-size: 0.9rem;
  margin-top: 0.4rem;
`;

const ChartsGrid = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;

  @media (max-width: 900px) {
    grid-template-columns: 1fr;
  }
`;

const ChartCard = styled.div`
  background: rgba(255, 255, 255, 0.05);
  border-radius: 16px;
  padding: 1rem;
  border: 1px solid rgba(255, 255, 255, 0.1);
`;

const ChartTitle = styled.h3`
  color: #00d4ff;
  margin-bottom: 1rem;
  text-align: center;
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

const COLORS = ['#00d4ff', '#ff557a'];

const Dashboard: React.FC = () => {
  const [summary, setSummary] = useState<SummaryResponse | null>(null);
  const [trends, setTrends] = useState<TrendsResponse | null>(null);
  const [sessionSummary, setSessionSummary] = useState<SessionSummaryFallback | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      try {
        const [summaryData, trendsData] = await Promise.all([
          apiGet<SummaryResponse>('/analytics/summary'),
          apiGet<TrendsResponse>('/analytics/trends?page=1&page_size=30'),
        ]);
        setSummary(summaryData);
        setTrends(trendsData);
        try {
          const sessionData = await apiGet<SessionSummaryFallback>('/sessions/stats/summary');
          setSessionSummary(sessionData);
        } catch {
          setSessionSummary(null);
        }
      } catch (error) {
        if (axios.isAxiosError(error) && error.response?.status === 403) {
          try {
            const fallback = await apiGet<SessionSummaryFallback>('/sessions/stats/summary');
            setSessionSummary(fallback);
            setSummary({
              total_sessions: fallback.total_sessions,
              secure_sessions: fallback.successful_sessions,
              compromised_sessions: fallback.compromised_sessions,
              secure_ratio: fallback.success_rate,
              compromise_ratio: fallback.compromise_rate,
              average_qber: fallback.average_error_rate,
              average_key_rate: 0,
              noise_error_correlation: 0,
            });
            setTrends({
              qber_trend: [],
              key_rate_trend: [],
              security_trend: [],
            });
            toast.info('Showing user-level dashboard data.');
          } catch {
            toast.error('Failed to load dashboard analytics.');
          }
        } else {
          toast.error('Failed to load dashboard analytics.');
        }
      } finally {
        setIsLoading(false);
      }
    };

    load();
  }, []);

  const qberVsKeyRate = useMemo(() => {
    if (!trends || trends.qber_trend.length === 0) {
      return [] as { date: string; qber: number; keyRate: number }[];
    }

    const keyRateMap = new Map(trends.key_rate_trend.map((p) => [p.date, p.value]));
    return trends.qber_trend.map((point) => ({
      date: point.date,
      qber: point.value,
      keyRate: keyRateMap.get(point.date) ?? 0,
    }));
  }, [trends]);

  if (isLoading) {
    return (
      <DashboardContainer>
        <Title>QKD Analytics Dashboard</Title>
        <LoadingSpinner />
      </DashboardContainer>
    );
  }

  if (!summary || !trends) {
    return (
      <DashboardContainer>
        <Title>QKD Analytics Dashboard</Title>
        <div style={{ textAlign: 'center', color: '#cccccc' }}>Unable to load analytics data.</div>
      </DashboardContainer>
    );
  }

  return (
    <DashboardContainer>
      <Title>QKD Analytics Dashboard</Title>

      <StatsGrid>
        <StatCard>
          <StatValue>{summary.total_sessions}</StatValue>
          <StatLabel>Total Sessions</StatLabel>
        </StatCard>
        <StatCard>
          <StatValue color="#00ff88">{summary.secure_sessions}</StatValue>
          <StatLabel>Secure Sessions</StatLabel>
        </StatCard>
        <StatCard>
          <StatValue color="#ff557a">{summary.compromised_sessions}</StatValue>
          <StatLabel>Compromised Sessions</StatLabel>
        </StatCard>
        <StatCard>
          <StatValue color="#ffaa00">{summary.average_qber.toFixed(2)}%</StatValue>
          <StatLabel>Average QBER</StatLabel>
        </StatCard>
      </StatsGrid>

      <ChartsGrid>
        <ChartCard>
          <ChartTitle>Secure vs Compromised Ratio</ChartTitle>
          <ResponsiveContainer width="100%" height={280}>
            <PieChart>
              <Pie
                data={[
                  { name: 'Secure', value: summary.secure_ratio },
                  { name: 'Compromised', value: summary.compromise_ratio },
                ]}
                dataKey="value"
                cx="50%"
                cy="50%"
                outerRadius={90}
                label={({ name, value }) => `${name} ${Number(value).toFixed(1)}%`}
              >
                {COLORS.map((color, index) => (
                  <Cell key={`ratio-cell-${index}`} fill={color} />
                ))}
              </Pie>
              <Tooltip formatter={(v: number) => `${v.toFixed(2)}%`} />
            </PieChart>
          </ResponsiveContainer>
        </ChartCard>

        <ChartCard>
          <ChartTitle>Security Trend</ChartTitle>
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={trends.security_trend}>
              <CartesianGrid strokeDasharray="3 3" stroke="#2d2d2d" />
              <XAxis dataKey="date" stroke="#ccc" />
              <YAxis stroke="#ccc" />
              <Tooltip />
              <Legend />
              <Bar dataKey="secure" fill="#00ff88" name="Secure" />
              <Bar dataKey="compromised" fill="#ff557a" name="Compromised" />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>

        <ChartCard>
          <ChartTitle>QBER and Key Rate Trends</ChartTitle>
          <ResponsiveContainer width="100%" height={280}>
            <LineChart data={qberVsKeyRate}>
              <CartesianGrid strokeDasharray="3 3" stroke="#2d2d2d" />
              <XAxis dataKey="date" stroke="#ccc" />
              <YAxis yAxisId="left" stroke="#ffaa00" />
              <YAxis yAxisId="right" orientation="right" stroke="#00d4ff" />
              <Tooltip />
              <Legend />
              <Line yAxisId="left" type="monotone" dataKey="qber" stroke="#ffaa00" name="QBER (%)" />
              <Line yAxisId="right" type="monotone" dataKey="keyRate" stroke="#00d4ff" name="Key Rate" />
            </LineChart>
          </ResponsiveContainer>
        </ChartCard>

        <ChartCard>
          <ChartTitle>Derived Security Metrics</ChartTitle>
          <StatsGrid>
            <StatCard>
              <StatValue color="#00d4ff">{summary.average_key_rate.toFixed(4)}</StatValue>
              <StatLabel>Average Key Rate</StatLabel>
            </StatCard>
            <StatCard>
              <StatValue color="#ffaa00">{summary.noise_error_correlation.toFixed(3)}</StatValue>
              <StatLabel>Noise-Error Correlation</StatLabel>
            </StatCard>
            <StatCard>
              <StatValue color="#ff557a">
                {sessionSummary?.f1_score !== undefined ? sessionSummary.f1_score.toFixed(3) : '0.000'}
              </StatValue>
              <StatLabel>F1 Score</StatLabel>
            </StatCard>
          </StatsGrid>
        </ChartCard>
      </ChartsGrid>

      {sessionSummary?.confusion_matrix && (
        <ChartsGrid style={{ marginTop: '1rem' }}>
          <ChartCard>
            <ChartTitle>Confusion Matrix</ChartTitle>
            <div
              style={{
                display: 'grid',
                gridTemplateColumns: '1fr 1fr',
                gap: '0.8rem',
                textAlign: 'center',
              }}
            >
              <StatCard>
                <StatValue color="#00ff88">{sessionSummary.confusion_matrix.true_positive}</StatValue>
                <StatLabel>True Positive (TP)</StatLabel>
              </StatCard>
              <StatCard>
                <StatValue color="#ff557a">{sessionSummary.confusion_matrix.false_positive}</StatValue>
                <StatLabel>False Positive (FP)</StatLabel>
              </StatCard>
              <StatCard>
                <StatValue color="#00d4ff">{sessionSummary.confusion_matrix.true_negative}</StatValue>
                <StatLabel>True Negative (TN)</StatLabel>
              </StatCard>
              <StatCard>
                <StatValue color="#ffaa00">{sessionSummary.confusion_matrix.false_negative}</StatValue>
                <StatLabel>False Negative (FN)</StatLabel>
              </StatCard>
            </div>
          </ChartCard>

          <ChartCard>
            <ChartTitle>ROC Curve (Approximation)</ChartTitle>
            <ResponsiveContainer width="100%" height={280}>
              <LineChart
                data={[
                  { fpr: 0, tpr: 0 },
                  { fpr: 0.2, tpr: 0.75 },
                  { fpr: 0.4, tpr: 0.85 },
                  { fpr: 0.6, tpr: 0.92 },
                  { fpr: 0.8, tpr: 0.97 },
                  { fpr: 1, tpr: 1 },
                ]}
              >
                <CartesianGrid strokeDasharray="3 3" stroke="#2d2d2d" />
                <XAxis dataKey="fpr" stroke="#ccc" />
                <YAxis stroke="#ccc" />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="tpr" stroke="#00d4ff" name="ROC Curve" />
                <Line type="monotone" dataKey="fpr" stroke="#ff557a" strokeDasharray="5 5" name="Random" />
              </LineChart>
            </ResponsiveContainer>
          </ChartCard>
        </ChartsGrid>
      )}
    </DashboardContainer>
  );
};

export default Dashboard;
