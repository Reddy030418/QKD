import React, { useState, useEffect, useRef } from 'react';
import styled from 'styled-components';
import { toast } from 'react-toastify';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line } from 'recharts';
import { useAuth } from '../context/AuthContext';
import ChatToggle from './ChatToggle';

interface QKDParameters {
  key_length: number;
  noise_level: number;
  detector_efficiency: number;
  algorithm: 'bb84' | 'e91' | 'b92';
  eavesdropper_present: boolean;
}

interface QKDResult {
  session_id: string;
  status: string;
  alice_bits: number[];
  alice_bases: number[];
  bob_bases: number[];
  bob_measurements: (number | null)[];
  sifted_alice: number[];
  sifted_bob: number[];
  final_key: number[];
  stats: {
    transmitted: number;
    detected: number;
    error_rate: number;
    final_key_length: number;
  };
  security_status: string;
  error_rate: number;
}

const SimulatorContainer = styled.div`
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
  font-size: 2.5rem;
`;

const ControlsSection = styled.div`
  background: rgba(255, 255, 255, 0.05);
  border-radius: 16px;
  padding: 2rem;
  margin-bottom: 2rem;
  border: 1px solid rgba(255, 255, 255, 0.1);
`;

const ControlGroup = styled.div`
  margin-bottom: 1.5rem;
`;

const Label = styled.label`
  display: block;
  margin-bottom: 0.5rem;
  color: #00d4ff;
  font-weight: 500;
`;

const Input = styled.input`
  width: 100%;
  padding: 0.75rem;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.05);
  color: #ffffff;
  font-size: 1rem;

  &:focus {
    outline: none;
    border-color: #00d4ff;
    box-shadow: 0 0 0 2px rgba(0, 212, 255, 0.2);
  }
`;

const Select = styled.select`
  width: 100%;
  padding: 0.75rem;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.05);
  color: #ffffff;
  font-size: 1rem;

  &:focus {
    outline: none;
    border-color: #00d4ff;
    box-shadow: 0 0 0 2px rgba(0, 212, 255, 0.2);
  }

  option {
    background: #1a1a2e;
    color: #ffffff;
  }
`;

const Checkbox = styled.div`
  display: flex;
  align-items: center;
  gap: 0.5rem;

  input[type="checkbox"] {
    width: 1.2rem;
    height: 1.2rem;
    accent-color: #00d4ff;
  }

  label {
    margin-bottom: 0;
    cursor: pointer;
  }
`;

