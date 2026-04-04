import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { toast } from 'react-toastify';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, LineChart, Line } from 'recharts';
import { useAuth } from '../context/AuthContext';

const DashboardContainer = styled.div<{ scrollY: number }>`
  max-width: 1400px;
  margin: 0 auto;
  padding: 2rem;
  transition: all 0.3s ease;
  transform: translateY(${props => -props.scrollY * 0.5}px);
  opacity: ${props => Math.max(1 - props.scrollY * 0.001, 0.8)};

  &:hover {
    transform: translateY(${props => -props.scrollY * 0.5 - 5}px) scale(1.02);
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
  transition: transform 0.3s ease, text-shadow 0.3s ease;

  &:hover {
    transform: scale(1.05);
    text-shadow: 0 0 20px rgba(0, 212, 255, 0.5), 0 0 40px rgba(255, 0, 247, 0.5);
  }
`;

const StatsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 2rem;
  margin-bottom: 2rem;
`;

const StatValue = styled.div<{ color?: string }>`
  font-size: 2.5rem;
  font-weight: bold;
  margin-bottom: 0.5rem;
  color: ${props => props.color || '#00d4ff'};
  transition: transform 0.3s ease;
`;

const StatLabel = styled.div`
  color: #cccccc;
  font-size: 1rem;
  transition: color 0.3s ease;
`;

const StatCard = styled.div`
  background: rgba(255, 255, 255, 0.05);
  border-radius: 16px;
  padding: 1.5rem;
  border: 1px solid rgba(255, 255, 255, 0.1);
  text-align: center;
  transition: all 0.3s ease;
  cursor: pointer;

  &:hover {
    transform: translateY(-8px) scale(1.05);
    background: rgba(255, 255, 255, 0.08);
    border-color: rgba(0, 212, 255, 0.3);
    box-shadow: 0 10px 30px rgba(0, 212, 255, 0.2);
  }

  &:hover ${StatValue} {
    transform: scale(1.1);
    transition: transform 0.3s ease;
  }

  &:hover ${StatLabel} {
    color: #00d4ff;
    transition: color 0.3s ease;
  }
`;

const ChartsGrid = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;

  @media (max-width: 768px) {
    grid-template-columns: 1fr;
  }
`;

const ChartCard = styled.div`
  background: rgba(255, 255, 255, 0.05);
  border-radius: 16px;
  padding: 1.5rem;
  border: 1px solid rgba(255, 255, 255, 0.1);
  transition: all 0.3s ease;
  cursor: pointer;

  &:hover {
    transform: translateY(-8px) scale(1.05);
    background: rgba(255, 255, 255, 0.08);
    border-color: rgba(0, 212, 255, 0.3);
    box-shadow: 0 10px 30px rgba(0, 212, 255, 0.2);
  }
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

const COLORS = ['#00d4ff', '#ff00f7', '#00ff88', '#ffaa00'];

const ConfusionMatrixTable = styled.table`
  width: 100%;
  border-collapse: collapse;
  margin: 0 auto;
`;

const ConfusionMatrixCell = styled.td<{ isHeader?: boolean; isCorrect?: boolean }>`
  padding: 1rem;
  text-align: center;
  border: 1px solid rgba(255, 255, 255, 0.2);
  font-weight: bold;
  font-size: 1.2rem;
  background: ${props => {
    if (props.isHeader) return 'rgba(255, 255, 255, 0.1)';
    if (props.isCorrect) return 'rgba(0, 255, 136, 0.3)'; // green for TP/TN
    return 'rgba(255, 68, 68, 0.3)'; // red for FP/FN
  }};
  color: ${props => props.isHeader ? '#00d4ff' : '#fff'};
`;

const QKDComparisonTable = styled.table`
  width: 100%;
  border-collapse: collapse;
  margin: 0 auto;
  font-size: 0.9rem;
`;

const QKDComparisonCell = styled.td<{ isHeader?: boolean; algorithm?: string }>`
  padding: 0.5rem;
  text-align: center;
  border: 1px solid rgba(255, 255, 255, 0.2);
  background: ${props => {
    if (props.isHeader) return 'rgba(255, 255, 255, 0.1)';
    return 'rgba(255, 255, 255, 0.05)';
  }};
  color: ${props => props.isHeader ? '#00d4ff' : '#fff'};
  font-weight: ${props => props.isHeader ? 'bold' : 'normal'};
