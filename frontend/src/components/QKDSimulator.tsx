import React, { useEffect, useRef, useState } from 'react';
import styled from 'styled-components';
import { toast } from 'react-toastify';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { useAuth } from '../context/AuthContext';
import { fetchApi, getWebSocketCandidates } from '../utils/api';

interface QKDParameters {
  key_length: number;
  noise_level: number;
  detector_efficiency: number;
  eavesdropper_present: boolean;
}

type SocketState = 'connecting' | 'connected' | 'reconnecting' | 'disconnected';

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
    qber?: number;
    key_rate?: number;
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
  display: flex;
  flex-direction: column;
  gap: 2rem;
  margin-top: 2rem;
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
  font-size: 0.7rem;
  line-height: 1.1;
  word-break: break-all;
  overflow-wrap: break-word;
  white-space: pre-wrap;
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

const stepText: Record<string, string> = {
  bit_generation: 'Generating bits and bases...',
  transmission: 'Transmitting and measuring photons...',
  sifting: 'Sifting key and estimating QBER...',
  final_key: 'Final key generation...',
  completed: 'QKD simulation completed successfully!',
};

const ConnectionBadge = styled.div<{ state: SocketState }>`
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  margin: 0 auto 1rem auto;
  padding: 0.35rem 0.75rem;
  border-radius: 999px;
  font-size: 0.85rem;
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: ${({ state }) =>
    state === 'connected' ? '#00ff88' : state === 'reconnecting' ? '#ffaa00' : '#ff7777'};
  background: rgba(0, 0, 0, 0.25);
`;
const QKDSimulator: React.FC = () => {
  const { token } = useAuth();
  const [parameters, setParameters] = useState<QKDParameters>({
    key_length: 50,
    noise_level: 5.0,
    detector_efficiency: 95.0,
    eavesdropper_present: false,
  });

  const [result, setResult] = useState<QKDResult | null>(null);
  const [isRunning, setIsRunning] = useState(false);
  const [progress, setProgress] = useState(0);
  const [currentStep, setCurrentStep] = useState<string>('');
  const [socketState, setSocketState] = useState<SocketState>('disconnected');

  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimerRef = useRef<number | null>(null);
  const reconnectAttemptRef = useRef(0);
  const shouldReconnectRef = useRef(true);
  const activeSessionRef = useRef<string | null>(null);

  const cleanupReconnectTimer = () => {
    if (reconnectTimerRef.current !== null) {
      window.clearTimeout(reconnectTimerRef.current);
      reconnectTimerRef.current = null;
    }
  };

  const sendSubscription = () => {
    if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) {
      return;
    }
    const sessionId = activeSessionRef.current;
    if (!sessionId) {
      return;
    }
    wsRef.current.send(JSON.stringify({ type: 'subscribe', session_id: sessionId }));
  };

  const connectSocket = (manual = false) => {
    setSocketState(reconnectAttemptRef.current > 0 ? 'reconnecting' : 'connecting');
    if (wsRef.current && (wsRef.current.readyState === WebSocket.OPEN || wsRef.current.readyState === WebSocket.CONNECTING)) {
      return;
    }

    const urls = getWebSocketCandidates('/ws/qkd');
    const primaryUrl = urls[reconnectAttemptRef.current % urls.length];
    const ws = new WebSocket(primaryUrl);
    wsRef.current = ws;

    ws.onopen = () => {
      setSocketState('connected');
      reconnectAttemptRef.current = 0;
      sendSubscription();
      if (!manual) {
        return;
      }
      toast.info('Live QKD channel connected');
    };

    ws.onmessage = (event) => {
      try {
        const payload = JSON.parse(event.data);
        const targetSession = activeSessionRef.current;

        if (payload.type === 'qkd_progress' && payload.session_id === targetSession) {
          setProgress(payload.progress ?? 0);
          setCurrentStep(stepText[payload.step] || payload.details?.message || 'Running simulation...');
        }

        if (payload.type === 'qkd_result' && payload.session_id === targetSession) {
          setResult(payload.result);
          setProgress(100);
          setCurrentStep(stepText.completed);
          setIsRunning(false);
        }
      } catch {
        // Ignore malformed websocket payloads.
      }
    };

    ws.onclose = () => {
      setSocketState(shouldReconnectRef.current ? 'reconnecting' : 'disconnected');
      wsRef.current = null;
      if (!shouldReconnectRef.current) {
        return;
      }
      const attempts = reconnectAttemptRef.current + 1;
      reconnectAttemptRef.current = attempts;
      const delay = Math.min(1000 * attempts, 5000);
      cleanupReconnectTimer();
      reconnectTimerRef.current = window.setTimeout(() => connectSocket(false), delay);
    };

    ws.onerror = () => {
      setSocketState('reconnecting');
      ws.close();
    };
  };

  useEffect(() => {
    connectSocket(false);
    return () => {
      shouldReconnectRef.current = false;
      cleanupReconnectTimer();
      wsRef.current?.close();
      wsRef.current = null;
    };
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  const createClientSessionId = () => {
    const rand = Math.random().toString(36).slice(2, 8);
    return `sess_${Date.now()}_${rand}`;
  };

  const clamp = (value: number, min: number, max: number) => Math.min(max, Math.max(min, value));

  const sanitizeParameters = (input: QKDParameters): QKDParameters => ({
    key_length: clamp(Number.isFinite(input.key_length) ? Math.round(input.key_length) : 50, 10, 500),
    noise_level: clamp(Number.isFinite(input.noise_level) ? input.noise_level : 5.0, 0, 30),
    detector_efficiency: clamp(Number.isFinite(input.detector_efficiency) ? input.detector_efficiency : 95.0, 70, 100),
    eavesdropper_present: !!input.eavesdropper_present,
  });
  const runSimulation = async () => {
    if (!token) {
      toast.error('Please login to run simulations');
      return;
    }

    const sessionId = createClientSessionId();
    activeSessionRef.current = sessionId;
    const safeParameters = sanitizeParameters(parameters);
    setParameters(safeParameters);

    setIsRunning(true);
    setProgress(0);
    setResult(null);
    setCurrentStep('Preparing real-time simulation channel...');

    try {
      connectSocket(true);
      sendSubscription();

      const response = await fetchApi('/qkd/run', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({ ...safeParameters, session_id: sessionId }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Simulation failed');
      }

      const data = await response.json();
      if (!result) {
        setResult(data);
        setProgress(100);
        setCurrentStep(stepText.completed);
      }
      toast.success('QKD simulation completed successfully!');
    } catch (error) {
      console.error('Simulation error:', error);
      setIsRunning(false);
      toast.error(error instanceof Error ? error.message : 'Simulation failed');
    }
  };

  
  const socketStateLabel =
    socketState === 'connected'
      ? 'WS Connected'
      : socketState === 'reconnecting'
      ? 'WS Reconnecting'
      : socketState === 'connecting'
      ? 'WS Connecting'
      : 'WS Disconnected';
  const resetSimulation = () => {
    const sessionId = activeSessionRef.current;
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN && sessionId) {
      wsRef.current.send(JSON.stringify({ type: 'unsubscribe', session_id: sessionId }));
    }
    activeSessionRef.current = null;
    setResult(null);
    setProgress(0);
    setCurrentStep('');
    setIsRunning(false);
    toast.info('Simulation reset');
  };

  return (
    <SimulatorContainer>
      <Title>BB84 Quantum Key Distribution Simulator</Title>
      <div style={{ textAlign: 'center' }}>
        <ConnectionBadge state={socketState}>{socketStateLabel}</ConnectionBadge>
      </div>

      <ControlsSection>
        <ControlGroup>
          <Label htmlFor="key_length">Key Length</Label>
          <Input
            id="key_length"
            type="number"
            min="10"
            max="500"
            value={parameters.key_length}
            onChange={(e) => {
              const value = Number(e.target.value);
              setParameters({...parameters, key_length: Number.isFinite(value) ? value : 50});
            }}
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
            onChange={(e) => {
              const value = Number(e.target.value);
              setParameters({...parameters, noise_level: Number.isFinite(value) ? value : 5.0});
            }}
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
            onChange={(e) => {
              const value = Number(e.target.value);
              setParameters({...parameters, detector_efficiency: Number.isFinite(value) ? value : 95.0});
            }}
            disabled={isRunning}
          />
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
            {isRunning ? 'Running Simulation...' : 'Run QKD Simulation'}
          </Button>

          <Button
            variant="danger"
            onClick={resetSimulation}
            disabled={isRunning}
          >
            Reset
          </Button>
        </ButtonGroup>

        {isRunning && (
          <div style={{ marginTop: '1rem', textAlign: 'center' }}>
            <div style={{ marginBottom: '0.5rem', color: '#00d4ff', fontWeight: 'bold' }}>
              {currentStep}
            </div>
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
            <ResultTitle>Simulation Results</ResultTitle>
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
            <ResultTitle>Final Shared Key</ResultTitle>
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
            <ResultTitle>Protocol Steps</ResultTitle>
            <BitsDisplay>
              <div><strong>Alice's Bits:</strong> {result.alice_bits.join('')}</div>
              <div><strong>Alice's Bases:</strong> {result.alice_bases.join('')}</div>
              <div><strong>Bob's Bases:</strong> {result.bob_bases.join('')}</div>
              <div><strong>Bob's Measurements:</strong> {result.bob_measurements.map(m => m ?? 'Ø').join('')}</div>
              <div><strong>Sifted Key (Alice):</strong> {result.sifted_alice.join('')}</div>
              <div><strong>Sifted Key (Bob):</strong> {result.sifted_bob.join('')}</div>
            </BitsDisplay>
          </ResultCard>

          <ResultCard>
            <ResultTitle>Statistics Chart</ResultTitle>
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
    </SimulatorContainer>
  );
};

export default QKDSimulator;