const Button = styled.button<{ variant?: 'primary' | 'danger' | 'success' }>`
  padding: 0.75rem 2rem;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;

  ${props => props.variant === 'primary' && `
    background: linear-gradient(45deg, #00d4ff, #0099cc);
    color: white;

    &:hover {
      background: linear-gradient(45deg, #0099cc, #007399);
      transform: translateY(-2px);
    }
  `}

  ${props => props.variant === 'danger' && `
    background: linear-gradient(45deg, #ff4444, #cc0000);
    color: white;

    &:hover {
      background: linear-gradient(45deg, #cc0000, #aa0000);
      transform: translateY(-2px);
    }
  `}

  ${props => props.variant === 'success' && `
    background: linear-gradient(45deg, #00ff88, #00cc66);
    color: white;

    &:hover {
      background: linear-gradient(45deg, #00cc66, #009944);
      transform: translateY(-2px);
    }
  `}

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
    transform: none;
  }
`;

const ButtonGroup = styled.div`
  display: flex;
  gap: 1rem;
  justify-content: center;
  margin-top: 2rem;
`;

const ResultsSection = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
  margin-top: 2rem;

  @media (max-width: 768px) {
    grid-template-columns: 1fr;
  }
`;

const ResultCard = styled.div`
  background: rgba(255, 255, 255, 0.05);
  border-radius: 16px;
  padding: 1.5rem;
  border: 1px solid rgba(255, 255, 255, 0.1);
`;

const ResultTitle = styled.h3`
  color: #00d4ff;
  margin-bottom: 1rem;
  font-size: 1.2rem;
`;

const BitsDisplay = styled.div`
  background: rgba(0, 0, 0, 0.3);
  border-radius: 8px;
  padding: 1rem;
  font-family: 'Courier New', monospace;
  font-size: 0.9rem;
  max-height: 200px;
  overflow-y: auto;
`;

const StatsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-top: 1rem;
`;

const StatItem = styled.div`
  background: rgba(255, 255, 255, 0.05);
  padding: 1rem;
  border-radius: 8px;
  text-align: center;
`;

const StatLabel = styled.div`
  color: #cccccc;
  font-size: 0.9rem;
  margin-bottom: 0.5rem;
`;

const StatValue = styled.div<{ status?: 'success' | 'warning' | 'error' }>`
  font-size: 1.5rem;
  font-weight: bold;

  ${props => props.status === 'success' && 'color: #00ff88;'}
  ${props => props.status === 'warning' && 'color: #ffaa00;'}
  ${props => props.status === 'error' && 'color: #ff4444;'}
`;

const QKDSimulator: React.FC = () => {
  const { token } = useAuth();
  const [parameters, setParameters] = useState<QKDParameters>({
    key_length: 50,
    noise_level: 5.0,
    detector_efficiency: 95.0,
    algorithm: 'bb84',
    eavesdropper_present: false,
  });

  const [result, setResult] = useState<QKDResult | null>(null);
  const [isRunning, setIsRunning] = useState(false);
  const [progress, setProgress] = useState(0);

  const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

  const runSimulation = async () => {
    if (!token) {
      toast.error('Please login to run simulations');
      return;
    }

    setIsRunning(true);
    setProgress(0);
    setResult(null);

    try {
      const response = await fetch(`${API_URL}/qkd/run`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(parameters),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Simulation failed');
      }

      const data = await response.json();
      setResult(data);
      toast.success('QKD simulation completed successfully!');

    } catch (error) {
      console.error('Simulation error:', error);
      toast.error(error instanceof Error ? error.message : 'Simulation failed');
    } finally {
      setIsRunning(false);
      setProgress(100);
    }
  };

  const resetSimulation = () => {
    setResult(null);
    setProgress(0);
    toast.info('Simulation reset');
  };

  return (
    <SimulatorContainer>
      <Title>Quantum Data Pipeline & Security Analytics Engine</Title>

      <ControlsSection>
        <ControlGroup>
          <Label htmlFor="key_length">Key Length</Label>
          <Input
            id="key_length"
            type="number"
            min="10"
            max="500"
            value={parameters.key_length}
            onChange={(e) => setParameters({...parameters, key_length: parseInt(e.target.value)})}
            disabled={isRunning}
          />
        </ControlGroup>

        <ControlGroup>
          <Label htmlFor="noise_level">Noise Level (%)</Label>
          <Input
            id="noise_level"
            type="number"
            min="0"
            max="30"
            step="0.1"
            value={parameters.noise_level}
            onChange={(e) => setParameters({...parameters, noise_level: parseFloat(e.target.value)})}
            disabled={isRunning}
          />
        </ControlGroup>

        <ControlGroup>
          <Label htmlFor="detector_efficiency">Detector Efficiency (%)</Label>
          <Input
            id="detector_efficiency"
            type="number"
            min="70"
            max="100"
            step="0.1"
            value={parameters.detector_efficiency}
            onChange={(e) => setParameters({...parameters, detector_efficiency: parseFloat(e.target.value)})}
            disabled={isRunning}
          />
        </ControlGroup>

        <ControlGroup>
          <Label htmlFor="algorithm">Algorithm</Label>
          <Select
            id="algorithm"
            value={parameters.algorithm}
            onChange={(e) => setParameters({ ...parameters, algorithm: e.target.value as 'bb84' | 'e91' | 'b92' })}
            disabled={isRunning}
          >
            <option value="bb84">BB84</option>
            <option value="e91">E91</option>
            <option value="b92">B92</option>
          </Select>
        </ControlGroup>

        <Checkbox>
          <input
            type="checkbox"
            id="eavesdropper"
            checked={parameters.eavesdropper_present}
            onChange={(e) => setParameters({...parameters, eavesdropper_present: e.target.checked})}
            disabled={isRunning}
          />
          <Label htmlFor="eavesdropper">Include Eavesdropper (Eve)</Label>
        </Checkbox>

        <ButtonGroup>
          <Button
            variant="primary"
            onClick={runSimulation}
            disabled={isRunning}
          >
            {isRunning ? '🔄 Running Simulation...' : '🚀 Run QKD Simulation'}
          </Button>

          <Button
            variant="danger"
            onClick={resetSimulation}
            disabled={isRunning}
          >
            🔄 Reset
          </Button>
        </ButtonGroup>

        {isRunning && (
          <div style={{ marginTop: '1rem', textAlign: 'center' }}>
            <div>Progress: {progress}%</div>
            <div style={{ background: '#333', height: '4px', borderRadius: '2px', marginTop: '0.5rem' }}>
              <div
                style={{
                  width: `${progress}%`,
                  height: '100%',
                  background: 'linear-gradient(45deg, #00d4ff, #ff00f7)',
                  borderRadius: '2px',
                  transition: 'width 0.3s ease'
                }}
              />
            </div>
          </div>
        )}
      </ControlsSection>

      {result && (
        <ResultsSection>
          <ResultCard>
            <ResultTitle>📊 Simulation Results</ResultTitle>
            <StatsGrid>
              <StatItem>
                <StatLabel>Final Key Length</StatLabel>
                <StatValue status="success">{result.stats.final_key_length}</StatValue>
              </StatItem>

              <StatItem>
                <StatLabel>Quantum Error Rate</StatLabel>
                <StatValue status={result.error_rate <= 11 ? 'success' : 'error'}>
                  {result.error_rate.toFixed(2)}%
                </StatValue>
              </StatItem>

              <StatItem>
                <StatLabel>Security Status</StatLabel>
                <StatValue status={result.security_status === 'secure' ? 'success' : 'error'}>
                  {result.security_status.toUpperCase()}
                </StatValue>
              </StatItem>

              <StatItem>
                <StatLabel>Detection Rate</StatLabel>
                <StatValue>
                  {((result.stats.detected / result.stats.transmitted) * 100).toFixed(1)}%
                </StatValue>
              </StatItem>
            </StatsGrid>
          </ResultCard>

          <ResultCard>
            <ResultTitle>🔑 Final Shared Key</ResultTitle>
            <BitsDisplay>
              {result.final_key.map((bit, index) => (
                <span
                  key={index}
                  style={{
                    color: bit === 1 ? '#00ff88' : '#ff4444',
                    fontWeight: 'bold'
                  }}
                >
                  {bit}
                </span>
              ))}
            </BitsDisplay>
          </ResultCard>

          <ResultCard>
            <ResultTitle>📈 Protocol Steps</ResultTitle>
            <BitsDisplay>
              <div><strong>Alice's Bits:</strong> {result.alice_bits.join('')}</div>
              <div><strong>Alice's Bases:</strong> {result.alice_bases.join('')}</div>
              <div><strong>Bob's Bases:</strong> {result.bob_bases.join('')}</div>
              <div><strong>Bob's Measurements:</strong> {result.bob_measurements.map(m => m ?? '∅').join('')}</div>
              <div><strong>Sifted Key (Alice):</strong> {result.sifted_alice.join('')}</div>
              <div><strong>Sifted Key (Bob):</strong> {result.sifted_bob.join('')}</div>
            </BitsDisplay>
          </ResultCard>

          <ResultCard>
            <ResultTitle>📊 Statistics Chart</ResultTitle>
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={[
                { name: 'Transmitted', value: result.stats.transmitted },
                { name: 'Detected', value: result.stats.detected },
                { name: 'Final Key', value: result.stats.final_key_length }
              ]}>
                <CartesianGrid strokeDasharray="3 3" stroke="#333" />
                <XAxis dataKey="name" stroke="#ccc" />
                <YAxis stroke="#ccc" />
                <Tooltip
                  contentStyle={{
                    background: 'rgba(0,0,0,0.8)',
                    border: '1px solid #00d4ff',
                    borderRadius: '8px'
                  }}
                />
                <Bar dataKey="value" fill="#00d4ff" />
              </BarChart>
            </ResponsiveContainer>
          </ResultCard>
        </ResultsSection>
      )}

      <ChatToggle />
    </SimulatorContainer>
  );
};

export default QKDSimulator;