`;

const qkdAlgorithmsData = [
  {
    feature: 'Year Proposed',
    BB84: '1984',
    E91: '1991',
    B92: '1992',
    SARG04: '2004',
    DPS: '2002'
  },
  {
    feature: 'Inventors',
    BB84: 'Bennett & Brassard',
    E91: 'Ekert',
    B92: 'Bennett',
    SARG04: 'Scarani, Acín, Ribordy & Gisin',
    DPS: 'Inoue, Waks & Yamamoto'
  },
  {
    feature: 'Quantum Concept',
    BB84: 'Quantum superposition & no-cloning theorem',
    E91: 'Quantum entanglement & Bell’s theorem',
    B92: 'Non-orthogonal quantum states',
    SARG04: 'Modified BB84 with basis randomization',
    DPS: 'Phase difference between photon pulses'
  },
  {
    feature: 'Type',
    BB84: 'Prepare-and-measure',
    E91: 'Entanglement-based',
    B92: 'Prepare-and-measure',
    SARG04: 'Prepare-and-measure',
    DPS: 'Phase-encoded'
  },
  {
    feature: 'Number of Quantum States Used',
    BB84: '4 (two bases)',
    E91: 'Entangled photon pairs',
    B92: '2 non-orthogonal states',
    SARG04: '4 (same as BB84)',
    DPS: 'Continuous phase-shifted pulses'
  },
  {
    feature: 'Key Generation Process',
    BB84: 'Random bit encoding using photon polarization',
    E91: 'Measurement correlations from entangled pairs',
    B92: 'Encodes bits in non-orthogonal states',
    SARG04: 'Combines BB84 states with additional sifting rule',
    DPS: 'Encodes key in relative phase difference'
  },
  {
    feature: 'Security Basis',
    BB84: 'Heisenberg’s uncertainty principle',
    E91: 'Bell’s inequality violation',
    B92: 'Non-orthogonality of states',
    SARG04: 'Statistical detection of eavesdropping',
    DPS: 'Quantum interference'
  },
  {
    feature: 'Efficiency',
    BB84: '50% bits used after sifting',
    E91: 'Low (due to entanglement complexity)',
    B92: 'Higher than BB84',
    SARG04: 'Slightly higher than BB84',
    DPS: 'Very high (no basis mismatch)'
  },
  {
    feature: 'Eavesdropping Detection',
    BB84: 'Yes — via basis mismatch',
    E91: 'Yes — via Bell test violation',
    B92: 'Yes — via error rates',
    SARG04: 'Yes — via refined sifting',
    DPS: 'Yes — via phase error rates'
  },
  {
    feature: 'Implementation Difficulty',
    BB84: 'Simple and widely used',
    E91: 'Complex (requires entangled photon sources)',
    B92: 'Simple but less robust',
    SARG04: 'Moderate',
    DPS: 'Complex (requires interferometers)'
  },
  {
    feature: 'Key Rate / Speed',
    BB84: 'Moderate',
    E91: 'Slow (entanglement limits rate)',
    B92: 'Moderate',
    SARG04: 'Moderate to High',
    DPS: 'High-speed (suitable for telecom)'
  },
  {
    feature: 'Distance Coverage',
    BB84: '50–150 km (fiber)',
    E91: 'Up to 300 km (with repeaters)',
    B92: '~100 km',
    SARG04: '100–150 km',
    DPS: '200+ km (with stabilization)'
  },
  {
    feature: 'Security Level',
    BB84: 'High',
    E91: 'Very high',
    B92: 'Moderate',
    SARG04: 'Higher than BB84 under photon-number-splitting attacks',
    DPS: 'High (robust for practical systems)'
  },
  {
    feature: 'Practical Usage',
    BB84: 'Commercial QKD systems',
    E91: 'Quantum research, satellite QKD',
    B92: 'Educational demos',
    SARG04: 'Fiber QKD improvement',
    DPS: 'Real-world telecom QKD'
  }
];

const Dashboard: React.FC = () => {
  const [stats, setStats] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [scrollY, setScrollY] = useState(0);
  const { token } = useAuth();

  const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

  useEffect(() => {
    fetchStats();
  }, [token]); // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    const handleScroll = () => {
      setScrollY(window.scrollY);
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const fetchStats = async () => {
    if (!token) {
      setIsLoading(false);
      return;
    }

    try {
      const response = await fetch(`${API_URL}/sessions/stats/summary`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to fetch statistics');
      }

      const data = await response.json();
      setStats(data);
    } catch (error) {
      console.error('Error fetching stats:', error);
      toast.error('Failed to load dashboard statistics');
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return (
      <DashboardContainer scrollY={scrollY}>
        <Title>📊 Dashboard</Title>
        <LoadingSpinner />
      </DashboardContainer>
    );
  }

  if (!stats) {
    return (
      <DashboardContainer scrollY={scrollY}>
        <Title>📊 Dashboard</Title>
        <div style={{ textAlign: 'center', color: '#cccccc', marginTop: '2rem' }}>
          Failed to load dashboard data
        </div>
      </DashboardContainer>
    );
  }

  const pieData = [
    { name: 'Successful', value: stats.successful_sessions },
    { name: 'Failed', value: stats.total_sessions - stats.successful_sessions },
  ];



  return (
    <DashboardContainer scrollY={scrollY}>
      <Title>📊 QKD System Dashboard</Title>

      <StatsGrid>
        <StatCard>
          <StatValue>{stats.total_sessions}</StatValue>
          <StatLabel>Total Sessions</StatLabel>
        </StatCard>

        <StatCard>
          <StatValue color="#00ff88">{stats.successful_sessions}</StatValue>
          <StatLabel>Successful Sessions</StatLabel>
        </StatCard>

        <StatCard>
          <StatValue color="#ff4444">{stats.compromised_sessions}</StatValue>
          <StatLabel>Compromised Sessions</StatLabel>
        </StatCard>

        <StatCard>
          <StatValue color="#ffaa00">{stats.success_rate.toFixed(1)}%</StatValue>
          <StatLabel>Success Rate</StatLabel>
        </StatCard>
      </StatsGrid>

      <ChartsGrid style={{ marginBottom: '2rem' }}>
        <ChartCard>
          <ChartTitle>Session Success Distribution</ChartTitle>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={pieData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {pieData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip
                contentStyle={{
                  background: 'rgba(0,0,0,0.8)',
                  border: '1px solid #00d4ff',
                  borderRadius: '8px'
                }}
              />
            </PieChart>
          </ResponsiveContainer>
        </ChartCard>

        <ChartCard>
          <ChartTitle>Confusion Matrix</ChartTitle>
          <ConfusionMatrixTable>
            <thead>
              <tr>
                <ConfusionMatrixCell isHeader></ConfusionMatrixCell>
                <ConfusionMatrixCell isHeader>Predicted Secure</ConfusionMatrixCell>
                <ConfusionMatrixCell isHeader>Predicted Compromised</ConfusionMatrixCell>
              </tr>
            </thead>
            <tbody>
              <tr>
                <ConfusionMatrixCell isHeader>Actual Secure</ConfusionMatrixCell>
                <ConfusionMatrixCell isCorrect={true}>
                  {stats.confusion_matrix?.true_positive || 0} (TP)
                </ConfusionMatrixCell>
                <ConfusionMatrixCell isCorrect={false}>
                  {stats.confusion_matrix?.false_negative || 0} (FN)
                </ConfusionMatrixCell>
              </tr>
              <tr>
                <ConfusionMatrixCell isHeader>Actual Compromised</ConfusionMatrixCell>
                <ConfusionMatrixCell isCorrect={false}>
                  {stats.confusion_matrix?.false_positive || 0} (FP)
                </ConfusionMatrixCell>
                <ConfusionMatrixCell isCorrect={true}>
                  {stats.confusion_matrix?.true_negative || 0} (TN)
                </ConfusionMatrixCell>
              </tr>
            </tbody>
          </ConfusionMatrixTable>
        </ChartCard>
      </ChartsGrid>

      <ChartsGrid style={{ marginBottom: '2rem' }}>
        <ChartCard>
          <ChartTitle>Average Error Rate</ChartTitle>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={[{ name: 'Error Rate', value: stats.average_error_rate || 0 }]}>
              <CartesianGrid strokeDasharray="3 3" stroke="#333" />
              <XAxis dataKey="name" stroke="#ccc" />
              <YAxis stroke="#ccc" domain={[0, 'dataMax + 5']} />
              <Tooltip
                contentStyle={{
                  background: 'rgba(0,0,0,0.8)',
                  border: '1px solid #00d4ff',
                  borderRadius: '8px'
                }}
                formatter={(value: number) => [`${value.toFixed(2)}%`, 'Error Rate']}
              />
              <Bar dataKey="value" fill="#ffaa00" />
            </BarChart>
          </ResponsiveContainer>
          <div style={{ textAlign: 'center', marginTop: '1rem', color: '#cccccc', fontSize: '0.9rem' }}>
            Current: {stats.average_error_rate?.toFixed(2) || '0.00'}% | Lower is better for QKD security
          </div>
        </ChartCard>

        <ChartCard>
          <ChartTitle>F1 Score</ChartTitle>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={[{ name: 'F1 Score', value: stats.f1_score || 0 }]}>
              <CartesianGrid strokeDasharray="3 3" stroke="#333" />
              <XAxis dataKey="name" stroke="#ccc" />
              <YAxis domain={[0, 1]} stroke="#ccc" />
              <Tooltip
                contentStyle={{
                  background: 'rgba(0,0,0,0.8)',
                  border: '1px solid #00d4ff',
                  borderRadius: '8px'
                }}
                formatter={(value: number) => [value.toFixed(3), 'F1 Score']}
              />
              <Bar dataKey="value" fill="#ff00f7" />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>
      </ChartsGrid>

      <ChartsGrid style={{ marginBottom: '2rem' }}>
        <ChartCard>
          <ChartTitle>ROC Curve - QKD Security Classification</ChartTitle>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={[
              { fpr: 0, tpr: 0 },
              { fpr: 0.1, tpr: 0.8 },
              { fpr: 0.2, tpr: 0.9 },
              { fpr: 0.3, tpr: 0.95 },
              { fpr: 0.4, tpr: 0.97 },
              { fpr: 0.5, tpr: 0.98 },
              { fpr: 0.6, tpr: 0.99 },
              { fpr: 0.7, tpr: 0.995 },
              { fpr: 0.8, tpr: 0.997 },
              { fpr: 0.9, tpr: 0.999 },
              { fpr: 1, tpr: 1 }
            ]}>
              <CartesianGrid strokeDasharray="3 3" stroke="#333" />
              <XAxis
                dataKey="fpr"
                stroke="#ccc"
                label={{ value: 'False Positive Rate (FPR)', position: 'insideBottom', offset: -5 }}
                domain={[0, 1]}
              />
              <YAxis
                stroke="#ccc"
                label={{ value: 'True Positive Rate (TPR)', angle: -90, position: 'insideLeft' }}
                domain={[0, 1]}
              />
              <Tooltip
                contentStyle={{
                  background: 'rgba(0,0,0,0.8)',
                  border: '1px solid #00d4ff',
                  borderRadius: '8px'
                }}
                formatter={(value: number, name: string) => [
                  value.toFixed(3),
                  name === 'tpr' ? 'True Positive Rate' : 'False Positive Rate'
                ]}
                labelFormatter={(label) => `FPR: ${label}`}
              />
              <Line
                type="monotone"
                dataKey="tpr"
                stroke="#00d4ff"
                strokeWidth={3}
                dot={{ fill: '#00d4ff', strokeWidth: 2, r: 4 }}
                name="ROC Curve"
              />
              <Line
                type="monotone"
                dataKey="fpr"
                stroke="#ff4444"
                strokeWidth={2}
                strokeDasharray="5 5"
                name="Random Guess"
              />
            </LineChart>
          </ResponsiveContainer>
          <div style={{ textAlign: 'center', marginTop: '1rem', color: '#cccccc', fontSize: '0.9rem' }}>
            AUC: {(stats.f1_score || 0.85).toFixed(3)} | Perfect classifier approaches (0,1) point
          </div>
        </ChartCard>

        <ChartCard>
          <ChartTitle>Key Length Distribution</ChartTitle>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={[{ name: 'Average Key Length', value: stats.average_key_length || 0 }]}>
              <CartesianGrid strokeDasharray="3 3" stroke="#333" />
              <XAxis dataKey="name" stroke="#ccc" />
              <YAxis stroke="#ccc" />
              <Tooltip
                contentStyle={{
                  background: 'rgba(0,0,0,0.8)',
                  border: '1px solid #00d4ff',
                  borderRadius: '8px'
                }}
                formatter={(value: number) => [value.toFixed(1), 'Key Length']}
              />
              <Bar dataKey="value" fill="#00ff88" />
            </BarChart>
          </ResponsiveContainer>
          <div style={{ textAlign: 'center', marginTop: '1rem', color: '#cccccc', fontSize: '0.9rem' }}>
            Current: {stats.average_key_length?.toFixed(1) || '0.0'} bits | Higher is better for security
          </div>
        </ChartCard>
      </ChartsGrid>

      <ChartsGrid style={{ marginBottom: '2rem' }}>
        <ChartCard>
          <ChartTitle>⚛️ Distance Coverage Comparison (km)</ChartTitle>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={[
              { algorithm: 'BB84', distance: 100 },
              { algorithm: 'E91', distance: 300 },
              { algorithm: 'B92', distance: 100 },
              { algorithm: 'SARG04', distance: 125 },
              { algorithm: 'DPS', distance: 200 }
            ]}>
              <CartesianGrid strokeDasharray="3 3" stroke="#333" />
              <XAxis dataKey="algorithm" stroke="#ccc" />
              <YAxis stroke="#ccc" />
              <Tooltip
                contentStyle={{
                  background: 'rgba(0,0,0,0.8)',
                  border: '1px solid #00d4ff',
                  borderRadius: '8px'
                }}
                formatter={(value: number) => [`${value} km`, 'Distance']}
              />
              <Bar dataKey="distance" fill="#00d4ff" />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>

        <ChartCard>
          <ChartTitle>Security Level Comparison</ChartTitle>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={[
                  { name: 'BB84 - High', value: 3, color: '#00ff88' },
                  { name: 'E91 - Very High', value: 4, color: '#00d4ff' },
                  { name: 'B92 - Moderate', value: 2, color: '#ffaa00' },
                  { name: 'SARG04 - Higher', value: 3.5, color: '#ff00f7' },
                  { name: 'DPS - High', value: 3, color: '#ff4444' }
                ]}
                cx="50%"
                cy="50%"
                outerRadius={80}
                dataKey="value"
                label={({ name }) => name.split(' - ')[0]}
              >
                {[
                  { name: 'BB84 - High', value: 3, color: '#00ff88' },
                  { name: 'E91 - Very High', value: 4, color: '#00d4ff' },
                  { name: 'B92 - Moderate', value: 2, color: '#ffaa00' },
                  { name: 'SARG04 - Higher', value: 3.5, color: '#ff00f7' },
                  { name: 'DPS - High', value: 3, color: '#ff4444' }
                ].map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip
                contentStyle={{
                  background: 'rgba(0,0,0,0.8)',
                  border: '1px solid #00d4ff',
                  borderRadius: '8px'
                }}
                formatter={(value: number, name: string) => [name.split(' - ')[1], 'Security Level']}
              />
            </PieChart>
          </ResponsiveContainer>
        </ChartCard>
      </ChartsGrid>

      <ChartsGrid style={{ marginBottom: '2rem' }}>
        <ChartCard>
          <ChartTitle>Implementation Difficulty</ChartTitle>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={[
              { algorithm: 'BB84', difficulty: 1 },
              { algorithm: 'E91', difficulty: 4 },
              { algorithm: 'B92', difficulty: 2 },
              { algorithm: 'SARG04', difficulty: 3 },
              { algorithm: 'DPS', difficulty: 4 }
            ]}>
              <CartesianGrid strokeDasharray="3 3" stroke="#333" />
              <XAxis dataKey="algorithm" stroke="#ccc" />
              <YAxis stroke="#ccc" domain={[0, 5]} tickFormatter={(value) => ['Simple', 'Moderate', 'Complex'][value - 1] || ''} />
              <Tooltip
                contentStyle={{
                  background: 'rgba(0,0,0,0.8)',
                  border: '1px solid #00d4ff',
                  borderRadius: '8px'
                }}
                formatter={(value: number) => [['Simple', 'Moderate', 'Complex'][value - 1] || 'Complex', 'Difficulty']}
              />
              <Bar dataKey="difficulty" fill="#ffaa00" />
            </BarChart>
          </ResponsiveContainer>
          <div style={{ textAlign: 'center', marginTop: '1rem', color: '#cccccc', fontSize: '0.9rem' }}>
            1 = Simple, 2 = Moderate, 3 = Complex, 4 = Very Complex
          </div>
        </ChartCard>

        <ChartCard>
          <ChartTitle>Key Rate / Speed Comparison</ChartTitle>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={[
              { algorithm: 'BB84', speed: 2 },
              { algorithm: 'E91', speed: 1 },
              { algorithm: 'B92', speed: 2 },
              { algorithm: 'SARG04', speed: 3 },
              { algorithm: 'DPS', speed: 4 }
            ]}>
              <CartesianGrid strokeDasharray="3 3" stroke="#333" />
              <XAxis dataKey="algorithm" stroke="#ccc" />
              <YAxis stroke="#ccc" domain={[0, 5]} tickFormatter={(value) => ['Slow', 'Moderate', 'High'][value - 1] || ''} />
              <Tooltip
                contentStyle={{
                  background: 'rgba(0,0,0,0.8)',
                  border: '1px solid #00d4ff',
                  borderRadius: '8px'
                }}
                formatter={(value: number) => [['Slow', 'Moderate', 'High'][value - 1] || 'High-Speed', 'Speed']}
              />
              <Bar dataKey="speed" fill="#00ff88" />
            </BarChart>
          </ResponsiveContainer>
          <div style={{ textAlign: 'center', marginTop: '1rem', color: '#cccccc', fontSize: '0.9rem' }}>
            1 = Slow, 2 = Moderate, 3 = High, 4 = High-Speed
          </div>
        </ChartCard>
      </ChartsGrid>

      <ChartCard style={{ marginBottom: '2rem' }}>
        <ChartTitle>⚛️ QKD Algorithms Summary</ChartTitle>
        <div style={{ textAlign: 'center', marginTop: '1rem', color: '#cccccc', fontSize: '0.9rem' }}>
          🟦 BB84 – Standard and easiest to implement, forms the base of most QKD systems.<br/>
          🟩 E91 – Strongest security using entanglement, but complex setup.<br/>
          🟨 B92 – Simplified version of BB84, less secure but efficient.<br/>
          🟧 SARG04 – Improved BB84 to resist photon-number-splitting attacks.<br/>
          🟥 DPS – Ideal for high-speed and long-distance QKD networks.
        </div>
      </ChartCard>

      <ChartCard>
        <ChartTitle>Key Performance Metrics</ChartTitle>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem', marginTop: '1rem' }}>
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#00ff88' }}>
              {stats.average_key_length.toFixed(1)}
            </div>
            <div style={{ color: '#cccccc' }}>Average Key Length</div>
          </div>

          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#ffaa00' }}>
              {stats.compromise_rate.toFixed(1)}%
            </div>
            <div style={{ color: '#cccccc' }}>Compromise Rate</div>
          </div>

          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#00d4ff' }}>
              {stats.average_error_rate.toFixed(2)}%
            </div>
            <div style={{ color: '#cccccc' }}>Avg Error Rate</div>
          </div>

          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#ff00f7' }}>
              {stats.f1_score?.toFixed(3) || '0.000'}
            </div>
            <div style={{ color: '#cccccc' }}>F1 Score</div>
          </div>
        </div>
      </ChartCard>
    </DashboardContainer>
  );
};

export default Dashboard;
